import os
from dotenv import load_dotenv
from pipeline.ingest_bigquery import fetch_tweets
from pipeline.classify_batch import classify_batch
from pipeline.graph_updater import update_tweet_metadata_in_neo4j
from utils.logging import log_result

# Load env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "password")

# Ingest tweets
tweets = [{"id": f"id_{i}", "text": t} for i, t in enumerate(fetch_tweets("my_dataset", "my_table"))]

# Classify
results = classify_batch(tweets)

# Update graph
for tweet_id, labels in results.items():
    update_tweet_metadata_in_neo4j(NEO4J_URI, NEO4J_AUTH, tweet_id, labels)
    log_result(tweet_id, labels)
