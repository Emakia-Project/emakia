# Load Neo4j

Pipeline scripts to load tweet data from Google BigQuery into Neo4j, with optional classification (OpenAI or CoreML) and retweet enrichment.

## Overview

This project provides two main pipelines:

1. **load_data_into_neo4j.py** – Fetches tweets from BigQuery, optionally classifies them with OpenAI (toxicity, misinformation, bias), and loads them into Neo4j with RETWEETED relationships.

2. **process_coreml_retweets.py** – Fetches CoreML predictions from BigQuery, finds their retweets, and loads predictions plus retweet graphs into Neo4j.

Both pipelines share the same Neo4j graph structure and can run independently or together.

## Prerequisites

- Python 3.11+
- Neo4j database (local or Neo4j Aura)
- Google BigQuery project with tweet data
- For `load_data_into_neo4j.py` classify mode: OpenAI API key

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment variables

Create a `.env` file in the project root with:

| Variable | Description | Required for |
|----------|-------------|--------------|
| `NEO4J_URI` | Neo4j connection URI (e.g. `neo4j+s://xxxx.databases.neo4j.io`) | All scripts |
| `NEO4J_USER` | Neo4j username | All scripts |
| `NEO4J_PASSWORD` | Neo4j password | All scripts |
| `BQ_PROJECT` | BigQuery project ID (default: `emakia`) | Both pipelines |
| `BQ_DATASET` | BigQuery dataset (default: `politics2024`) | Both pipelines |
| `BQ_TABLE` | BigQuery tweets table (default: `tweets`) | load_data_into_neo4j |
| `BQ_CREDS` | JSON string of service account credentials | Both (or use `GOOGLE_APPLICATION_CREDENTIALS`) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON file | BigQuery fallback |
| `OPENAI_API_KEY` | OpenAI API key | load_data_into_neo4j classify mode |
| `LLM_MODEL` | OpenAI model (default: `gpt-4o-mini`) | load_data_into_neo4j classify mode |

## Scripts

### test.py

Verifies Neo4j connectivity.

```bash
python test.py
```

### load_data_into_neo4j.py

Loads tweets from BigQuery, optionally classifies them with OpenAI, and writes to Neo4j and BigQuery.

**Modes:**

- `classify` (default) – Classify tweets with OpenAI, load into Neo4j and BigQuery `results` table.
- `load-only` – Load tweets into Neo4j without classification.

**Examples:**

```bash
# Classify 5 batches of 100 tweets (default)
python load_data_into_neo4j.py

# Load only, no classification
python load_data_into_neo4j.py --mode load-only

# Custom batch size and offset
python load_data_into_neo4j.py --batch-size 50 --batches 10 --offset 0

# Initialize Neo4j schema only
python load_data_into_neo4j.py --init-schema
```

**Arguments:**

| Argument | Default | Description |
|----------|---------|-------------|
| `--bq-project` | `emakia` | BigQuery project ID |
| `--bq-dataset` | `politics2024` | BigQuery dataset |
| `--bq-table` | `tweets` | BigQuery table |
| `--batch-size` | `100` | Rows per batch |
| `--batches` | `5` | Number of batches |
| `--offset` | `500` | Starting offset |
| `--mode` | `classify` | `load-only` or `classify` |
| `--llm-model` | `gpt-4o-mini` | OpenAI model |
| `--verbose` | - | Verbose output |
| `--init-schema` | - | Create Neo4j constraints/indexes |

### process_coreml_retweets.py

Loads CoreML predictions from BigQuery, finds retweets, and writes to Neo4j and BigQuery.

**Examples:**

```bash
# Process 5 batches of 100 predictions
python process_coreml_retweets.py

# Custom batch and offset
python process_coreml_retweets.py --batch-size 50 --batches 10 --offset 0

# Initialize Neo4j schema
python process_coreml_retweets.py --init-schema --verbose
```

**Arguments:**

| Argument | Default | Description |
|----------|---------|-------------|
| `--bq-project` | `emakia` | BigQuery project ID |
| `--bq-dataset` | `politics2024` | BigQuery dataset |
| `--batch-size` | `100` | Predictions per batch |
| `--batches` | `5` | Number of batches |
| `--offset` | `0` | Starting offset |
| `--verbose` | - | Verbose output |
| `--init-schema` | - | Create Neo4j constraints/indexes |

## BigQuery Tables

| Table | Used by | Description |
|-------|---------|-------------|
| `tweets` | Both | Raw tweet data with `referenced_tweets` |
| `CoreMLpredictions` | process_coreml_retweets | CoreML toxicity predictions |
| `results` | load_data_into_neo4j | LLM classifications |
| `results_of_CoreML` | process_coreml_retweets | CoreML predictions + retweet counts |

## Neo4j Schema

- **Nodes:** `Tweet` with `tweet_id` (unique)
- **Relationships:** `RETWEETED` – retweet → original tweet
- **Indexes:** `tweet_id`, `author_id`, `created_at`

### Tweet properties (varies by pipeline)

- From `load_data_into_neo4j`: `text`, `author_id`, `created_at`, `possibly_sensitive`, `toxicity`, `misinformation`, `bias`
- From `process_coreml_retweets`: `text`, `prediction`, `score`, `model_version`, `prediction_llm0`, `score_llm0`, etc.

## Project structure

```
load-Neo4j/
├── load_data_into_neo4j.py   # LLM-classification pipeline
├── process_coreml_retweets.py # CoreML + retweets pipeline
├── test.py                   # Neo4j connection test
├── requirements.txt
├── .env                      # (create from .env.example, not committed)
└── README.md
```

## Troubleshooting

### DNS resolution failure for Neo4j

If you see `Failed to DNS resolve address` for `*.databases.neo4j.io`:

- Check internet connectivity and any VPN/DNS settings
- Confirm the Neo4j Aura instance is running and the URI is correct
- Ensure `.env` uses `NEO4J_URI=` with no spaces around `=`

### BigQuery authentication

- Use `BQ_CREDS` (JSON string) or `GOOGLE_APPLICATION_CREDENTIALS` (path to JSON file)
- For local development, `gcloud auth application-default login` can be used
