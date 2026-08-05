import azure.functions as func
from azure.storage.blob import BlobClient
import json
import sys
import pandas as pd
from io import StringIO, BytesIO
import logging

sys.path.append(".")
from scripts.split_valid_invalid import split

app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="raw-uploads/{name}", connection="AzureWebJobsStorage")
async def stratoflow_pipeline(myblob: func.InputStream, context: func.Context) -> None:
    """
    Blob trigger: validates CSV, splits valid/invalid, uploads Parquet output.
    """
    logging.info(f"Processing blob: {myblob.name}")
    
    try:
        # 1. Read CSV from blob
        csv_content = myblob.read().decode('utf-8')
        csv_df = pd.read_csv(StringIO(csv_content))
        
        # 2. Validate & split using Phase 1 logic
        temp_path = f"/tmp/{myblob.name}"
        csv_df.to_csv(temp_path, index=False)
        valid, invalid = split(temp_path)
        
        logging.info(f"Valid: {len(valid)}, Invalid: {len(invalid)}")
        
        # 3. If invalid rows, log them (TODO: send to Service Bus DLQ later)
        if len(invalid) > 0:
            logging.warning(f"Quarantined {len(invalid)} invalid rows")
        
        # 4. Convert valid rows to Parquet
        parquet_buffer = BytesIO()
        valid.to_parquet(parquet_buffer, engine='pyarrow', index=False)
        parquet_buffer.seek(0)
        
        # 5. Upload to output blob
        output_blob_name = myblob.name.replace('.csv', '.parquet')
        # TODO: Upload to "processed-output" container
        # blob_client = BlobClient.from_connection_string(...)
        # blob_client.upload_blob(parquet_buffer.getvalue(), overwrite=True)
        
        logging.info(f"Successfully processed {len(valid)} rows → {output_blob_name}")
        
    except Exception as e:
        logging.error(f"Pipeline failed: {str(e)}")
        raise