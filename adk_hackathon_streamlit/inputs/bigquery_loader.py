from google.cloud import bigquery
from dotenv import load_dotenv
import os
from google.cloud import bigquery

# Path to your service account key JSON file
SERVICE_ACCOUNT_KEY_PATH = "/Users/corinnedavid/Downloads/emakia-236347b5f4b3.json"

# Construct a BigQuery client object with credentials
client = bigquery.Client.from_service_account_json(SERVICE_ACCOUNT_KEY_PATH)
# Load environment variables (including credentials path)
load_dotenv()

# Initialize BigQuery client
def init_bigquery_client():
    try:
        # Construct a BigQuery client object with credentials
        client = bigquery.Client.from_service_account_json(SERVICE_ACCOUNT_KEY_PATH)
        print("✅ BigQuery client initialized.")
        return client
    except Exception as e:
        print(f"❌ Error initializing BigQuery client: {e}")
        return None

# Fetch tweets with cleaned content and link parsing
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
        seen_contents = set()
        tweets = []

        for row in results:
            raw_text = row.text.strip()

            # Extract link from text (if present)
            if "https://" in raw_text:
                content_part, link_part = raw_text.split("https://", 1)
                content = content_part.strip()
                link = "https://" + link_part.strip()
            else:
                content = raw_text
                link = None

            if content not in seen_contents:
                tweets.append({
                    #"id": row.id,
                    "title": row.id,
                    "content": content,
                    "link": link,
                    #"sensitive": row.possibly_sensitive
                })
                seen_contents.add(content)

        print(f"✅ Retrieved {len(tweets)} unique tweets with cleaned content + link.")
        return tweets

    except Exception as e:
        print(f"❌ Failed to fetch tweets: {e}")
        return []

# --- Run as standalone test ---
if __name__ == "__main__":
    tweets = get_tweets_from_bigquery()
    for i, tweet in enumerate(tweets, 1):
        print(f"{i}. Row ID: {tweet['id']} | Sensitive: {tweet['sensitive']}")
        print(f"   Content: {tweet['content']}")
        print(f"   Link: {tweet['link']}\n")
