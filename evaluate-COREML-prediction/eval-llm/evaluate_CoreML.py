"""
Evaluate CoreML Predictions with LLMs

This script:
1. Fetches CoreML predictions from BigQuery (all three models: llm0, llm3, llm4)
2. Gets predictions from 6 LLMs (OpenAI, Gemini, Grok, Llama, DeepSeek, Claude)
3. Saves results to CSV for consensus analysis

Features:
- Batch processing with resume capability
- All 6 LLMs including Claude integrated
- Handles all three CoreML model predictions
- Progress tracking and error handling
"""

import csv
import os
import time
from google.cloud import bigquery
from dotenv import load_dotenv
import sys

# Add llm_wrappers folder to Python path (go up one level, then into llm_wrappers)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(parent_dir, 'llm_wrappers'))

# Load environment variables
load_dotenv()

# Import LLM wrappers
from openai_wrapper import call_openai
from gemini_wrapper import call_gemini
from grok_wrapper import call_grok
from llama_wrapper import call_llama
from deepseek_wrapper import call_deepseek
from claude_wrapper import call_claude

# Configuration
PROJECT_ID = "emakia"
DATASET_ID = "politics2024"
TABLE_ID = "CoreMLpredictions"
OUTPUT_FILE = "coreml_llm_predictions_log.csv"
BATCH_SIZE = 10  # Process in batches
RESUME_FROM_ROW = 0  # Set to continue from specific row

# BigQuery query to fetch all three model predictions
QUERY = f"""
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
    created_at
FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
ORDER BY created_at DESC
"""


def initialize_bigquery():
    """Initialize BigQuery client"""
    print("🔗 Connecting to BigQuery...")
    try:
        client = bigquery.Client(project=PROJECT_ID)
        print("   ✅ Connected")
        return client
    except Exception as e:
        print(f"   ❌ Failed to connect: {e}")
        raise


def fetch_predictions(client, limit=None):
    """Fetch CoreML predictions from BigQuery"""
    query = QUERY
    if limit:
        query += f" LIMIT {limit}"
    
    print(f"\n📊 Fetching predictions from BigQuery...")
    print(f"   Table: {PROJECT_ID}.{DATASET_ID}.{TABLE_ID}")
    
    try:
        query_job = client.query(query)
        results = list(query_job.result())
        print(f"   ✅ Fetched {len(results)} rows")
        return results
    except Exception as e:
        print(f"   ❌ Query failed: {e}")
        raise


def get_llm_predictions(texts):
    """
    Get predictions from all 6 LLMs
    
    Args:
        texts: List of text strings to classify
    
    Returns:
        Dictionary with predictions from each LLM ("Neutral" or "Harassment")
    """
    predictions = {}
    
    print(f"   🤖 Calling 6 LLMs for {len(texts)} texts...")
    
    # OpenAI
    try:
        predictions['openai'] = call_openai(texts)
        print(f"      ✅ OpenAI complete")
    except Exception as e:
        print(f"      ❌ OpenAI failed: {e}")
        predictions['openai'] = ["Harassment"] * len(texts)  # Default to toxic on error
    
    # Gemini
    try:
        predictions['gemini'] = call_gemini(texts)
        print(f"      ✅ Gemini complete")
    except Exception as e:
        print(f"      ❌ Gemini failed: {e}")
        predictions['gemini'] = ["Harassment"] * len(texts)
    
    # Grok
    try:
        predictions['grok'] = call_grok(texts)
        print(f"      ✅ Grok complete")
    except Exception as e:
        print(f"      ❌ Grok failed: {e}")
        predictions['grok'] = ["Harassment"] * len(texts)
    
    # Llama
    try:
        predictions['llama'] = call_llama(texts)
        print(f"      ✅ Llama complete")
    except Exception as e:
        print(f"      ❌ Llama failed: {e}")
        predictions['llama'] = ["Harassment"] * len(texts)
    
    # DeepSeek
    try:
        predictions['deepseek'] = call_deepseek(texts)
        print(f"      ✅ DeepSeek complete")
    except Exception as e:
        print(f"      ❌ DeepSeek failed: {e}")
        predictions['deepseek'] = ["Harassment"] * len(texts)
    
    # Claude
    try:
        predictions['claude'] = call_claude(texts)
        print(f"      ✅ Claude complete")
    except Exception as e:
        print(f"      ❌ Claude failed: {e}")
        predictions['claude'] = ["Harassment"] * len(texts)
    
    return predictions


