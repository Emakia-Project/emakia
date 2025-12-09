


from flask import Flask, jsonify
from google.cloud import bigquery
from google.oauth2 import service_account
from dotenv import load_dotenv
import json
import os
from flask import request

# Local dev support
try:
    import streamlit as st
except ImportError:
    st = None

load_dotenv()
app = Flask(__name__)

# --- Credential Loader ---
def load_bq_credentials():
    try:
        # ✅ LOCAL: Streamlit secrets
        if st and "bq" in st.secrets and "creds" in st.secrets["bq"]:
            creds_dict = dict(st.secrets["bq"]["creds"])
            if "\\n" in creds_dict["private_key"]:
                creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            print("🟢 Using Streamlit secrets for BigQuery.")
            return creds_dict
        
        # ✅ PROD: Heroku via BQ_CREDS
        raw_creds = os.environ.get("BQ_CREDS")
        if raw_creds:
            creds_dict = json.loads(raw_creds)
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            print("🟡 Using Heroku BQ_CREDS env var for BigQuery.")
            return creds_dict

        raise RuntimeError("❌ No valid BigQuery credentials found.")
    except Exception as e:
        print("❌ Failed to load BigQuery credentials:", e)
        return None

# --- Client Initializer ---
def init_bigquery_client():
    creds_dict = load_bq_credentials()
    if creds_dict:
        creds = service_account.Credentials.from_service_account_info(creds_dict)
        return bigquery.Client(credentials=creds, project=creds_dict.get("project_id"))
    else:
        return None

client = init_bigquery_client()

# --- Routes ---
@app.route("/")
def index():
    return "Emakia Tech API is running 🚀"



@app.route("/api/tweet-cascade", methods=["GET"])
def get_tweet_cascade():
    if client is None:
        return jsonify({"error": "BigQuery client not initialized"}), 500

    topic = request.args.get("topic")
    limit = request.args.get("limit", default=50, type=int)
    sensitive_filter = request.args.get("sensitive_filter")  # "true", "false", or None

    try:
        # 🔍 Filtering logic
        filters = []
        if topic:
            filters.append(f"LOWER(t.text) LIKE '%{topic.lower()}%'")
        if sensitive_filter == "true":
            filters.append("t.possibly_sensitive = TRUE")
        elif sensitive_filter == "false":
            filters.append("t.possibly_sensitive = FALSE")

        # 🧠 Enriched tweet query with JOIN to users table
        base_query = """
            SELECT
                t.id AS tweet_id,
                t.text AS content,
                t.author_id,
                t.possibly_sensitive,
                t.created_at,
                u.username,
                u.name,
                u.profile_image_url
            FROM `emakia.politics2024.tweets` AS t
            LEFT JOIN `emakia.politics2024.users` AS u
                ON t.author_id = u.id
        """

        if filters:
            base_query += " WHERE " + " AND ".join(filters)
        base_query += f" ORDER BY t.created_at DESC LIMIT {limit}"

        # 🧪 Execute query
        query_job = client.query(base_query)
        results = query_job.result()

        # 📦 Format output
        data = [
            {
                "tweet_id": row.tweet_id,
                "content": row.content,
                "author_id": row.author_id,
                "possibly_sensitive": row.possibly_sensitive,
                "created_at": str(row.created_at),
                "username": row.username,
                "name": row.name,
                "profile_image_url": row.profile_image_url
            }
            for row in results
        ]

        return jsonify(data)

    except Exception as e:
        print(f"❌ Query error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run()
