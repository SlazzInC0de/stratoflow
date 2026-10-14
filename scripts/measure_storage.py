"""Reproducible storage comparison for the validated output.

Writes every format into a temp dir, measures bytes on disk and prints a
Markdown table. Usage:

    python scripts/measure_storage.py [path/to/valid_rows.csv]
"""
import gzip
import os
import sys
import tempfile

import pandas as pd
import pyarrow as pa


def size(path: str) -> int:
    return os.path.getsize(path)


def main(csv_path: str = "data/valid_rows.csv") -> None:
    df = pd.read_csv(csv_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    with tempfile.TemporaryDirectory() as tmp:
        variants = {}

        lf = os.path.join(tmp, "lf.csv")
        df.to_csv(lf, index=False, lineterminator="\n")
        variants["CSV (LF line endings)"] = size(lf)

        crlf = os.path.join(tmp, "crlf.csv")
        df.to_csv(crlf, index=False, lineterminator="\r\n")
        variants["CSV (CRLF, as saved on Windows)"] = size(crlf)

        gz = lf + ".gz"
        with open(lf, "rb") as src, gzip.open(gz, "wb", compresslevel=9) as dst:
            dst.write(src.read())
        variants["CSV + gzip -9"] = size(gz)

        for codec in ("snappy", "gzip", "zstd", "none"):
            out = os.path.join(tmp, f"{codec}.parquet")
            df.to_parquet(out, engine="pyarrow", index=False, compression=None if codec == "none" else codec)
            label = f"Parquet ({codec}{', pipeline default' if codec == 'snappy' else ''})"
            variants[label] = size(out)

    base = variants["CSV (LF line endings)"]
    print(f"Rows: {len(df)} · columns: {len(df.columns)} · pandas {pd.__version__} · pyarrow {pa.__version__}\n")
    print("| Format | Bytes | vs CSV (LF) |")
    print("|---|---:|---:|")
    for name, value in variants.items():
        if value == base:
            change = "baseline"
        elif value < base:
            change = f"{100 * (1 - value / base):.1f}% smaller"
        else:
            change = f"{100 * (value / base - 1):.1f}% larger"
        print(f"| {name} | {value:,} | {change} |")


if __name__ == "__main__":
    main(*sys.argv[1:])
