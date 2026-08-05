import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

SENSOR_TYPES = {
    "temperature": {"unit": "C", "range": (-10, 45)},
    "humidity": {"unit": "%", "range": (0, 100)},
    "pressure": {"unit": "hPa", "range": (950, 1050)},
    "battery": {"unit": "%batt", "range": (0, 100)},
}
LOCATIONS = ["warehouse_a", "warehouse_b", "warehouse_c"]

def generate_row(i, base_time):
    sensor_type = random.choice(list(SENSOR_TYPES.keys()))
    meta = SENSOR_TYPES[sensor_type]
    device_id = f"SENSOR_{random.randint(1, 50):03d}"
    timestamp = base_time + timedelta(minutes=i)
    value = round(random.uniform(*meta["range"]), 2)

    return {
        "device_id": device_id,
        "timestamp": timestamp.isoformat(),
        "sensor_type": sensor_type,
        "reading_value": value,
        "unit": meta["unit"],
        "location": random.choice(LOCATIONS),
    }

def inject_messiness(rows):
    n = len(rows)
    # missing device_id
    for i in random.sample(range(n), 15):
        rows[i]["device_id"] = None
    # null readings
    for i in random.sample(range(n), 20):
        rows[i]["reading_value"] = None
    # out-of-range glitches (e.g. temp sensor reporting 500)
    for i in random.sample(range(n), 10):
        rows[i]["reading_value"] = round(random.uniform(500, 999), 2)
    # wrong dtype — sensor error strings instead of numbers
    for i in random.sample(range(n), 8):
        rows[i]["reading_value"] = "ERROR"
    # duplicate timestamps (sensor retry glitch)
    for i in random.sample(range(1, n), 12):
        rows[i]["timestamp"] = rows[i - 1]["timestamp"]
    return rows

if __name__ == "__main__":
    base_time = datetime(2026, 8, 1, 0, 0, 0)
    rows = [generate_row(i, base_time) for i in range(500)]
    rows = inject_messiness(rows)
    df = pd.DataFrame(rows)
    df.to_csv("data/raw_sensor_data.csv", index=False)
    print(f"Generated {len(df)} rows -> data/raw_sensor_data.csv")