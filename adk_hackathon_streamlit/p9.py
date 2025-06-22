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

limit=25
offset=50

query = f"""
        SELECT id, text, possibly_sensitive
        FROM `emakia.politics2024.tweets`
        ORDER BY text
        LIMIT {limit} OFFSET {offset}
    """

results = client.query(query).result()

print(client.list_datasets())
list_datasets = client.list_datasets()




