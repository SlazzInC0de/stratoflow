import logging
import os
import sys
import tempfile
from io import BytesIO

import azure.functions as func
from azure.storage.blob import BlobServiceClient

sys.path.append(".")
from scripts.split_valid_invalid import split  # noqa: E402

OUTPUT_CONTAINER = os.environ.get("OUTPUT_CONTAINER", "processed-output")

app = func.FunctionApp()


def _upload(service: BlobServiceClient, blob_name: str, data: bytes) -> None:
    client = service.get_blob_client(container=OUTPUT_CONTAINER, blob=blob_name)
    client.upload_blob(data, overwrite=True)


@app.blob_trigger(arg_name="myblob", path="raw-uploads/{name}", connection="AzureWebJobsStorage")
def stratoflow_pipeline(myblob: func.InputStream) -> None:
    """Validate an uploaded CSV, quarantine bad rows and publish clean rows as Parquet."""
    file_name = os.path.basename(myblob.name)
    stem, _ = os.path.splitext(file_name)
    logging.info("Processing blob: %s", myblob.name)

    try:
        # 1. Persist the upload so the Phase 1 split logic can read it unchanged
        with tempfile.TemporaryDirectory() as tmp:
            temp_path = os.path.join(tmp, file_name)
            with open(temp_path, "wb") as fh:
                fh.write(myblob.read())

            # 2. Validate and split into clean / quarantined rows
            valid, invalid = split(temp_path)

        logging.info("Valid: %d, Invalid: %d", len(valid), len(invalid))
        service = BlobServiceClient.from_connection_string(os.environ["AzureWebJobsStorage"])

        # 3. Quarantine bad rows with their reason codes
        if len(invalid) > 0:
            _upload(service, f"quarantine/{stem}.csv", invalid.to_csv(index=False).encode("utf-8"))
            logging.warning("Quarantined %d invalid rows", len(invalid))

        # 4. Publish valid rows as Parquet for Synapse
        parquet_buffer = BytesIO()
        valid.to_parquet(parquet_buffer, engine="pyarrow", index=False)
        _upload(service, f"{stem}.parquet", parquet_buffer.getvalue())

        logging.info("Processed %d rows -> %s/%s.parquet", len(valid), OUTPUT_CONTAINER, stem)

    except Exception:
        logging.exception("Pipeline failed for %s", myblob.name)
        raise
