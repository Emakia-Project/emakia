import json
import os
from google.oauth2 import service_account
from google.cloud import bigquery
import streamlit as st

# Parse the stringified JSON from secrets and write it to a file
bq_creds = json.loads(st.secrets["bq"]["creds"])
cred_path = "/tmp/bq_creds.json"  # Use /tmp or a local secure location

with open(cred_path, "w") as f:
    json.dump(bq_creds, f)

# Explicitly load the service account using the freshly written file
creds = service_account.Credentials.from_service_account_file(cred_path)
client = bigquery.Client(credentials=creds, project=creds.project_id)
