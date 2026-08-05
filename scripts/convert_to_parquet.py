import pandas as pd

def convert(csv_path, parquet_path):
    df = pd.read_csv(csv_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.to_parquet(parquet_path, engine="pyarrow", index=False)
    print(f"Converted {len(df)} rows -> {parquet_path}")

    # quick size comparison for your README's cost/efficiency section
    import os
    csv_size = os.path.getsize(csv_path)
    parquet_size = os.path.getsize(parquet_path)
    print(f"CSV size: {csv_size} bytes | Parquet size: {parquet_size} bytes")
    print(f"Compression: {100 * (1 - parquet_size/csv_size):.1f}% smaller")

if __name__ == "__main__":
    convert("data/valid_rows.csv", "data/valid_rows.parquet")