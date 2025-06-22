import json
import os
from google.oauth2 import service_account
from google.cloud import bigquery
import streamlit as st

# Use the creds directly since it's already a dict
bq_creds = st.secrets["bq"]["creds"]
cred_path = "/tmp/bq_creds.json"

with open(cred_path, "w") as f:
    json.dump(bq_creds, f)

# Load from the clean, written file
creds = service_account.Credentials.from_service_account_file(cred_path)
client = bigquery.Client(credentials=creds, project=creds.project_id)
