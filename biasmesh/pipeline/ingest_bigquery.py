from google.cloud import bigquery

def fetch_tweets(dataset, table, limit=100):
    client = bigquery.Client()
    query = f"SELECT text FROM `{dataset}.{table}` LIMIT {limit}"
    return [row["text"] for row in client.query(query).result()]
