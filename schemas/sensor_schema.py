import pandera.pandas as pa
from pandera import Column, Check, DataFrameSchema

VALID_RANGES = {
    "temperature": (-10, 45),
    "humidity": (0, 100),
    "pressure": (950, 1050),
    "battery": (0, 100),
}
VALID_SENSOR_TYPES = list(VALID_RANGES.keys())

raw_schema = DataFrameSchema(
    {
        "device_id": Column(str, nullable=False),
        "timestamp": Column(str, nullable=False),
        "sensor_type": Column(str, Check.isin(VALID_SENSOR_TYPES), nullable=False),
        "reading_value": Column(float, nullable=False),
        "unit": Column(str, nullable=False),
        "location": Column(str, nullable=False),
    },
    strict=True,
)

def is_valid_range(sensor_type, value):
    lo, hi = VALID_RANGES.get(sensor_type, (None, None))
    if lo is None:
        return False
    return lo <= value <= hi