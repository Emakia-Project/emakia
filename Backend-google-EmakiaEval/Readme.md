Here is a cleaned-up, well-structured, and more professional version of the README.md content:

```markdown
# Emakia Tech API (Backend)

Flask-based backend API for the **Emakia** system.

This service ingests machine learning toxicity predictions for tweets (mainly political content from 2024) and serves them efficiently.  
Data is stored in **Google BigQuery** (dataset: `emakia.politics2024`).

Supports multiple model versions in parallel: **llm0**, **llm3**, **llm4**.

## Features

- **Store predictions**  
  POST toxicity predictions for one or more models per tweet (duplicates are skipped)

- **Tweet cascade / filtered listing**  
  GET tweets enriched with predictions, supporting filters:  
  topic • language • sensitivity • model version • prediction type

- **Model comparison**  
  GET agreement statistics and confusion metrics between llm0, llm3, and llm4

- **Health checks**  
  Simple `/` and detailed `/api/health` endpoints (includes BigQuery connectivity test)

## Tech Stack

- Python 3.9+
- Flask
- google-cloud-bigquery
- python-dotenv
- gunicorn (production)
- Optional: Streamlit (for local development / debugging)

See [`requirements.txt`](./requirements.txt) for full dependencies.

## Setup

### 1. Clone & install dependencies

```bash
git clone <repository-url>
cd <repository-folder>
pip install -r requirements.txt
```

### 2. Authentication – Google BigQuery

Choose **one** of the following methods:

**A. Local development (recommended)**  
Set environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-service-account.json"
```

**B. Streamlit / local secrets**  
Add `bq.creds` key in `.streamlit/secrets.toml` with the full JSON content.

**C. Heroku / production**  
Set environment variable `BQ_CREDS` = full JSON string of the service account key.

**D. Manual env vars** (less common)  
```bash
export TYPE="service_account"
export PROJECT_ID="emakia"
export PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
export CLIENT_EMAIL="..."
# + other standard GCP fields
```

### 3. Optional environment variables

```bash
# .env file (loaded automatically via python-dotenv)
PORT=5001
FLASK_DEBUG=true              # enables debug mode + auto-reload
```

### 4. Run locally

```bash
python app.py
# or with gunicorn (more production-like)
gunicorn --bind 0.0.0.0:5001 app:app
```

The API will be available at:  
http://localhost:5001 (or your chosen PORT)

## API Endpoints

| Method | Path                        | Description                                      |
|--------|-----------------------------|--------------------------------------------------|
| `GET`  | `/`                         | Basic health check (API + BigQuery status)       |
| `GET`  | `/api/health`               | Detailed health info + BigQuery connectivity     |
| `POST` | `/api/prediction`           | Store ML prediction(s) for a tweet               |
| `GET`  | `/api/tweet-cascade`        | List tweets + predictions (with query filters)   |
| `GET`  | `/api/model-comparison`     | Model agreement statistics (llm0 vs llm3 vs llm4)|
| `POST` | `/api/test-prediction`      | Echo received JSON payload (debugging)           |

### POST /api/prediction – Payload Example

```json
{
  "tweet_id": "1893746281945620482",
  "text": "This is an example tweet content",
  "possibly_sensitive": false,
  "predictions": {
    "llm0": {
      "prediction": "harassment",
      "score": 0.87
    },
    "llm3": {
      "prediction": "neutral",
      "score": 0.92
    },
    "llm4": {
      "prediction": "harassment",
      "score": 0.854
    }
  }
}
```

- At least **one** of `llm0`, `llm3`, `llm4` must be present  
- Table written to: `emakia.politics2024.CoreMLpredictions`

## BigQuery Tables (Reference)

| Table name                              | Purpose                              |
|-----------------------------------------|--------------------------------------|
| `emakia.politics2024.CoreMLpredictions` | Stored model predictions & scores    |
| `emakia.politics2024.NoRetweets-political2024` | Original tweet content & metadata |
| `emakia.politics2024.users`             | User information (username, name, profile image, etc.) |

`/api/tweet-cascade` performs joins across these tables.

## License

**Internal / Emakia Tech** – All rights reserved.

Not for public redistribution or commercial use outside Emakia projects.
```

This version improves:

- readability with consistent markdown
- clearer setup instructions
- proper table formatting
- better organization of sections
- realistic payload example
- explicit notes about requirements & limitations

Feel free to adjust any company-specific details or add badges, CI status, etc. if needed!
