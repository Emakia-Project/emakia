# Install dependencies
# pip install crewai weave google-cloud-bigquery neo4j

import weave
from crewai import Agent, Task, Crew, LLM, Process
from google.cloud import bigquery
from neo4j import GraphDatabase
from flask import Flask, jsonify

import json
from dotenv import load_dotenv
from google.oauth2 import service_account

# Only load .env if it exists (for local dev)
load_dotenv()


import os
import json



from dotenv import load_dotenv
load_dotenv()

def load_bq_credentials():
    import json, os
    raw_creds = os.environ.get("BQ_CREDS")
    if raw_creds:
        creds = json.loads(raw_creds)
        creds["private_key"] = creds["private_key"].replace("\\n", "\n")
        return creds
    else:
        return {
            "type": os.environ["TYPE"],
            "project_id": os.environ["PROJECT_ID"],
            "private_key_id": os.environ["PRIVATE_KEY_ID"],
            "private_key": os.environ["PRIVATE_KEY"].replace("\\n", "\n"),
            "client_email": os.environ["CLIENT_EMAIL"],
            "client_id": os.environ["CLIENT_ID"],
            "auth_uri": os.environ["AUTH_URI"],
            "token_uri": os.environ["TOKEN_URI"],
            "auth_provider_x509_cert_url": os.environ["AUTH_PROVIDER_X509_CERT_URL"],
            "client_x509_cert_url": os.environ["CLIENT_X509_CERT_URL"],
            "universe_domain": os.environ["UNIVERSE_DOMAIN"]
        }


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

app = Flask(__name__)


# Initialize Weave
weave.init(project_name="tweet_classification_pipeline")

# Step 1: Fetch tweets from BigQuery
def fetch_tweets("emakia", "politics2024", "tweets"):
    client = bigquery.Client()
    query = """
        SELECT id, text, possibly_sensitive
        FROM `emakia.politics2024.tweets`
        LIMIT 100
    """
    results = client.query(query).result()
    return [dict(row) for row in results]

# Step 2: Define LLM and Agent
llm = LLM(model="gpt-4o", temperature=0)

classifier_agent = Agent(
    role="Tweet Classifier",
    goal="Classify tweets into categories like misinformation, sentiment, or relevance",
    backstory="An expert in NLP and social media analysis",
    llm=llm,
    verbose=True
)

# Step 3: Create Task
classification_task = Task(
    description="Classify the following tweets: {tweets}",
    expected_output="A list of tweet IDs with their classification labels",
    agent=classifier_agent
)

# Step 4: Run Crew
def classify_tweets(tweets):
    crew = Crew(
        agents=[classifier_agent],
        tasks=[classification_task],
        verbose=True,
        process=Process.sequential
    )
    result = crew.kickoff(inputs={"tweets": tweets})
    return result

# Step 5: Push to Neo4j (optional)
def load_tweets_to_neo4j(classified_data):


    def create_nodes_and_relationships(tx, tweet):
        tx.run("""
            MERGE (t1:Tweet {tweet_id: $tweet_id})
            SET t1.text = $text, t1.created_at = $created_at
            WITH t1
            MERGE (t2:Tweet {tweet_id: $referenced_tweet_id})
            MERGE (t1)-[:RETWEETED]->(t2)
        """, tweet_id=tweet["tweet_id"],
             text=tweet["text"],
             created_at=str(tweet["created_at"]),
             referenced_tweet_id=tweet["referenced_tweet_id"])

    with driver.session() as session:
        for tweet in tweets:
            if tweet.get("referenced_tweet_id"):
                #session.write_transaction(create_nodes_and_relationships, tweet)
                session.execute_write(create_nodes_and_relationships, tweet)
                #session.execute_write(create_nodes_and_relationships, tweet)


    print("✅ All tweets loaded into Neo4j.")


# --- Neo4j credentials and execution ---
neo4j_uri = "neo4j+s://fe163f2d.databases.neo4j.io"
neo4j_user = "neo4j"
neo4j_password = "vFc6xsYHQMfTfCWY_yaDytcY-O7E9PT3JnJtJhLCSkE"  # Consider moving this to Streamlit secrets

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))





if __name__ == "__main__":
    tweets = fetch_tweets()
    if tweets:
        tweet_text_only = tweets[0]["text"]
        print("🧪 Testing with one text input:", tweet_text_only)
        result = classify_tweets(tweet_text_only)
        print("🎯 Classification result:", result.raw_output)

    else:
        print("⚠️ No tweets found in BigQuery.")


