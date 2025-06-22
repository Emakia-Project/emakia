import json
from google.oauth2 import service_account
from google.cloud import bigquery
import streamlit as st
import os


bq_creds_dict = dict(st.secrets["bq"]["creds"])


# Write to a temporary file
cred_path = "/tmp/bq_creds.json"
with open(cred_path, "w") as f:
    json.dump(bq_creds_dict, f)

# Load credentials from the temp file
creds = service_account.Credentials.from_service_account_file(cred_path)
#client = bigquery.Client(credentials=creds, project=creds.project_id)



client = bigquery.Client(credentials=creds, project=creds.project_id)# Quick test
print(f"Found client: {client.project}")
for dataset in client.list_datasets():  
    print(f"Found dataset: {dataset.dataset_id}")