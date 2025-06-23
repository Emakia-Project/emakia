import json
from google.oauth2 import service_account
from google.cloud import bigquery
import streamlit as st
import os

# Safely parse the stringified JSON from secrets.toml
bq_creds_raw = st.secrets["bq"]["creds"]
bq_creds_dict = json.loads(bq_creds_raw)

# Write to a temporary file
cred_path = "/tmp/bq_creds.json"
with open(cred_path, "w") as f:
    json.dump(bq_creds_dict, f)

# Load credentials from the temp file
creds = service_account.Credentials.from_service_account_file(cred_path)
client = bigquery.Client(credentials=creds, project=creds.project_id)
