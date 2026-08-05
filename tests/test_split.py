import pandas as pd
import sys
sys.path.append(".")
from scripts.split_valid_invalid import split

def test_split_separates_valid_and_invalid(tmp_path):
    csv_content = """device_id,timestamp,sensor_type,reading_value,unit,location
SENSOR_001,2026-08-01T00:00:00,temperature,22.5,C,warehouse_a
,2026-08-01T00:01:00,temperature,23.0,C,warehouse_a
SENSOR_003,2026-08-01T00:02:00,temperature,ERROR,C,warehouse_a
SENSOR_004,2026-08-01T00:03:00,temperature,999.0,C,warehouse_a
SENSOR_005,2026-08-01T00:04:00,humidity,50.0,%,warehouse_b
"""
    csv_path = tmp_path / "test_data.csv"
    csv_path.write_text(csv_content)

    valid, invalid = split(str(csv_path))

    assert len(valid) == 2  # SENSOR_001 and SENSOR_005
    assert len(invalid) == 3
    reasons = set(invalid["_reason"])
    assert "missing_device_id" in reasons
    assert "invalid_reading_value_dtype" in reasons
    assert "out_of_range" in reasons