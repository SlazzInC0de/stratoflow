import pandas as pd
import pandera.pandas as pa
import sys
sys.path.append(".")
from schemas.sensor_schema import raw_schema

def validate(csv_path):
    df = pd.read_csv(csv_path)
    try:
        validated = raw_schema.validate(df, lazy=True)
        print(f"Validation passed: {len(validated)} rows OK")
        return validated
    except Exception as e:
        print("SCHEMA VALIDATION FAILED:")
        print(e)
        return None

if __name__ == "__main__":
    validate("data/raw_sensor_data.csv")