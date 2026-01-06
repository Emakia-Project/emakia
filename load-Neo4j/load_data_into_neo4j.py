from __future__ import annotations

import argparse
import json
import os
import re
from typing import Iterable

from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account
from neo4j import GraphDatabase
from openai import OpenAI

load_dotenv()


def extract_label(raw_text: str, expected_values: list[str]) -> str:
    """Extract a classification label from LLM output."""
    if not raw_text:
        return "unknown"

    text = raw_text.strip().lower()
    for val in sorted(expected_values, key=len, reverse=True):
        if re.search(rf"\b{re.escape(val.lower())}\b", text):
            return val
    return "unknown"


def classify_tweet_with_openai(text: str, client: OpenAI, model: str) -> dict[str, str]:
    """Classify a tweet using OpenAI API with a single combined prompt."""
    
    prompt = f"""Analyze the following tweet and classify it on three dimensions:

Tweet: "{text}"

Provide classifications for:
1. Toxicity: Is it 'toxic' or 'non-toxic'?
2. Misinformation: Is it 'misinformation' or 'non-misinformation'?
3. Bias: Is it 'biased' or 'non-biased'?

Respond in this exact format:
Toxicity: [toxic/non-toxic]
Misinformation: [misinformation/non-misinformation]
Bias: [biased/non-biased]"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert at analyzing social media content for toxicity, misinformation, and bias."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=150
        )
        
        result_text = response.choices[0].message.content
        
        # Parse the response
        toxicity = extract_label(result_text, ["non-toxic", "toxic"])
        misinfo = extract_label(result_text, ["non-misinformation", "misinformation"])
        bias = extract_label(result_text, ["non-biased", "biased"])
        
        return {
            "toxicity": toxicity,
            "misinfo": misinfo,
            "bias": bias
        }
    except Exception as e:
        print(f"⚠️ Error classifying tweet: {e}")
        return {
            "toxicity": "unknown",
            "misinfo": "unknown",
            "bias": "unknown"
        }


def load_bq_credentials() -> dict | None:
    raw_creds = os.environ.get("BQ_CREDS")
    if not raw_creds:
        return None
    creds = json.loads(raw_creds)
    if "private_key" in creds and isinstance(creds["private_key"], str):
        creds["private_key"] = creds["private_key"].replace("\\n", "\n")
    return creds


def init_bigquery_client() -> bigquery.Client:
    """Initialize BigQuery client using either BQ_CREDS JSON or ADC."""
    creds_dict = load_bq_credentials()
    if creds_dict:
        creds = service_account.Credentials.from_service_account_info(creds_dict)
        project_id = creds_dict.get("project_id")
        return bigquery.Client(credentials=creds, project=project_id)
    return bigquery.Client()


def fetch_tweets(
    client: bigquery.Client,
    project_id: str,
    dataset_id: str,
    table_id: str,
    limit: int,
    offset: int,
) -> list[dict]:
    query = f"""
        SELECT
            t.id AS tweet_id,
            t.text,
            t.author_id,
            t.created_at,
            t.possibly_sensitive,
            ref_tweet.id AS referenced_tweet_id
        FROM `{project_id}.{dataset_id}.{table_id}` AS t
        LEFT JOIN UNNEST(t.referenced_tweets) AS ref_tweet
        WHERE t.text IS NOT NULL
        LIMIT {int(limit)} OFFSET {int(offset)}
    """
    results = client.query(query).result()
    return [dict(row) for row in results]


def get_neo4j_driver():
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USER")
    password = os.environ.get("NEO4J_PASSWORD")
    if not uri or not user or not password:
        raise ValueError(
            "Missing Neo4j config. Set NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD (in env or .env)."
        )
    return GraphDatabase.driver(uri, auth=(user, password))


def initialize_neo4j_schema(driver) -> None:
    """Create constraints and indexes for the Neo4j database."""
    print("🔧 Initializing Neo4j schema...")
    
    with driver.session() as session:
        # Create uniqueness constraint on tweet_id (also creates an index)
        try:
            session.run(
                "CREATE CONSTRAINT tweet_id_unique IF NOT EXISTS "
                "FOR (t:Tweet) REQUIRE t.tweet_id IS UNIQUE"
            )
            print("✅ Created uniqueness constraint on Tweet.tweet_id")
        except Exception as e:
            print(f"⚠️ Constraint may already exist: {e}")
        
        # Create index on author_id for faster lookups
        try:
            session.run(
                "CREATE INDEX tweet_author_idx IF NOT EXISTS "
                "FOR (t:Tweet) ON (t.author_id)"
            )
            print("✅ Created index on Tweet.author_id")
        except Exception as e:
            print(f"⚠️ Index may already exist: {e}")
        
        # Create index on created_at for temporal queries
        try:
            session.run(
                "CREATE INDEX tweet_created_at_idx IF NOT EXISTS "
                "FOR (t:Tweet) ON (t.created_at)"
            )
            print("✅ Created index on Tweet.created_at")
        except Exception as e:
            print(f"⚠️ Index may already exist: {e}")
    
    print("✅ Schema initialization complete\n")


def create_bigquery_results_table(client: bigquery.Client, project_id: str, dataset_id: str) -> None:
    """Create the results table in BigQuery if it doesn't exist."""
    table_id = f"{project_id}.{dataset_id}.results"
    
    schema = [
        bigquery.SchemaField("tweet_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("text", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("author_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("possibly_sensitive", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("referenced_tweet_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("toxicity", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("misinformation", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("bias", "STRING", mode="NULLABLE"),
    ]
    
    table = bigquery.Table(table_id, schema=schema)
    try:
        client.create_table(table)
        print(f"✅ Created BigQuery table: {table_id}")
    except Exception as e:
        print(f"⚠️ Table may already exist: {e}")


def insert_results_to_bigquery(
    client: bigquery.Client,
    project_id: str,
    dataset_id: str,
    results: list[dict]
) -> int:
    """Insert classified results into BigQuery. Duplicates will be handled by checking existing IDs."""
    table_id = f"{project_id}.{dataset_id}.results"
    
    try:
        # Step 1: Get existing tweet_ids to avoid duplicates
        tweet_ids = [result["tweet_id"] for result in results]
        tweet_ids_str = ','.join([f"'{tid}'" for tid in tweet_ids])
        
        check_query = f"""
        SELECT tweet_id 
        FROM `{table_id}`
        WHERE tweet_id IN ({tweet_ids_str})
        """
        existing_ids = set()
        try:
            existing_result = client.query(check_query).result()
            existing_ids = {row.tweet_id for row in existing_result}
        except Exception:
            # Table might be empty or query failed, continue with all inserts
            pass
        
        # Step 2: Prepare rows (only new ones)
        rows_to_insert = []
        for result in results:
            if result["tweet_id"] in existing_ids:
                continue  # Skip duplicates
                
            created_at = result.get("created_at")
            if created_at is not None:
                created_at = str(created_at)
            
            row = {
                "tweet_id": result["tweet_id"],
                "text": result.get("text"),
                "author_id": result.get("author_id"),
                "created_at": created_at,
                "possibly_sensitive": result.get("possibly_sensitive"),
                "referenced_tweet_id": result.get("referenced_tweet_id"),
                "toxicity": result.get("toxicity"),
                "misinformation": result.get("misinfo"),
                "bias": result.get("bias"),
            }
            rows_to_insert.append(row)
        
        if not rows_to_insert:
            print(f"⚠️ All {len(results)} tweets already exist in BigQuery, skipping insert")
            return 0
        
        # Step 3: Insert new rows
        errors = client.insert_rows_json(table_id, rows_to_insert)
        if errors:
            print(f"❌ Errors inserting rows to BigQuery: {errors}")
            return 0
        
        skipped = len(results) - len(rows_to_insert)
        if skipped > 0:
            print(f"ℹ️ Skipped {skipped} duplicate tweets")
        
        return len(rows_to_insert)
        
    except Exception as e:
        print(f"❌ Error during BigQuery insert: {e}")
        return 0


def load_tweets_to_neo4j(driver, tweets: Iterable[dict]) -> int:
    """Load tweets into Neo4j with all properties including classifications."""
    def create_nodes_and_relationships(tx, tweet: dict):
        # Create or update the tweet node with ALL properties
        tx.run(
            """
            MERGE (t:Tweet {tweet_id: $tweet_id})
            SET t.text = $text,
                t.author_id = $author_id,
                t.created_at = $created_at,
                t.possibly_sensitive = $possibly_sensitive,
                t.toxicity = $toxicity,
                t.misinformation = $misinfo,
                t.bias = $bias
            """,
            tweet_id=tweet["tweet_id"],
            text=tweet.get("text"),
            author_id=tweet.get("author_id"),
            created_at=str(tweet.get("created_at")) if tweet.get("created_at") else None,
            possibly_sensitive=tweet.get("possibly_sensitive"),
            toxicity=tweet.get("toxicity"),
            misinfo=tweet.get("misinfo"),
            bias=tweet.get("bias"),
        )

        # Create relationship if this is a retweet/reply
        if tweet.get("referenced_tweet_id"):
            tx.run(
                """
                MERGE (target:Tweet {tweet_id: $referenced_tweet_id})
                MERGE (source:Tweet {tweet_id: $tweet_id})
                MERGE (source)-[:RETWEETED]->(target)
                """,
                tweet_id=tweet["tweet_id"],
                referenced_tweet_id=tweet["referenced_tweet_id"],
            )

    inserted = 0
    failed = 0
    with driver.session() as session:
        for tweet in tweets:
            try:
                session.execute_write(create_nodes_and_relationships, tweet)
                inserted += 1
            except Exception as e:
                failed += 1
                print(f"⚠️ Failed to insert tweet {tweet.get('tweet_id')}: {e}")
    
    if failed > 0:
        print(f"⚠️ {failed} tweets failed to insert into Neo4j")
    
    return inserted


def main() -> int:
    parser = argparse.ArgumentParser(description="Load tweets from BigQuery, classify with LLM, store in Neo4j and BigQuery.")
    parser.add_argument("--bq-project", default=os.getenv("BQ_PROJECT", "emakia"))
    parser.add_argument("--bq-dataset", default=os.getenv("BQ_DATASET", "politics2024"))
    parser.add_argument("--bq-table", default=os.getenv("BQ_TABLE", "tweets"))
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--batches", type=int, default=5)
    parser.add_argument("--offset", type=int, default=500)
    parser.add_argument(
        "--mode",
        choices=["load-only", "classify"],
        default="classify",
        help="load-only=import tweets without classification; classify=classify and store in both Neo4j and BigQuery",
    )
    parser.add_argument("--llm-model", default=os.getenv("LLM_MODEL", "gpt-4o-mini"))
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--init-schema", action="store_true", help="Initialize Neo4j schema (constraints and indexes)")
    args = parser.parse_args()

    bq_client = init_bigquery_client()
    driver = get_neo4j_driver()

    # Initialize Neo4j schema
    if args.init_schema or args.mode in {"load-only", "classify"}:
        initialize_neo4j_schema(driver)

    # Create BigQuery results table if in classify mode
    if args.mode == "classify":
        create_bigquery_results_table(bq_client, args.bq_project, args.bq_dataset)

    # Initialize OpenAI client if in classify mode
    openai_client = None
    if args.mode == "classify":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY in environment variables")
        openai_client = OpenAI(api_key=api_key)
        print(f"✅ Using OpenAI model: {args.llm_model}\n")

    try:
        for batch_num in range(args.batches):
            batch_offset = args.offset + batch_num * args.batch_size
            print(f"\n🔄 Processing batch {batch_num + 1}/{args.batches} (rows {batch_offset}–{batch_offset + args.batch_size - 1})")

            tweets_batch = fetch_tweets(
                bq_client,
                args.bq_project,
                args.bq_dataset,
                args.bq_table,
                limit=args.batch_size,
                offset=batch_offset,
            )
            if not tweets_batch:
                print("⚠️ No tweets retrieved in this batch.")
                continue

            if args.mode == "load-only":
                # Load tweets without classification
                inserted = load_tweets_to_neo4j(driver, tweets_batch)
                print(f"✅ Loaded {inserted} tweets into Neo4j (no classification).")
            
            elif args.mode == "classify":
                # Classify tweets and add predictions to each tweet
                classified_tweets = []
                for i, tweet in enumerate(tweets_batch, 1):
                    if args.verbose and i % 10 == 0:
                        print(f"  📊 Classifying tweet {i}/{len(tweets_batch)}...")
                    
                    result = classify_tweet_with_openai(
                        tweet.get("text", ""),
                        openai_client,
                        args.llm_model
                    )
                    tweet["toxicity"] = result["toxicity"]
                    tweet["misinfo"] = result["misinfo"]
                    tweet["bias"] = result["bias"]
                    classified_tweets.append(tweet)
                
                # Store in Neo4j with all data
                inserted = load_tweets_to_neo4j(driver, classified_tweets)
                print(f"✅ Loaded {inserted} classified tweets into Neo4j.")
                
                # Store in BigQuery results table
                bq_inserted = insert_results_to_bigquery(
                    bq_client,
                    args.bq_project,
                    args.bq_dataset,
                    classified_tweets
                )
                print(f"✅ Inserted {bq_inserted} results into BigQuery table: {args.bq_project}.{args.bq_dataset}.results")
    
    finally:
        driver.close()
    
    print("\n" + "="*60)
    print("📊 FINAL SUMMARY")
    print("="*60)
    
    # Verify Neo4j counts
    try:
        with driver.session() as session:
            result = session.run("MATCH (t:Tweet) WHERE t.toxicity IS NOT NULL RETURN count(t) as count")
            neo4j_count = result.single()["count"]
            print(f"✅ Neo4j classified tweets: {neo4j_count}")
    except Exception as e:
        print(f"⚠️ Could not verify Neo4j count: {e}")
    
    # Verify BigQuery counts
    try:
        query = f"SELECT COUNT(*) as count FROM `{args.bq_project}.{args.bq_dataset}.results`"
        result = bq_client.query(query).result()
        bq_count = result.to_dataframe()['count'].values[0]
        print(f"✅ BigQuery results table: {bq_count}")
    except Exception as e:
        print(f"⚠️ Could not verify BigQuery count: {e}")
    
    print("="*60)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())