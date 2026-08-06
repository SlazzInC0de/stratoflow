This is already a fantastic README—it clearly explains the \*"why"\* behind your architectural choices, acknowledges real-world constraints (like institutional tenant restrictions), and proves the value of the pipeline.



To take it from a Notepad draft to a highly professional, standout GitHub repository, I have upgraded the formatting. I added \*\*dynamic tech badges\*\*, converted your text architecture into a \*\*Mermaid.js diagram\*\* (which GitHub renders automatically as a visual flowchart), added a \*\*Table of Contents\*\*, and polished the typography for better scannability.



Here is your improved `README.md`. You can copy and paste this directly into your repository.



\---



```markdown

\# StratoFlow — Serverless Data Refinery Pipeline



!\[Azure](https://img.shields.io/badge/azure-%230072C6.svg?style=for-the-badge\&logo=microsoftazure\&logoColor=white)

!\[Terraform](https://img.shields.io/badge/terraform-%235835CC.svg?style=for-the-badge\&logo=terraform\&logoColor=white)

!\[Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge\&logo=python\&logoColor=ffdd54)

!\[GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge\&logo=githubactions\&logoColor=white)

!\[Testing](https://img.shields.io/badge/pytest-%230A9EDC.svg?style=for-the-badge\&logo=pytest\&logoColor=white)



A resilient, event-driven ETL pipeline built on Azure: validates messy IoT sensor data, quarantines bad records, converts clean data to Parquet, and makes it instantly queryable via SQL — all serverless, all infrastructure-as-code.



> \*Upload a messy CSV. Get validated, catalogued, query-ready Parquet — automatically, for pennies.\*



\## 📖 Table of Contents

\- \[Why this project](#why-this-project)

\- \[Architecture](#architecture)

\- \[Tech Stack](#tech-stack)

\- \[Data Validation \& Quarantine](#data-validation--quarantine)

\- \[The Parquet Advantage](#the-parquet-advantage)

\- \[Analytics Layer](#analytics-layer)

\- \[Infrastructure as Code (IaC)](#infrastructure-as-code-iac)

\- \[Testing \& CI/CD](#testing--cicd)

\- \[Cost Analysis](#cost-analysis)

\- \[Future Enhancements](#future-enhancements)

\- \[Project Structure](#project-structure)



\---



\## 💡 Why this project



Most "serverless pipeline" tutorials stop at `S3 → Lambda → Output Bucket`. StratoFlow goes further by implementing real-world enterprise patterns:

\*   \*\*Granular Data Validation:\*\* Per-field rules and a quarantine pattern for bad records (dead-letter-queue methodology), rather than simple try/fail batch execution.

\*   \*\*Immediate ROI:\*\* An analytics layer that proves the output has actual value with zero downstream ETL.

\*   \*\*Infrastructure as Code:\*\* Managed entirely through Terraform, including resources adopted from manual setup into IaC—a highly common scenario in cloud engineering.



\---



\## 🏗️ Architecture



```mermaid

flowchart TD

&#x20;   A\[Raw CSV Upload<br>Azure Blob Storage] -->|Blob Trigger| B(Azure Function<br>Python)

&#x20;   B --> C{Pandera Schema<br>Validation}

&#x20;   C -- Invalid Rows --> D\[Quarantine<br>Reason Logged]

&#x20;   C -- Valid Rows --> E\[Pandas Transform]

&#x20;   E --> F\[Parquet Output<br>Azure Blob Storage]

&#x20;   F -- 61.7% Smaller --> G\[(Synapse Serverless<br>SQL Pool)]

&#x20;   G -.-> H\[Queryable via Standard SQL]



```



\---



\## 🛠️ Tech Stack



| Layer | Tool / Technology |

| --- | --- |

| \*\*Storage\*\* | Azure Blob Storage |

| \*\*Compute\*\* | Azure Functions (Python) |

| \*\*Validation\*\* | Pandera |

| \*\*Data Format\*\* | Parquet (PyArrow) |

| \*\*Analytics\*\* | Synapse Serverless SQL Pool |

| \*\*IaC\*\* | Terraform (`azurerm` provider) |

| \*\*CI/CD\*\* | GitHub Actions |

| \*\*Testing\*\* | Pytest |



\---



\## 🛡️ Data Validation \& Quarantine



Rather than failing an entire batch due to bad data, StratoFlow validates row-by-row and routes failures to quarantine with a specific reason code. Validation rules are \*\*sensor-type-aware\*\* (e.g., temperature and pressure sensors have different valid ranges), checking each row against the correct bounds for its `sensor\_type` rather than applying a blanket range.



\*\*Results on a 500-row test dataset with deliberately injected anomalies:\*\*



| Result Type | Record Count |

| --- | --- |

| ✅ \*\*Valid rows\*\* | 450 |

| ❌ Missing `reading\_value` | 18 |

| ❌ Missing `device\_id` | 15 |

| ❌ Out-of-range reading (sensor glitch) | 9 |

| ❌ Invalid dtype (`"ERROR"` string) | 8 |



\---



\## 📦 The Parquet Advantage



Converting the validated output from CSV to Parquet yielded significant performance and cost improvements:



\* \*\*Source CSV:\*\* 28,494 bytes

\* \*\*Output Parquet:\*\* 10,910 bytes

\* \*\*Result:\*\* \*\*61.7% smaller footprint\*\* utilizing columnar storage and compression, ready for direct Synapse querying without a load step.



\---



\## 📊 Analytics Layer



Processed Parquet output is queryable directly via Azure Synapse Serverless SQL Pool — no traditional data warehouse or separate ETL into a database is required.



```sql

