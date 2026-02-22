
README content
# Emakia Tech API (backend-Google-iPhone)Flask API backend for the Emakia system. Ingests and serves ML toxicity predictions for tweets, backed by **Google BigQuery** (dataset: `emakia.politics2024`). Supports multiple model versions (llm0, llm3, llm4) in a single flow.## Features- **Store predictions**: POST ML prediction results (one or more of llm0, llm3, llm4) per tweet; duplicates are skipped.- **Tweet cascade**: GET tweets with predictions, with filters (topic, language, sensitivity, model, prediction type).- **Model comparison**: GET agreement statistics between models (llm0 vs llm3 vs llm4).- **Health**: Root and `/api/health` endpoints for status and BigQuery connectivity.## Requirements- Python 3.x- See `requirements.txt` for dependencies (Flask, `google-cloud-bigquery`, `python-dotenv`, gunicorn, streamlit optional, etc.)## Setup1. **Clone and install**   pip install -r requirements.txt   
BigQuery credentials (one of):
Streamlit (local): set bq.creds in Streamlit secrets.
File: set GOOGLE_APPLICATION_CREDENTIALS to the path of a service account JSON file.
Heroku/production: set BQ_CREDS to the full JSON string of the service account.
Env vars: set TYPE, PROJECT_ID, PRIVATE_KEY, CLIENT_EMAIL, and other standard GCP service account fields.
Environment
.env with python-dotenv is supported (e.g. for local GOOGLE_APPLICATION_CREDENTIALS or other vars).
Optional: PORT (default 5001), FLASK_DEBUG=true for debug.
Run locally
python app.py
Runs on http://0.0.0.0:5001 (or PORT). Production can use the Procfile (e.g. web: python app.py or web: gunicorn app:app).
API Endpoints
Method	Path	Description
GET	/	Health check; reports API and BigQuery status.
GET	/api/health	Detailed health + BigQuery connectivity check.
POST	/api/prediction	Store a prediction payload (see below).
GET	/api/tweet-cascade	List tweets with predictions (query params: topic, limit, lang, sensitive_filter, model, prediction_type).
GET	/api/model-comparison	Aggregated agreement stats between llm0, llm3, llm4.
POST	/api/test-prediction	Echo received JSON (for debugging payloads).
POST /api/prediction payload
{  "tweet_id": "12345",  "text": "tweet content",  "possibly_sensitive": false,  "predictions": {    "llm0": { "prediction": "harassment", "score": 0.87 },    "llm3": { "prediction": "neutral", "score": 0.92 },    "llm4": { "prediction": "harassment", "score": 0.85 }  }}
At least one of llm0, llm3, llm4 must be present. Data is written to emakia.politics2024.CoreMLpredictions; tweet cascade joins with NoRetweets-political2024 and users.
BigQuery tables (reference)
emakia.politics2024.CoreMLpredictions — stored predictions (tweet_id, text, scores per model).
emakia.politics2024.NoRetweets-political2024 — tweet content/metadata.
emakia.politics2024.users — user info (username, name, profile_image_url).
License
Internal / Emakia Tech.
