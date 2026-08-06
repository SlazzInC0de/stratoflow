\# StratoFlow — Serverless Data Refinery Pipeline



A resilient, event-driven ETL pipeline built on Azure: validates messy IoT sensor data, quarantines bad records, converts clean data to Parquet, and makes it instantly queryable via SQL — all serverless, all infrastructure-as-code.



> Upload a messy CSV. Get validated, catalogued, query-ready Parquet — automatically, for pennies.



\## Why this project



Most "serverless pipeline" tutorials stop at S3 → Lambda → output bucket. StratoFlow goes further: real data validation with per-field rules, a quarantine pattern for bad records (not just try/fail), an analytics layer that proves the output has actual value, and infrastructure managed entirely through Terraform — including resources adopted from manual setup into IaC, which is a common real-world scenario.



\## Architecture



Raw CSV Upload (Blob Storage)

↓

Azure Function (Blob Trigger)

↓

Pandera Schema Validation ──→ Invalid rows quarantined (reason logged)

↓

Valid rows → Pandas Transform

↓

Parquet Output (Blob Storage) ──→ 61.7% smaller than source CSV

↓

Synapse Serverless SQL Pool ──→ Queryable via standard SQL, no ETL into a database



\## Tech Stack



| Layer | Tool |

|---|---|

| Storage | Azure Blob Storage |

| Compute | Azure Functions (Python) |

| Validation | Pandera |

| Data format | Parquet (PyArrow) |

| Analytics | Synapse Serverless SQL Pool |

| IaC | Terraform (`azurerm` provider) |

| CI/CD | GitHub Actions |

| Testing | Pytest |



\## Data Validation \& Quarantine



Rather than failing an entire batch on bad data, StratoFlow validates row-by-row and routes failures to quarantine with a reason code — mirroring how a production dead-letter-queue pattern works.



On a 500-row test dataset with deliberately injected messiness:



| Result | Count |

|---|---|

| Valid rows | 450 |

| Missing `reading\_value` | 18 |

| Missing `device\_id` | 15 |

| Out-of-range reading (sensor glitch) | 9 |

| Invalid dtype (`"ERROR"` string) | 8 |



Validation rules are sensor-type-aware — a temperature sensor and a pressure sensor have different valid ranges, so the schema checks each row against the correct bounds for its `sensor\_type`, not a single blanket range.



\## Why Parquet



Converting the validated output from CSV to Parquet:



\- \*\*CSV\*\*: 28,494 bytes

\- \*\*Parquet\*\*: 10,910 bytes

\- \*\*61.7% smaller\*\* — columnar storage + compression, and it's directly queryable by Synapse without any load step



\## Analytics Layer



Processed Parquet output is queryable directly via Azure Synapse Serverless SQL Pool — no data warehouse, no separate ETL into a database.



```sql

SELECT sensor\_type, AVG(reading\_value) as avg\_reading, COUNT(\*) as count

FROM OPENROWSET(

&#x20;   BULK 'https://stratoflowdata.blob.core.windows.net/processed-output/valid\_rows.parquet',

&#x20;   FORMAT = 'PARQUET'

) AS rows

GROUP BY sensor\_type;

```



This proves the pipeline's output isn't just files sitting in storage — it's immediately analyzable, standard-SQL-accessible data.



\## Infrastructure as Code



All Azure infrastructure — resource group, storage account, containers, Synapse workspace, firewall rules, role assignments — is managed through Terraform (`terraform/`). Resources were provisioned via CLI during initial setup and then \*\*imported into Terraform state\*\*, so the entire environment is now reproducible and version-controlled, not a one-off manual setup.



```powershell

cd terraform

terraform init

terraform plan

terraform apply

```



\## Testing



7 Pytest tests cover schema validation and the quarantine split logic — including edge cases (null fields, invalid categories, out-of-range values, dtype coercion failures).



```powershell

pytest -v

```



\## CI/CD



GitHub Actions runs on every push/PR:

\- \*\*Test \& Lint\*\* — Pytest suite + flake8 on the data validation logic

\- \*\*Terraform Validate \& Format\*\* — confirms the Terraform configuration is syntactically valid and correctly formatted, without requiring cloud credentials



\*\*Note on deployment\*\*: `terraform plan`/`apply` are run manually rather than in CI. The Azure tenant used for this project (an institutional subscription) restricts service principal / app registration creation, which is normally required for GitHub Actions to authenticate with Azure. In an unrestricted environment, this would be automated via OIDC federated credentials or a stored service principal. This is a real, common constraint in enterprise and institutional cloud environments, not a limitation of the pipeline design.



\## Cost



Running on Azure's serverless consumption tier (Functions) and free-tier-eligible Blob Storage:



\- Azure Functions: pay-per-execution, first 1M executions/month free

\- Blob Storage: fractions of a cent per GB/month

\- Synapse Serverless SQL: pay-per-query (per TB scanned), not per-hour like a dedicated pool



Estimated cost for 1,000 pipeline runs/month (small CSV files): \*\*under $1/month\*\*.



\## What I'd do differently at scale



\- Partition Parquet output by date/sensor\_type for faster querying on large datasets

\- Add schema evolution handling (new sensor types, changed fields) instead of a fixed schema

\- Replace the current single-container quarantine log with a proper Service Bus dead-letter queue and alerting

\- Add a lightweight dashboard (Power BI or a simple web app) on top of the Synapse queries

\- Move from `use\_cli` local Terraform auth to OIDC federated credentials for CI/CD, if tenant restrictions were lifted



\## Project Structure



stratoflow/

├── schemas/ # Pandera validation schemas

├── scripts/ # Data generation, validation, split, Parquet conversion

├── tests/ # Pytest suite

├── sql/ # Synapse analytics queries

├── terraform/ # Infrastructure as code (iam, storage, synapse)

├── function\_app.py # Azure Functions pipeline (blob trigger)

├── .github/workflows/ # CI/CD pipeline

└── data/ # Sample dataset

