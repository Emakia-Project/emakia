from google.cloud import bigquery

# Path to your service account key JSON file
SERVICE_ACCOUNT_KEY_PATH = "/Users/corinnedavid/Downloads/emakia-236347b5f4b3.json"

# Construct a BigQuery client object with credentials
client = bigquery.Client.from_service_account_json(SERVICE_ACCOUNT_KEY_PATH)

# Define your SQL query
query = """
    SELECT *
    FROM `emakia.politics2024.tweets`
    LIMIT 10
"""

# Make an API request
query_job = client.query(query)

# Process and print results
for row in query_job:
    print(dict(row))  # You can convert rows to dictionaries for easier access
