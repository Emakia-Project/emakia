import json
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery

# Dump service account creds to disk (safe in Streamlit Cloud)
bq_creds_dict = dict(st.secrets["bq"]["creds"])
cred_path = "/tmp/bq_creds.json"
with open(cred_path, "w") as f:
    json.dump(bq_creds_dict, f)

# Load creds and initialize BigQuery client
creds = service_account.Credentials.from_service_account_file(cred_path)
client = bigquery.Client(credentials=creds, project=creds.project_id)

st.title("✅ Streamlit BigQuery Debug")

# Inspect the client object without triggering DataFrame conversion
st.subheader("🔍 BigQuery Client Metadata")
st.write("Client project:", client.project)
st.write("Client location:", client.location or "default")
st.write("Credentials service account email:", creds.service_account_email)
st.subheader("🔎 Private key preview (debug only!)")
st.code(repr(bq_creds_dict["private_key"]))

limit = 25
offset = 50

# Try running the query
try:
    st.subheader("🧪 Running Test Query on Public Dataset")
    query = """
        SELECT id, text, possibly_sensitive
        FROM `emakia.politics2024.tweets`
        ORDER BY text
        LIMIT {limit} OFFSET {offset}
    """

    df = client.query(query).to_dataframe()
    st.dataframe(df)
    st.success("✅ Query succeeded and returned data.")
except Exception as e:
    st.error(f"❌ Failed to run query: {e}")
