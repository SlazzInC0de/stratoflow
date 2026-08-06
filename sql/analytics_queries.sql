## Phase 3: Analytics

Processed Parquet output is queryable directly via Azure Synapse Serverless SQL Pool — no data warehouse or ETL into a database required.

**Example — average reading by sensor type:**
```sql
SELECT sensor_type, AVG(reading_value) as avg_reading, COUNT(*) as count
FROM OPENROWSET(
    BULK 'https://stratoflowdata.blob.core.windows.net/processed-output/valid_rows.parquet',
    FORMAT = 'PARQUET'
) AS rows
GROUP BY sensor_type;
```

This proves the pipeline's output isn't just files in storage — it's immediately analyzable, standard-SQL-accessible data.