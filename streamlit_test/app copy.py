import json
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery  # <-- You need this

# Write credentials to temp file
bq_creds_dict = dict(st.secrets["bq"]["creds"])
cred_path = "/tmp/bq_creds.json"
with open(cred_path, "w") as f:
    json.dump(bq_creds_dict, f)

# Load credentials and initialize client
creds = service_account.Credentials.from_service_account_file(cred_path)
client = bigquery.Client(credentials=creds, project=creds.project_id)



st.title("✅ Streamlit BigQuery Test")

try:
    query = """
        SELECT name, SUM(number) as total
        FROM `bigquery-public-data.usa_names.usa_1910_current`
        WHERE state = 'CA'
        GROUP BY name
        ORDER BY total DESC
        LIMIT 10
    """

    st.write("Running test query on public dataset…")
    df = client.query(query).to_dataframe()
    st.dataframe(df)
    st.success("Success! Query ran and returned results.")
except Exception as e:
    st.error(f"❌ Failed to run query: {e}")
