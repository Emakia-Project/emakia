import json
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import db_dtypes  # 👈 Forces BigQuery to register its custom dtype handlers

import sys



# Load credentials from secrets
bq_creds_dict = dict(st.secrets["bq"]["creds"])
print("bq_creds_dict-private_key")
print(bq_creds_dict["private_key"])
# Fix the private key line breaks, if they’ve been escaped
if "\\n" in bq_creds_dict["private_key"]:
    bq_creds_dict["private_key"] = bq_creds_dict["private_key"].replace("\\n", "\n")

# Write fixed creds to disk
cred_path = "/Users/corinnedavid/Downloads/emakia-236347b5f4b3.json"
#with open(cred_path, "w") as f:
    #json.dump(bq_creds_dict, f, indent=2)


# Load credentials and initialize BigQuery client
creds = service_account.Credentials.from_service_account_file(cred_path)

client = bigquery.Client(credentials=creds, project=creds.project_id)

st.title("✅ Streamlit BigQuery Debug")
st.text(f"Python binary: {sys.executable}")
# Show metadata
st.subheader("🔍 BigQuery Client Metadata")
st.write("Client project:", client.project)
st.write("Client location:", client.location or "default")
st.write("Credentials service account email:", creds.service_account_email) 
st.write("Credentials project ID:", bq_creds_dict["private_key"][:400]) 

# Check the private key in memory (safe for debug)
st.subheader("🔎 Private key preview (debug only!)")
#st.code(repr(bq_creds_dict["private_key"][:100]) + "...")

# Query setup
limit = 25
offset = 50

try:
    st.subheader("🧪 Running Test Query on Public Dataset")
    query = f"""
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
