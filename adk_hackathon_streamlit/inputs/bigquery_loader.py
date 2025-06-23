import os
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery

# --- Load and format credentials from Streamlit secrets ---
def load_bq_credentials():
    bq_creds_dict = dict(st.secrets["bq"]["creds"])

    # Fix escaped newlines in the private key
    if "\\n" in bq_creds_dict["private_key"]:
        bq_creds_dict["private_key"] = bq_creds_dict["private_key"].replace("\\n", "\n")

    return bq_creds_dict

# --- Initialize BigQuery client with explicit project ID ---
def init_bigquery_client():
    try:
        creds_dict = load_bq_credentials()
        creds = service_account.Credentials.from_service_account_info(creds_dict)
        project_id = creds_dict.get("project_id")

        if not project_id:
            raise ValueError("❌ Missing 'project_id' in credentials.")

        client = bigquery.Client(credentials=creds, project=project_id)
        print("✅ BigQuery client initialized.")
        return client
    except Exception as e:
        print(f"❌ Error initializing BigQuery client: {e}")
        return None

# --- Query tweets from BigQuery and extract text/link pairs ---
def get_tweets_from_bigquery(limit=25, offset=50):
    client = init_bigquery_client()
    if not client:
        print("❌ No BigQuery client available.")
        return []

    query = f"""
        SELECT id, text, possibly_sensitive
        FROM `emakia.politics2024.tweets`
        ORDER BY text
        LIMIT {limit} OFFSET {offset}
    """

    try:
        results = client.query(query).result()
        tweets, seen_contents = [], set()

        for row in results:
            raw_text = row.text.strip()
            content, link = raw_text, None

            if "https://" in raw_text:
                content, link_part = raw_text.split("https://", 1)
                content = content.strip()
                link = "https://" + link_part.strip()

            if content not in seen_contents:
                tweets.append({
                    "title": row.id,
                    "content": content,
                    "link": link,
                })
                seen_contents.add(content)

        print(f"✅ Retrieved {len(tweets)} unique tweets.")
        return tweets

    except Exception as e:
        print(f"❌ Failed to fetch tweets: {e}")
        return []

# --- Standalone testing block ---
if __name__ == "__main__":
    tweets = get_tweets_from_bigquery()
    for i, tweet in enumerate(tweets, 1):
        print(f"{i}. ID: {tweet['title']}")
        print(f"   Content: {tweet['content']}")
        print(f"   Link: {tweet['link']}\n")