SELECT 

&#x20;   sensor\_type, 

&#x20;   AVG(reading\_value) as avg\_reading, 

&#x20;   COUNT(\*) as count

FROM OPENROWSET(

&#x20;   BULK '\[https://stratoflowdata.blob.core.windows.net/processed-output/valid\_rows.parquet](https://stratoflowdata.blob.core.windows.net/processed-output/valid\_rows.parquet)',

&#x20;   FORMAT = 'PARQUET'

) AS rows

GROUP BY sensor\_type;



```



\*This proves the pipeline's output isn't just files sitting in storage — it's immediately analyzable, standard-SQL-accessible data.\*



\---



\## ⚙️ Infrastructure as Code (IaC)



All Azure infrastructure — resource groups, storage accounts, containers, Synapse workspaces, firewall rules, and role assignments — is managed through Terraform.



Resources were provisioned via CLI during initial setup and then \*\*imported into Terraform state\*\*, ensuring the entire environment is reproducible and version-controlled.



```bash

cd terraform

terraform init

terraform plan

terraform apply



```



\---



\## 🧪 Testing \& CI/CD



\### Testing



A suite of \*\*7 Pytest tests\*\* covers schema validation and quarantine split logic, handling edge cases like null fields, invalid categories, out-of-range values, and dtype coercion failures.



```bash

pytest -v



```



\### CI/CD Workflow



GitHub Actions runs automatically on every push/PR:



1\. \*\*Test \& Lint:\*\* Pytest suite + flake8 on the data validation logic.

2\. \*\*Terraform Validate \& Format:\*\* Confirms IaC syntactical validity without requiring cloud credentials.



> \*\*Note on Deployment:\*\* `terraform plan/apply` are currently run manually rather than in CI. The Azure tenant used for this project (an institutional subscription) restricts service principal/app registration creation. In an unrestricted environment, this would be automated via OIDC federated credentials. This reflects real-world enterprise constraints, not a limitation of the pipeline design.



\---



\## 💰 Cost Analysis



Running on Azure's serverless consumption tier and free-tier-eligible Blob Storage keeps overhead remarkably low:



\* \*\*Azure Functions:\*\* Pay-per-execution (first 1M executions/month free).

\* \*\*Blob Storage:\*\* Fractions of a cent per GB/month.

\* \*\*Synapse Serverless SQL:\*\* Pay-per-query (per TB scanned), avoiding hourly dedicated pool costs.



\*\*Estimated cost for 1,000 pipeline runs/month (small CSV files):\*\* Under $1.00/month.



\---



\## 🚀 Future Enhancements (Scaling Up)



If deploying this architecture for higher volumes, I would implement:



\* \*\*Partitioning:\*\* Partition Parquet output by `date`/`sensor\_type` for faster querying on massive datasets.

\* \*\*Schema Evolution:\*\* Dynamic handling for new sensor types and changed fields instead of a fixed schema.

\* \*\*Enterprise Messaging:\*\* Replace the single-container quarantine log with a proper Azure Service Bus dead-letter queue and alerting system.

\* \*\*Visualization:\*\* Add a lightweight dashboard (Power BI or Streamlit) on top of the Synapse queries.

\* \*\*Automated IaC:\*\* Transition from `use\_cli` local Terraform auth to OIDC federated credentials for end-to-end CI/CD.



\---



\## 📁 Project Structure



```text

stratoflow/

├── schemas/                # Pandera validation schemas

├── scripts/                # Data generation, validation, split, Parquet conversion

├── tests/                  # Pytest suite

├── sql/                    # Synapse analytics queries

├── terraform/              # Infrastructure as code (IAM, storage, Synapse)

├── function\_app.py         # Azure Functions pipeline (blob trigger)

├── .github/workflows/      # CI/CD pipeline definitions

└── data/                   # Sample dataset 



```



```



```

