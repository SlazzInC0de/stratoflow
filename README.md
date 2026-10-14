<div align="center">

# ☁️ StratoFlow

### Serverless data refinery on Azure

**Upload a messy CSV. Get validated, quarantined, query-ready Parquet, automatically.**

[![CI](https://github.com/SlazzInC0de/stratoflow/actions/workflows/deploy.yml/badge.svg)](https://github.com/SlazzInC0de/stratoflow/actions/workflows/deploy.yml)
![Python](https://img.shields.io/badge/Python-3.13-0f172a?logo=python&logoColor=3776AB)
![Azure Functions](https://img.shields.io/badge/Azure_Functions-0f172a?logo=azurefunctions&logoColor=0062AD)
![Terraform](https://img.shields.io/badge/Terraform-0f172a?logo=terraform&logoColor=844FBA)
![Synapse](https://img.shields.io/badge/Synapse_Serverless_SQL-0f172a?logo=microsoftazure&logoColor=0078D4)
![Coverage](https://img.shields.io/badge/coverage-96%25-22c55e)
![License](https://img.shields.io/badge/License-MIT-22d3ee)

</div>

---

## ✨ Highlights

| | |
|---|---|
| ⚡ **Event-driven** | A blob upload triggers the pipeline. No servers, no schedulers. |
| 🛡️ **Row-level validation** | Sensor-aware rules quarantine bad rows with a reason code instead of failing the whole batch. |
| 📦 **61% smaller output** | Clean data lands as columnar Parquet (28.0 KB CSV → 10.9 KB), measured by a script in the repo. |
| 🔎 **Instantly queryable** | Synapse Serverless SQL reads the Parquet in place via `OPENROWSET`. |
| 🏗️ **100% IaC** | Storage, containers, Synapse, firewall and RBAC are all in Terraform. |
| ✅ **Tested + CI** | 11 pytest cases (96% coverage) including the Function with storage mocked, plus flake8 and `terraform validate` on every push. |

## 🏛️ Architecture

```mermaid
flowchart LR
    U([📄 CSV upload]) --> R[(Blob Storage<br/>raw-uploads)]
    R -- blob trigger --> F{{Azure Function<br/>Python}}
    F --> V[Pandera-style<br/>row validation]
    V -- invalid rows + reason --> Q[(processed-output/<br/>quarantine/*.csv)]
    V -- valid rows --> P[(processed-output/<br/>*.parquet)]
    P --> S[[Synapse Serverless<br/>SQL Pool]]
    S --> A([📊 SQL analytics])

    subgraph IaC [Terraform managed]
        R
        Q
        P
        S
    end
```

## 🛡️ Validation and quarantine

Every row is checked independently, and failures are routed to quarantine with the reason attached, mirroring a production dead-letter pattern. Ranges are **sensor-type aware**: temperature, humidity, pressure and battery each have their own bounds.

Result on the bundled 500-row dataset with deliberately injected noise:

| Outcome | Rows |
|---|---:|
| ✅ Valid | **450** |
| Missing `reading_value` | 18 |
| Missing `device_id` | 15 |
| Out-of-range reading (sensor glitch) | 9 |
| Invalid dtype (`"ERROR"` string) | 8 |

## 📦 Storage: measured, not estimated

`python scripts/measure_storage.py` rewrites the 450 validated rows in every format and reports bytes on disk (pandas 3.0, pyarrow 26):

| Format | Bytes | vs CSV |
|---|---:|---:|
| CSV (LF line endings) | 28,043 | baseline |
| CSV (CRLF, as saved on Windows) | 28,494 | 1.6% larger |
| **Parquet, snappy (pipeline default)** | **10,910** | **61.1% smaller** |
| Parquet, zstd | 8,978 | 68.0% smaller |
| Parquet, gzip | 9,353 | 66.6% smaller |
| Parquet, uncompressed | 13,529 | 51.8% smaller |
| CSV + gzip -9 | 4,505 | 83.9% smaller |

**Reading the numbers honestly:** on a file this small, gzip on the raw CSV is smaller than any Parquet variant, because Parquet carries per-file schema and column metadata. Size is not why the pipeline uses Parquet. It is chosen because it is **typed and columnar**: Synapse reads only the columns a query needs, skips row groups using column statistics, and queries the file in place. A gzipped CSV has to be fully decompressed and parsed on every read. The gap in Parquet's favour grows with row count. CI re-runs this measurement on every push.

## 🔎 Analytics layer

```sql
SELECT sensor_type, AVG(reading_value) AS avg_reading, COUNT(*) AS readings
FROM OPENROWSET(
    BULK 'https://stratoflowdata.blob.core.windows.net/processed-output/valid_rows.parquet',
    FORMAT = 'PARQUET'
) AS rows
GROUP BY sensor_type;
```

More queries live in [`sql/analytics_queries.sql`](sql/analytics_queries.sql).

## 🧰 Tech stack

| Layer | Tool |
|---|---|
| Storage | Azure Blob Storage |
| Compute | Azure Functions (Python, blob trigger) |
| Validation | pandas + Pandera schema |
| Format | Parquet (PyArrow) |
| Analytics | Azure Synapse Serverless SQL |
| IaC | Terraform (`azurerm`) |
| CI | GitHub Actions |
| Tests | Pytest |

## 🚀 Run it locally

```bash
git clone https://github.com/SlazzInC0de/stratoflow.git
cd stratoflow
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt pytest pytest-cov

# Phase 1 pipeline on the sample data
python scripts/generate_sample_data.py     # optional: regenerate raw data
python scripts/split_valid_invalid.py      # -> data/valid_rows.csv + data/quarantined_rows.csv
python scripts/convert_to_parquet.py       # -> data/valid_rows.parquet (+ size report)
python scripts/measure_storage.py          # CSV vs Parquet vs gzip comparison

pytest -v --cov=function_app --cov=schemas --cov=scripts.split_valid_invalid
```

**Deploy the infrastructure**

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

The Function reads its storage connection from `AzureWebJobsStorage` and writes to the `processed-output` container (override with `OUTPUT_CONTAINER`).

## 🧪 Tests

11 pytest cases, **96% line coverage** on the pipeline code (`function_app.py`, `schemas/`, `scripts/split_valid_invalid.py`; the 3 uncovered lines are the script's `__main__` block).

| Suite | Covers |
|---|---|
| `test_schema.py` | Per-sensor range checks, nulls, invalid categories |
| `test_split.py` | Row routing and reason codes for each failure type |
| `test_function_app.py` | The real blob-trigger handler with Azure Storage mocked: Parquet + quarantine outputs, nested blob paths, clean batches with no quarantine file, and storage outages surfacing as errors |

## 🧭 Design decisions

| Decision | Why | Trade-off / alternative |
|---|---|---|
| **Quarantine bad rows** instead of failing the batch | One bad sensor reading should not block 449 good ones; every rejected row keeps its reason code | Bad rows need a follow-up process; a dead-letter queue with alerts is on the roadmap |
| **Validation rules per sensor type** | Temperature and pressure have very different valid ranges | New sensor types need a code change (no schema evolution yet) |
| **Re-raise on storage errors** | The Functions runtime retries failed blob triggers, so transient outages heal themselves | A persistently broken file retries until the poison-blob limit |
| **Overwrite outputs** (`overwrite=True`) | Re-processing the same upload is idempotent | Two different uploads with the same file name overwrite each other |
| **Parquet + Synapse Serverless** | Columnar, queryable in place, billed per TB scanned | Not a real-time store; queries take seconds, not milliseconds |
| **Terraform with imported resources** | Resources first created by CLI are now version-controlled and reproducible | `apply` stays manual because the institutional tenant blocks service principals |

## 🔁 CI/CD

GitHub Actions runs on every push and PR:

- **Test & Lint**: Pytest with coverage, the storage measurement and flake8, with results published to each run's summary
- **Terraform Validate & Format**: `fmt -check` and `validate` without cloud credentials

`terraform apply` is run manually. The institutional Azure tenant blocks service principal creation, which GitHub Actions normally needs to authenticate. In an unrestricted tenant this would move to OIDC federated credentials.

## 💸 Cost

Consumption-tier Functions (1M free executions/month), Blob Storage and pay-per-query Synapse keep **1,000 runs/month under $1**.

## 🗺️ Roadmap

- [ ] Partition Parquet by date and `sensor_type`
- [ ] Schema evolution for new sensor types
- [ ] Service Bus dead-letter queue with alerting
- [ ] Dashboard on top of the Synapse views
- [ ] OIDC-based `terraform apply` in CI

## 📁 Project structure

```text
stratoflow/
├── function_app.py        # Azure Function: blob trigger -> validate -> Parquet
├── schemas/               # Validation schema and sensor ranges
├── scripts/               # Data generation, split, Parquet conversion
├── tests/                 # Pytest suite
├── sql/                   # Synapse analytics queries
├── terraform/             # IaC: storage, Synapse, IAM
├── data/                  # Sample dataset and outputs
└── .github/workflows/     # CI pipeline
```

## 📄 License

MIT © [Suryansh Verma](https://github.com/SlazzInC0de)
