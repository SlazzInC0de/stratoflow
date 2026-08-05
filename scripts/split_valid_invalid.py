import pandas as pd
import numpy as np
import sys
sys.path.append(".")
from schemas.sensor_schema import VALID_SENSOR_TYPES, is_valid_range

def split(csv_path):
    df = pd.read_csv(csv_path)
    df["_reason"] = None

    # try coercing reading_value to float, flag failures
    coerced = pd.to_numeric(df["reading_value"], errors="coerce")
    dtype_fail = coerced.isna() & df["reading_value"].notna()
    df.loc[dtype_fail, "_reason"] = "invalid_reading_value_dtype"
    df["reading_value"] = coerced

    # flag nulls
    df.loc[df["device_id"].isna() & df["_reason"].isna(), "_reason"] = "missing_device_id"
    df.loc[df["reading_value"].isna() & df["_reason"].isna(), "_reason"] = "missing_reading_value"

    # flag invalid sensor_type
    bad_type = ~df["sensor_type"].isin(VALID_SENSOR_TYPES)
    df.loc[bad_type & df["_reason"].isna(), "_reason"] = "invalid_sensor_type"

    # flag out-of-range (only where reading_value exists and sensor_type is valid)
    checkable = df["reading_value"].notna() & ~bad_type & df["_reason"].isna()
    out_of_range = checkable & ~df.apply(
        lambda r: is_valid_range(r["sensor_type"], r["reading_value"]), axis=1
    )
    df.loc[out_of_range, "_reason"] = "out_of_range"

    valid = df[df["_reason"].isna()].drop(columns=["_reason"])
    invalid = df[df["_reason"].notna()]

    print(f"Valid rows: {len(valid)}")
    print(f"Invalid rows: {len(invalid)}")
    print(invalid["_reason"].value_counts())

    return valid, invalid

if __name__ == "__main__":
    valid, invalid = split("data/raw_sensor_data.csv")
    valid.to_csv("data/valid_rows.csv", index=False)
    invalid.to_csv("data/quarantined_rows.csv", index=False)