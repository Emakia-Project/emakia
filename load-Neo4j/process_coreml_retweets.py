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

load_dotenv()


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


def fetch_coreml_predictions(
    client: bigquery.Client,
    project_id: str,
    dataset_id: str,
    limit: int,
    offset: int,
) -> list[dict]:
    """Fetch predictions from CoreMLpredictions table."""
    query = f"""
        SELECT
            tweet_id,
            text,
            prediction,
            score,
            model_version,
            prediction_llm0,
            score_llm0,
            prediction_llm3,
            score_llm3,
            prediction_llm4,
            score_llm4,
            possibly_sensitive,
            created_at,
            updated_at,
            normalized_text,
            rn
        FROM `{project_id}.{dataset_id}.CoreMLpredictions`
        LIMIT {int(limit)} OFFSET {int(offset)}
    """
    results = client.query(query).result()
    return [dict(row) for row in results]


def find_retweets_for_tweet(
    client: bigquery.Client,
    project_id: str,
    dataset_id: str,
    tweet_id: str,
) -> list[dict]:
    """Find all retweets of a specific tweet from the tweets table."""
    query = f"""
        SELECT
            t.id AS retweet_id,
            t.text AS retweet_text,
            t.author_id AS retweeter_id,
            t.created_at AS retweet_created_at,
            t.possibly_sensitive,
            ref_tweet.id AS referenced_tweet_id
        FROM `{project_id}.{dataset_id}.tweets` AS t,
        UNNEST(t.referenced_tweets) AS ref_tweet
        WHERE ref_tweet.id = @tweet_id
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("tweet_id", "STRING", tweet_id)
        ]
    )
    
    results = client.query(query, job_config=job_config).result()
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


def create_bigquery_results_table(client: bigquery.Client, project_id: str, dataset_id: str) -> None:
    """Create the results_of_CoreML table in BigQuery if it doesn't exist."""
    table_id = f"{project_id}.{dataset_id}.results_of_CoreML"
    
    schema = [
        bigquery.SchemaField("tweet_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("text", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("prediction", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("score", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("model_version", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("prediction_llm0", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("score_llm0", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("prediction_llm3", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("score_llm3", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("prediction_llm4", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("score_llm4", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("possibly_sensitive", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("normalized_text", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("rn", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("retweet_count", "INTEGER", mode="NULLABLE"),
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
    prediction: dict,
    retweet_count: int
) -> bool:
    """Insert prediction results with retweet count into BigQuery."""
    table_id = f"{project_id}.{dataset_id}.results_of_CoreML"
    
    try:
        # Check if tweet_id already exists
        tweet_id = prediction["tweet_id"]
        check_query = f"""
        SELECT tweet_id 
        FROM `{table_id}`
        WHERE tweet_id = '{tweet_id}'
        """
        
        existing_ids = set()
        try:
            check_result = client.query(check_query).result()
            existing_ids = {row["tweet_id"] for row in check_result}
        except Exception:
            pass  # Table might be empty
        
        if tweet_id in existing_ids:
            return False  # Skip duplicate
        
        # Prepare row for insertion
        created_at = prediction.get("created_at")
        if created_at is not None:
            created_at = str(created_at)
            
        updated_at = prediction.get("updated_at")
        if updated_at is not None:
            updated_at = str(updated_at)
        
        row = {
            "tweet_id": tweet_id,
            "text": prediction.get("text"),
            "prediction": prediction.get("prediction"),
            "score": float(prediction["score"]) if prediction.get("score") is not None else None,
            "model_version": prediction.get("model_version"),
            "prediction_llm0": prediction.get("prediction_llm0"),
            "score_llm0": float(prediction["score_llm0"]) if prediction.get("score_llm0") is not None else None,
            "prediction_llm3": prediction.get("prediction_llm3"),
            "score_llm3": float(prediction["score_llm3"]) if prediction.get("score_llm3") is not None else None,
            "prediction_llm4": prediction.get("prediction_llm4"),
            "score_llm4": float(prediction["score_llm4"]) if prediction.get("score_llm4") is not None else None,
            "possibly_sensitive": prediction.get("possibly_sensitive"),
            "created_at": created_at,
            "updated_at": updated_at,
            "normalized_text": prediction.get("normalized_text"),
            "rn": int(prediction["rn"]) if prediction.get("rn") is not None else None,
            "retweet_count": retweet_count,
        }
        
        # Insert row
        errors = client.insert_rows_json(table_id, [row])
        if errors:
            print(f"❌ Errors inserting row to BigQuery: {errors}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error during BigQuery insert: {e}")
        return False


def initialize_neo4j_schema(driver) -> None:
    """Create constraints and indexes for the Neo4j database."""
    print("🔧 Initializing Neo4j schema...")
    
    with driver.session() as session:
        # Create uniqueness constraint on tweet_id
        try:
            session.run(
                "CREATE CONSTRAINT tweet_id_unique IF NOT EXISTS "
                "FOR (t:Tweet) REQUIRE t.tweet_id IS UNIQUE"
            )
            print("✅ Created uniqueness constraint on Tweet.tweet_id")
        except Exception as e:
            print(f"⚠️ Constraint may already exist: {e}")
        
        # Create index on author_id
        try:
            session.run(
                "CREATE INDEX tweet_author_idx IF NOT EXISTS "
                "FOR (t:Tweet) ON (t.author_id)"
            )
            print("✅ Created index on Tweet.author_id")
        except Exception as e:
            print(f"⚠️ Index may already exist: {e}")
        
        # Create index on created_at
        try:
            session.run(
                "CREATE INDEX tweet_created_at_idx IF NOT EXISTS "
                "FOR (t:Tweet) ON (t.created_at)"
            )
            print("✅ Created index on Tweet.created_at")
        except Exception as e:
            print(f"⚠️ Index may already exist: {e}")
    
    print("✅ Schema initialization complete\n")


def load_predictions_and_retweets_to_neo4j(driver, prediction: dict, retweets: list[dict]) -> int:
    """Load prediction tweet and its retweets into Neo4j."""
    def create_nodes_and_relationships(tx, pred: dict, rts: list[dict]):
        # Create or update the original tweet node with CoreML predictions
        tx.run(
            """
            MERGE (t:Tweet {tweet_id: $tweet_id})
            SET t.text = $text,
                t.prediction = $prediction,
                t.score = $score,
                t.model_version = $model_version,
                t.prediction_llm0 = $prediction_llm0,
                t.score_llm0 = $score_llm0,
                t.prediction_llm3 = $prediction_llm3,
                t.score_llm3 = $score_llm3,
                t.prediction_llm4 = $prediction_llm4,
                t.score_llm4 = $score_llm4,
                t.possibly_sensitive = $possibly_sensitive,
                t.created_at = $created_at,
                t.updated_at = $updated_at,
                t.normalized_text = $normalized_text,
                t.rn = $rn
            """,
            tweet_id=pred["tweet_id"],
            text=pred.get("text"),
            prediction=pred.get("prediction"),
            score=float(pred["score"]) if pred.get("score") is not None else None,
            model_version=pred.get("model_version"),
            prediction_llm0=pred.get("prediction_llm0"),
            score_llm0=float(pred["score_llm0"]) if pred.get("score_llm0") is not None else None,
            prediction_llm3=pred.get("prediction_llm3"),
            score_llm3=float(pred["score_llm3"]) if pred.get("score_llm3") is not None else None,
            prediction_llm4=pred.get("prediction_llm4"),
            score_llm4=float(pred["score_llm4"]) if pred.get("score_llm4") is not None else None,
            possibly_sensitive=pred.get("possibly_sensitive"),
            created_at=str(pred.get("created_at")) if pred.get("created_at") else None,
            updated_at=str(pred.get("updated_at")) if pred.get("updated_at") else None,
            normalized_text=pred.get("normalized_text"),
            rn=int(pred["rn"]) if pred.get("rn") is not None else None,
        )

        # Create retweet nodes and relationships
        for rt in rts:
            # Create retweet node
            tx.run(
                """
                MERGE (rt:Tweet {tweet_id: $retweet_id})
                SET rt.text = $retweet_text,
                    rt.author_id = $retweeter_id,
                    rt.created_at = $retweet_created_at,
                    rt.possibly_sensitive = $possibly_sensitive
                """,
                retweet_id=rt["retweet_id"],
                retweet_text=rt.get("retweet_text"),
                retweeter_id=rt.get("retweeter_id"),
                retweet_created_at=str(rt.get("retweet_created_at")) if rt.get("retweet_created_at") else None,
                possibly_sensitive=rt.get("possibly_sensitive"),
            )
            
            # Create RETWEETED relationship
            tx.run(
                """
                MATCH (source:Tweet {tweet_id: $retweet_id})
                MATCH (target:Tweet {tweet_id: $original_tweet_id})
                MERGE (source)-[:RETWEETED]->(target)
                """,
                retweet_id=rt["retweet_id"],
                original_tweet_id=pred["tweet_id"],
            )

    inserted = 0
    failed = 0
    with driver.session() as session:
        try:
            session.execute_write(create_nodes_and_relationships, prediction, retweets)
            inserted = 1 + len(retweets)  # Original tweet + retweets
        except Exception as e:
            failed += 1
            print(f"⚠️ Failed to insert tweet {prediction.get('tweet_id')}: {e}")
    
    if failed > 0:
        print(f"⚠️ {failed} predictions failed to insert into Neo4j")
    
    return inserted


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Load CoreML predictions from BigQuery, find their retweets, and store in Neo4j and BigQuery."
    )
    parser.add_argument("--bq-project", default=os.getenv("BQ_PROJECT", "emakia"))
    parser.add_argument("--bq-dataset", default=os.getenv("BQ_DATASET", "politics2024"))
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--batches", type=int, default=5)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--init-schema", action="store_true", help="Initialize Neo4j schema (constraints and indexes)")
    args = parser.parse_args()

    bq_client = init_bigquery_client()
    driver = get_neo4j_driver()

    # Initialize Neo4j schema
    if args.init_schema:
        initialize_neo4j_schema(driver)

    # Create BigQuery results table
    create_bigquery_results_table(bq_client, args.bq_project, args.bq_dataset)

    total_predictions_processed = 0
    total_retweets_found = 0
    total_nodes_created = 0
    total_bq_inserted = 0

    try:
        for batch_num in range(args.batches):
            batch_offset = args.offset + batch_num * args.batch_size
            print(f"\n{'='*60}")
            print(f"🔄 Processing batch {batch_num + 1}/{args.batches}")
            print(f"📍 Offset: {batch_offset}, Limit: {args.batch_size}")
            print(f"{'='*60}\n")

            # Fetch predictions from CoreMLpredictions table
            predictions_batch = fetch_coreml_predictions(
                bq_client,
                args.bq_project,
                args.bq_dataset,
                limit=args.batch_size,
                offset=batch_offset,
            )
            
            if not predictions_batch:
                print("⚠️ No predictions retrieved in this batch.")
                continue

            print(f"📊 Retrieved {len(predictions_batch)} predictions from CoreMLpredictions table")

            batch_retweets = 0
            batch_bq_inserted = 0

            # Process each prediction
            for i, prediction in enumerate(predictions_batch, 1):
                tweet_id = prediction.get("tweet_id")
                
                if args.verbose:
                    print(f"\n  🔍 [{i}/{len(predictions_batch)}] Processing tweet_id: {tweet_id}")
                
                # Find retweets for this tweet
                retweets = find_retweets_for_tweet(
                    bq_client,
                    args.bq_project,
                    args.bq_dataset,
                    tweet_id,
                )
                
                retweet_count = len(retweets)
                batch_retweets += retweet_count
                
                if args.verbose:
                    print(f"    ↪ Found {retweet_count} retweet(s)")
                
                # Load to Neo4j
                nodes_created = load_predictions_and_retweets_to_neo4j(driver, prediction, retweets)
                total_nodes_created += nodes_created
                
                # Insert to BigQuery results table
                inserted = insert_results_to_bigquery(
                    bq_client,
                    args.bq_project,
                    args.bq_dataset,
                    prediction,
                    retweet_count
                )
                
                if inserted:
                    batch_bq_inserted += 1
                    total_bq_inserted += 1
                
                total_predictions_processed += 1
                total_retweets_found += retweet_count
                
                if args.verbose:
                    print(f"    ✅ Created {nodes_created} node(s) in Neo4j")
                    print(f"    ✅ Inserted to BigQuery: {inserted}")
            
            print(f"\n✅ Batch {batch_num + 1} complete:")
            print(f"   • Predictions processed: {len(predictions_batch)}")
            print(f"   • Retweets found: {batch_retweets}")
            print(f"   • Inserted to BigQuery: {batch_bq_inserted}")
    
    finally:
        driver.close()
    
    # Final summary
    print("\n" + "="*60)
    print("📊 FINAL SUMMARY")
    print("="*60)
    print(f"✅ Total predictions processed: {total_predictions_processed}")
    print(f"✅ Total retweets found: {total_retweets_found}")
    print(f"✅ Total nodes created in Neo4j: {total_nodes_created}")
    print(f"✅ Total rows inserted to BigQuery: {total_bq_inserted}")
    
    # Verify Neo4j counts
    try:
        with driver.session() as session:
            result = session.run("MATCH (t:Tweet) WHERE t.prediction IS NOT NULL RETURN count(t) as count")
            neo4j_predictions = result.single()["count"]
            print(f"✅ Neo4j tweets with predictions: {neo4j_predictions}")
            
            result = session.run("MATCH ()-[r:RETWEETED]->() RETURN count(r) as count")
            neo4j_retweets = result.single()["count"]
            print(f"✅ Neo4j RETWEETED relationships: {neo4j_retweets}")
    except Exception as e:
        print(f"⚠️ Could not verify Neo4j count: {e}")
    
    # Verify BigQuery counts
    try:
        query = f"SELECT COUNT(*) as count FROM `{args.bq_project}.{args.bq_dataset}.results_of_CoreML`"
        result = bq_client.query(query).result()
        bq_count = result.to_dataframe()['count'].values[0]
        print(f"✅ BigQuery results_of_CoreML table: {bq_count}")
    except Exception as e:
        print(f"⚠️ Could not verify BigQuery count: {e}")
    
    print("="*60)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
