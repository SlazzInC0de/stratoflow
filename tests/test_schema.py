import pandas as pd
import pytest
import sys
sys.path.append(".")
from schemas.sensor_schema import raw_schema, is_valid_range

def make_row(**overrides):
    base = {
        "device_id": "SENSOR_001",
        "timestamp": "2026-08-01T00:00:00",
        "sensor_type": "temperature",
        "reading_value": 22.5,
        "unit": "C",
        "location": "warehouse_a",
    }
    base.update(overrides)
    return base

def test_valid_row_passes_schema():
    df = pd.DataFrame([make_row()])
    validated = raw_schema.validate(df)
    assert len(validated) == 1

def test_null_device_id_fails_schema():
    df = pd.DataFrame([make_row(device_id=None)])
    with pytest.raises(Exception):
        raw_schema.validate(df)

def test_invalid_sensor_type_fails_schema():
    df = pd.DataFrame([make_row(sensor_type="not_a_real_sensor")])
    with pytest.raises(Exception):
        raw_schema.validate(df)

def test_is_valid_range_inside_bounds():
    assert is_valid_range("temperature", 20.0) is True

def test_is_valid_range_outside_bounds():
    assert is_valid_range("temperature", 500.0) is False

def test_is_valid_range_unknown_sensor_type():
    assert is_valid_range("not_real", 20.0) is False