"""

gatekeeper/_utils.py

Contains DB Handlers / Utils.
"""

import pandas as pd
from google.cloud import bigquery

def upload_dataframe_to_bq(df: pd.DataFrame, table_ref: str):
    """ Uploads a pandas DataFrame to a specified BigQuery table. """

    client = bigquery.Client()

    # table_ref = f"{project_id}.{dataset_id}.{table_id}"
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=True
    )
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()  # Wait for the job to complete.
    print(f"✅ Data uploaded to {table_ref}")