def save_results(rows, mode='w'):
    """Save results to CSV"""
    if not rows:
        return
    
    # CSV columns including all three CoreML models and all 6 LLMs
    fieldnames = [
        'tweet_id', 'text', 
        'prediction', 'score', 'model_version',
        'prediction_llm0', 'score_llm0',
        'prediction_llm3', 'score_llm3',
        'prediction_llm4', 'score_llm4',
        'possibly_sensitive', 'created_at',
        'prediction_openai', 'prediction_gemini', 'prediction_grok',
        'prediction_llama', 'prediction_deepseek', 'prediction_claude'
    ]
    
    with open(OUTPUT_FILE, mode, newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if mode == 'w':
            writer.writeheader()
        writer.writerows(rows)
    
    print(f"   💾 Saved {len(rows)} rows to {OUTPUT_FILE}")


def process_batch(batch, batch_num, total_batches):
    """
    Process a single batch of texts
    
    Args:
        batch: List of BigQuery rows
        batch_num: Current batch number
        total_batches: Total number of batches
    
    Returns:
        List of result dictionaries ready for CSV
    """
    print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch)} rows)")
    
    # Extract texts for LLM classification
    texts = [row['text'] for row in batch]
    
    # Get predictions from all 6 LLMs
    llm_predictions = get_llm_predictions(texts)
    
    # Combine CoreML predictions with LLM predictions
    results = []
    for i, row in enumerate(batch):
        result = {
            'tweet_id': row['tweet_id'],
            'text': row['text'],
            'prediction': row['prediction'],
            'score': row['score'],
            'model_version': row['model_version'],
            'prediction_llm0': row.get('prediction_llm0'),
            'score_llm0': row.get('score_llm0'),
            'prediction_llm3': row.get('prediction_llm3'),
            'score_llm3': row.get('score_llm3'),
            'prediction_llm4': row.get('prediction_llm4'),
            'score_llm4': row.get('score_llm4'),
            'possibly_sensitive': row.get('possibly_sensitive'),
            'created_at': row['created_at'],
            'prediction_openai': llm_predictions['openai'][i],
            'prediction_gemini': llm_predictions['gemini'][i],
            'prediction_grok': llm_predictions['grok'][i],
            'prediction_llama': llm_predictions['llama'][i],
            'prediction_deepseek': llm_predictions['deepseek'][i],
            'prediction_claude': llm_predictions['claude'][i]
        }
        results.append(result)
    
    return results


def main():
    print("="*60)
    print("🔍 COREML PREDICTION EVALUATION WITH LLMs")
    print("   Including Claude in main workflow")
    print("="*60)
    
    # Check environment variables
    required_vars = [
        'OPENAI_API_KEY', 'GOOGLE_API_KEY', 'XAI_API_KEY',
        'FIREWORKS_API_KEY', 'ANTHROPIC_API_KEY'
    ]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"\n❌ Missing environment variables: {', '.join(missing)}")
        print("   Please set all required API keys")
        return
    
    # Initialize BigQuery
    try:
        client = initialize_bigquery()
    except Exception as e:
        print(f"❌ Failed to initialize BigQuery: {e}")
        return
    
    # Fetch predictions
    try:
        rows = fetch_predictions(client)
    except Exception as e:
        print(f"❌ Failed to fetch predictions: {e}")
        return
    
    if not rows:
        print("❌ No data fetched from BigQuery")
        return
    
    # Check if resuming
    start_row = RESUME_FROM_ROW
    if start_row > 0:
        print(f"\n⏭️  Resuming from row {start_row}")
        rows = rows[start_row:]
    
    # Process in batches
    total_batches = (len(rows) + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"\n📊 Processing {len(rows)} rows in {total_batches} batches of {BATCH_SIZE}")
    print(f"   Estimated time: ~{(total_batches * 2) / 60:.1f} minutes")
    
    all_results = []
    mode = 'w' if start_row == 0 else 'a'
    
    start_time = time.time()
    
    for batch_num in range(total_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(rows))
        batch = [dict(row) for row in rows[start_idx:end_idx]]
        
        try:
            results = process_batch(batch, batch_num + 1, total_batches)
            all_results.extend(results)
            
            # Save after each batch
            save_results(results, mode)
            mode = 'a'  # Append for subsequent batches
            
            # Progress summary
            elapsed = time.time() - start_time
            processed = (batch_num + 1) * BATCH_SIZE
            rate = processed / elapsed if elapsed > 0 else 0
            remaining = (len(rows) - processed) / rate if rate > 0 else 0
            
            print(f"   📈 Progress: {processed}/{len(rows)} rows | "
                  f"Elapsed: {elapsed/60:.1f}m | Remaining: ~{remaining/60:.1f}m")
            
            # Rate limiting between batches
            if batch_num < total_batches - 1:
                print(f"   ⏳ Waiting 3 seconds before next batch...")
                time.sleep(3)
                
        except Exception as e:
            print(f"   ❌ Batch {batch_num + 1} failed: {e}")
            print(f"   💡 To resume, set RESUME_FROM_ROW = {start_row + start_idx}")
            break
    
    # Final summary
    total_time = time.time() - start_time
    print("\n" + "="*60)
    print("✅ EVALUATION COMPLETE")
    print("="*60)
    print(f"\nResults:")
    print(f"   Total rows processed: {len(all_results)}")
    print(f"   Total time: {total_time/60:.1f} minutes")
    print(f"   Output file: {OUTPUT_FILE}")
    print(f"\nNext steps:")
    print(f"   Run analysis: python analyze_consensus_three_models.py")
    print("="*60)


if __name__ == "__main__":
    main()
