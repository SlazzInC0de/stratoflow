"""End-to-end tests for the blob-triggered Function with Azure Storage mocked."""
import io

import pandas as pd
import pytest

import function_app as fa

CSV = """device_id,timestamp,sensor_type,reading_value,unit,location
SENSOR_001,2026-08-01T00:00:00,temperature,22.5,C,warehouse_a
,2026-08-01T00:01:00,temperature,23.0,C,warehouse_a
SENSOR_003,2026-08-01T00:02:00,humidity,ERROR,%,warehouse_b
SENSOR_004,2026-08-01T00:03:00,pressure,2000.0,hPa,warehouse_b
SENSOR_005,2026-08-01T00:04:00,battery,88.0,%,warehouse_c
"""


class FakeBlob:
    def __init__(self, name, data):
        self.name = name
        self._data = data.encode() if isinstance(data, str) else data

    def read(self):
        return self._data


class FakeStorage:
    def __init__(self, fail=False):
        self.uploads = {}
        self.fail = fail

    def get_blob_client(self, container, blob):
        storage = self

        class Client:
            def upload_blob(self, data, overwrite):
                if storage.fail:
                    raise ConnectionError("storage unavailable")
                storage.uploads[f"{container}/{blob}"] = data

        return Client()


@pytest.fixture
def storage(monkeypatch):
    fake = FakeStorage()
    monkeypatch.setenv("AzureWebJobsStorage", "UseDevelopmentStorage=true")
    monkeypatch.setattr(fa.BlobServiceClient, "from_connection_string", staticmethod(lambda _cs: fake))
    return fake


# get_functions() may only be called once per FunctionApp, so resolve the handler at import.
HANDLER = next(iter(fa.app.get_functions())).get_user_function()


def run(blob):
    HANDLER(blob)


def test_valid_rows_land_as_parquet_and_bad_rows_in_quarantine(storage):
    run(FakeBlob("raw-uploads/batch_07.csv", CSV))

    parquet = pd.read_parquet(io.BytesIO(storage.uploads["processed-output/batch_07.parquet"]))
    assert list(parquet["device_id"]) == ["SENSOR_001", "SENSOR_005"]

    quarantine = pd.read_csv(io.BytesIO(storage.uploads["processed-output/quarantine/batch_07.csv"]))
    assert sorted(quarantine["_reason"]) == ["invalid_reading_value_dtype", "missing_device_id", "out_of_range"]


def test_nested_blob_paths_use_only_the_file_name(storage):
    run(FakeBlob("raw-uploads/2026/08/01/batch.csv", CSV))
    assert "processed-output/batch.parquet" in storage.uploads


def test_clean_batch_writes_no_quarantine_file(storage):
    clean = "\n".join(CSV.splitlines()[:2]) + "\n"
    run(FakeBlob("raw-uploads/clean.csv", clean))
    assert list(storage.uploads) == ["processed-output/clean.parquet"]


def test_storage_failure_is_raised_so_the_runtime_retries(storage):
    storage.fail = True
    with pytest.raises(ConnectionError):
        run(FakeBlob("raw-uploads/batch.csv", CSV))
