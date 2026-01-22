from flask import Flask, request, jsonify
from google.cloud import bigquery
from google.oauth2 import service_account
from dotenv import load_dotenv
import json
import os
from datetime import datetime

# Local dev support
try:
    import streamlit as st
except ImportError:
    st = None

load_dotenv()
app = Flask(__name__)

# --- Credential Loader ---
def load_bq_credentials():
    """
    Load BigQuery credentials from multiple sources in priority order:
    1. Streamlit secrets (for local Streamlit development)
    2. GOOGLE_APPLICATION_CREDENTIALS file path
    3. BQ_CREDS environment variable (Heroku/production)
    4. Individual environment variables (TYPE, PROJECT_ID, PRIVATE_KEY, etc.)
    """
    try:
        # ✅ Method 1: Streamlit secrets
        if st and "bq" in st.secrets and "creds" in st.secrets["bq"]:
            creds_dict = dict(st.secrets["bq"]["creds"])
            if "\\n" in creds_dict.get("private_key", ""):
                creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            print("🟢 Using Streamlit secrets for BigQuery.")
            return creds_dict
        
        # ✅ Method 2: GOOGLE_APPLICATION_CREDENTIALS file path
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if credentials_path and os.path.exists(credentials_path):
            with open(credentials_path, 'r') as f:
                creds_dict = json.load(f)
                # Ensure proper newline formatting in private key
                if "\\n" in creds_dict.get("private_key", ""):
                    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
                print(f"🟢 Using credentials from file: {credentials_path}")
                return creds_dict
        
        # ✅ Method 3: BQ_CREDS environment variable (Heroku)
        raw_creds = os.environ.get("BQ_CREDS")
        if raw_creds:
            creds_dict = json.loads(raw_creds)
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            print("🟡 Using BQ_CREDS environment variable for BigQuery.")
            return creds_dict
        
        # ✅ Method 4: Build from individual environment variables
        if os.environ.get("TYPE") and os.environ.get("PROJECT_ID") and os.environ.get("PRIVATE_KEY"):
            creds_dict = {
                "type": os.environ.get("TYPE"),
                "project_id": os.environ.get("PROJECT_ID"),
                "private_key_id": os.environ.get("PRIVATE_KEY_ID"),
                "private_key": os.environ.get("PRIVATE_KEY", "").replace("\\n", "\n"),
                "client_email": os.environ.get("CLIENT_EMAIL"),
                "client_id": os.environ.get("CLIENT_ID"),
                "auth_uri": os.environ.get("AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
                "token_uri": os.environ.get("TOKEN_URI", "https://oauth2.googleapis.com/token"),
                "auth_provider_x509_cert_url": os.environ.get("AUTH_PROVIDER_X509_CERT_URL", 
                                                                "https://www.googleapis.com/oauth2/v1/certs"),
                "client_x509_cert_url": os.environ.get("CLIENT_X509_CERT_URL"),
                "universe_domain": os.environ.get("UNIVERSE_DOMAIN", "googleapis.com")
            }
            print("🟡 Using individual environment variables for BigQuery.")
            return creds_dict

        raise RuntimeError("❌ No valid BigQuery credentials found in any source.")
    
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error in credentials: {e}")
        return None
    except Exception as e:
        print(f"❌ Failed to load BigQuery credentials: {e}")
        return None

# --- Client Initializer ---
def init_bigquery_client():
    """Initialize BigQuery client with loaded credentials"""
    creds_dict = load_bq_credentials()
    if creds_dict:
        try:
            creds = service_account.Credentials.from_service_account_info(creds_dict)
            project_id = creds_dict.get("project_id")
            client = bigquery.Client(credentials=creds, project=project_id)
            print(f"✅ BigQuery client initialized successfully for project: {project_id}")
            return client
        except Exception as e:
            print(f"❌ Failed to initialize BigQuery client: {e}")
            return None
    else:
        print("❌ Cannot initialize BigQuery client - no credentials available")
        return None

# Initialize client on startup
client = init_bigquery_client()

# --- Routes ---
@app.route("/")
def index():
    """Health check endpoint"""
    if client:
        return jsonify({
            "status": "running",
            "message": "Emakia Tech API is running 🚀",
            "bigquery": "connected"
        }), 200
    else:
        return jsonify({
            "status": "running",
            "message": "Emakia Tech API is running 🚀",
            "bigquery": "disconnected",
            "error": "BigQuery client not initialized"
        }), 503


@app.route("/api/prediction", methods=["POST"])
def receive_prediction():
    """
    Receive and store ML prediction results in BigQuery
    Supports multiple model versions (llm0, llm3, llm4) in a single request
    
    Expected JSON payload:
    {
        "tweet_id": "12345",
        "text": "example tweet",
        "predictions": {
            "llm0": {"prediction": "harassment", "score": 0.87},
            "llm3": {"prediction": "neutral", "score": 0.92},
            "llm4": {"prediction": "harassment", "score": 0.85}
        }
    }
    """
    if client is None:
        return jsonify({"error": "BigQuery client not initialized"}), 500

    try:
        # Get and log raw request
        raw_data = request.get_data(as_text=True)
        print("=" * 80)
        print("🔍 RAW REQUEST:")
        print(raw_data[:500])  # First 500 chars
        print("=" * 80)
        
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "No JSON payload provided"}), 400

        print(f"✅ Parsed JSON successfully")
        print(f"   Keys received: {list(data.keys())}")
        
        # Validate required fields
        required_fields = ["tweet_id", "text", "predictions"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            print(f"❌ {error_msg}")
            return jsonify({
                "error": error_msg,
                "received_keys": list(data.keys())
            }), 400

        # Extract and validate predictions
        predictions = data.get("predictions", {})
        if not isinstance(predictions, dict):
            return jsonify({"error": f"predictions must be a dict, got {type(predictions).__name__}"}), 400
        
        if not predictions:
            return jsonify({"error": "predictions dict is empty"}), 400
        
        print(f"   Predictions keys: {list(predictions.keys())}")

        # Prepare base row data
        table_id = "emakia.politics2024.CoreMLpredictions"
        tweet_id = str(data.get("tweet_id"))
        tweet_text = str(data.get("text"))
        
        print(f"📝 Processing tweet_id: {tweet_id}")
        print(f"   Text length: {len(tweet_text)} chars")
        
        # Check if tweet already exists
        check_query = f"""
            SELECT COUNT(*) as count 
            FROM `{table_id}` 
            WHERE tweet_id = '{tweet_id}'
        """
        
        try:
            result = list(client.query(check_query).result())
            if result[0].count > 0:
                print(f"⚠️ Tweet {tweet_id} already exists, skipping...")
                return jsonify({
                    "status": "skipped",
                    "message": "Tweet already exists in database",
                    "tweet_id": tweet_id
                }), 200
        except Exception as e:
            print(f"⚠️ Error checking for duplicates: {e}")
        
        # Build row data with REQUIRED fields
        row_data = {
            "tweet_id": tweet_id,
            "text": tweet_text,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Process each model's predictions
        models_added = []
        primary_prediction_set = False
        
        # Process llm0
        if "llm0" in predictions and isinstance(predictions["llm0"], dict):
            llm0_pred = str(predictions["llm0"].get("prediction", ""))
            llm0_score = float(predictions["llm0"].get("score", 0.0))
            
            if llm0_pred:  # Only add if prediction exists
                row_data["prediction_llm0"] = llm0_pred
                row_data["score_llm0"] = llm0_score
                models_added.append("llm0")
                print(f"   ✅ llm0: {llm0_pred} ({llm0_score:.3f})")
                
                # Set as primary if first
                if not primary_prediction_set:
                    row_data["prediction"] = llm0_pred
                    row_data["score"] = llm0_score
                    row_data["model_version"] = "ToxicityTextClassifier0"
                    primary_prediction_set = True
        
        # Process llm3
        if "llm3" in predictions and isinstance(predictions["llm3"], dict):
            llm3_pred = str(predictions["llm3"].get("prediction", ""))
            llm3_score = float(predictions["llm3"].get("score", 0.0))
            
            if llm3_pred:
                row_data["prediction_llm3"] = llm3_pred
                row_data["score_llm3"] = llm3_score
                models_added.append("llm3")
                print(f"   ✅ llm3: {llm3_pred} ({llm3_score:.3f})")
                
                if not primary_prediction_set:
                    row_data["prediction"] = llm3_pred
                    row_data["score"] = llm3_score
                    row_data["model_version"] = "ToxicityTextClassifier3"
                    primary_prediction_set = True
        
        # Process llm4
        if "llm4" in predictions and isinstance(predictions["llm4"], dict):
            llm4_pred = str(predictions["llm4"].get("prediction", ""))
            llm4_score = float(predictions["llm4"].get("score", 0.0))
            
            if llm4_pred:
                row_data["prediction_llm4"] = llm4_pred
                row_data["score_llm4"] = llm4_score
                models_added.append("llm4")
                print(f"   ✅ llm4: {llm4_pred} ({llm4_score:.3f})")
                
                if not primary_prediction_set:
                    row_data["prediction"] = llm4_pred
                    row_data["score"] = llm4_score
                    row_data["model_version"] = "ToxicityTextClassifier4"
                    primary_prediction_set = True
        
        # Validate we got at least one model
        if not models_added:
            return jsonify({"error": "No valid model predictions found in payload"}), 400
        
        # Verify REQUIRED fields are present
        if "prediction" not in row_data or "score" not in row_data:
            return jsonify({"error": "Failed to set required prediction/score fields"}), 500
        
        print(f"   📊 Primary: {row_data['prediction']} ({row_data['score']:.3f})")
        print(f"   🎯 Models stored: {', '.join(models_added)}")
        
        # Insert into BigQuery
        rows_to_insert = [row_data]
        errors = client.insert_rows_json(table_id, rows_to_insert)
        
        if errors == []:
            print(f"✅ Successfully inserted prediction for tweet {tweet_id}")
            return jsonify({
                "status": "success",
                "message": "Prediction stored successfully",
                "tweet_id": tweet_id,
                "models_stored": models_added,
                "primary_prediction": row_data["prediction"]
            }), 200
        else:
            print(f"❌ BigQuery insert errors: {errors}")
            return jsonify({
                "status": "error",
                "message": "Failed to insert into BigQuery",
                "details": errors
            }), 500

    except ValueError as e:
        print(f"❌ ValueError: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Invalid data type: {str(e)}"}), 400
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route("/api/tweet-cascade", methods=["GET"])
def get_tweet_cascade():
    """
    Retrieve tweets with predictions from all models
    
    Query parameters:
    - topic: Filter tweets containing this text (case-insensitive)
    - limit: Maximum number of tweets to return (default: 50, max: 1000)
    - sensitive_filter: Filter by sensitivity ("true", "false", or omit for all)
    - lang: Filter by language (default: "en" for English only)
    - model: Filter by specific model prediction (llm0, llm3, llm4)
    - prediction_type: Filter by prediction type (harassment, neutral, etc.)
    """
    if client is None:
        return jsonify({"error": "BigQuery client not initialized"}), 500

    # Parse query parameters
    topic = request.args.get("topic", "").strip()
    limit = min(request.args.get("limit", default=50, type=int), 1000)
    sensitive_filter = request.args.get("sensitive_filter")
    lang = request.args.get("lang", "en")
    model_filter = request.args.get("model")
    prediction_type = request.args.get("prediction_type")

    try:
        # Build dynamic filters
        filters = []
        
        if lang:
            filters.append(f"t.lang = '{lang}'")
        
        if topic:
            topic_escaped = topic.replace("'", "\\'").lower()
            filters.append(f"LOWER(t.text) LIKE '%{topic_escaped}%'")
        
        if sensitive_filter == "true":
            filters.append("t.possibly_sensitive = TRUE")
        elif sensitive_filter == "false":
            filters.append("t.possibly_sensitive = FALSE")
        
        # Filter by model prediction
        if model_filter and prediction_type:
            model_column = f"p.prediction_{model_filter}"
            filters.append(f"{model_column} = '{prediction_type}'")

        # ✅ Build query with predictions from all models
        query = """
            SELECT DISTINCT
                t.id AS tweet_id,
                t.text AS content,
                t.author_id,
                t.possibly_sensitive,
                t.created_at,
                t.lang,
                u.username,
                u.name,
                u.profile_image_url,
                p.prediction_llm0,
                p.score_llm0,
                p.prediction_llm3,
                p.score_llm3,
                p.prediction_llm4,
                p.score_llm4
            FROM `emakia.politics2024.tweets` AS t
            LEFT JOIN `emakia.politics2024.users` AS u
                ON t.author_id = u.id
            LEFT JOIN `emakia.politics2024.CoreMLpredictions` AS p
                ON t.id = p.tweet_id
        """

        if filters:
            query += " WHERE " + " AND ".join(filters)
        
        query += f" ORDER BY t.created_at DESC LIMIT {limit}"

        print(f"📊 Executing query (limit: {limit}, lang: {lang})")
        query_job = client.query(query)
        results = query_job.result()

        tweets = []
        for row in results:
            tweet_data = {
                "tweet_id": row.tweet_id,
                "content": row.content,
                "author_id": row.author_id,
                "possibly_sensitive": row.possibly_sensitive,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "username": row.username,
                "name": row.name,
                "profile_image_url": row.profile_image_url,
                "predictions": {}
            }
            
            # Add model predictions if available
            if row.prediction_llm0:
                tweet_data["predictions"]["llm0"] = {
                    "prediction": row.prediction_llm0,
                    "score": row.score_llm0
                }
            if row.prediction_llm3:
                tweet_data["predictions"]["llm3"] = {
                    "prediction": row.prediction_llm3,
                    "score": row.score_llm3
                }
            if row.prediction_llm4:
                tweet_data["predictions"]["llm4"] = {
                    "prediction": row.prediction_llm4,
                    "score": row.score_llm4
                }
            
            tweets.append(tweet_data)

        print(f"📊 Found {len(tweets)} tweets")

        return jsonify({
            "count": len(tweets),
            "data": tweets,
            "filters_applied": {
                "topic": topic if topic else "all",
                "sensitive_filter": sensitive_filter,
                "limit": limit,
                "lang": lang,
                "model": model_filter,
                "prediction_type": prediction_type
            }
        }), 200

    except Exception as e:
        print(f"❌ Query error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Failed to fetch tweets",
            "details": str(e)
        }), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Detailed health check endpoint"""
    health_status = {
        "api": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "bigquery": "disconnected"
    }
    
    if client:
        try:
            query = "SELECT 1 as test"
            result = list(client.query(query).result())
            health_status["bigquery"] = "connected"
            health_status["bigquery_project"] = client.project
            return jsonify(health_status), 200
        except Exception as e:
            health_status["bigquery"] = "error"
            health_status["bigquery_error"] = str(e)
            return jsonify(health_status), 503
    
    return jsonify(health_status), 503


@app.route("/api/test-prediction", methods=["POST"])
def test_prediction():
    """
    Test endpoint that echoes back what it receives
    Use this to debug payload issues
    """
    try:
        raw_data = request.get_data(as_text=True)
        
        print("=" * 80)
        print("TEST PREDICTION ENDPOINT")
        print("=" * 80)
        print(f"Content-Type: {request.content_type}")
        print(f"Content-Length: {request.content_length}")
        print(f"\nRaw Data:")
        print(raw_data)
        print("=" * 80)
        
        data = request.get_json(force=True)
        
        response = {
            "received": {
                "content_type": request.content_type,
                "data": data,
                "keys": list(data.keys()) if data else [],
                "predictions_present": "predictions" in data if data else False,
                "predictions_type": str(type(data.get("predictions"))) if data else None,
                "predictions_value": data.get("predictions") if data else None
            }
        }
        
        print(f"\nParsed JSON Response:")
        print(json.dumps(response, indent=2))
        print("=" * 80)
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ Test endpoint error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route("/api/model-comparison", methods=["GET"])
def model_comparison():
    """
    Compare predictions across different models
    Returns statistics on agreement/disagreement between models
    """
    if client is None:
        return jsonify({"error": "BigQuery client not initialized"}), 500
    
    try:
        limit = min(request.args.get("limit", default=100, type=int), 10000)
        
        query = f"""
            SELECT 
                COUNT(*) as total_predictions,
                SUM(CASE WHEN prediction_llm0 = prediction_llm3 AND prediction_llm3 = prediction_llm4 THEN 1 ELSE 0 END) as all_agree,
                SUM(CASE WHEN prediction_llm0 = prediction_llm3 THEN 1 ELSE 0 END) as llm0_llm3_agree,
                SUM(CASE WHEN prediction_llm0 = prediction_llm4 THEN 1 ELSE 0 END) as llm0_llm4_agree,
                SUM(CASE WHEN prediction_llm3 = prediction_llm4 THEN 1 ELSE 0 END) as llm3_llm4_agree
            FROM `emakia.politics2024.CoreMLpredictions`
            WHERE prediction_llm0 IS NOT NULL 
                AND prediction_llm3 IS NOT NULL 
                AND prediction_llm4 IS NOT NULL
            LIMIT {limit}
        """
        
        query_job = client.query(query)
        results = list(query_job.result())
        
        if results:
            row = results[0]
            total = row.total_predictions
            
            return jsonify({
                "total_predictions": total,
                "all_models_agree": row.all_agree,
                "all_models_agree_pct": round(row.all_agree / total * 100, 2) if total > 0 else 0,
                "llm0_llm3_agree": row.llm0_llm3_agree,
                "llm0_llm3_agree_pct": round(row.llm0_llm3_agree / total * 100, 2) if total > 0 else 0,
                "llm0_llm4_agree": row.llm0_llm4_agree,
                "llm0_llm4_agree_pct": round(row.llm0_llm4_agree / total * 100, 2) if total > 0 else 0,
                "llm3_llm4_agree": row.llm3_llm4_agree,
                "llm3_llm4_agree_pct": round(row.llm3_llm4_agree / total * 100, 2) if total > 0 else 0
            }), 200
        else:
            return jsonify({"error": "No data found"}), 404
            
    except Exception as e:
        print(f"❌ Model comparison error: {e}")
        return jsonify({"error": str(e)}), 500


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    
    print(f"🚀 Starting Flask app on port {port}")
    print(f"🔧 Debug mode: {debug}")
    
    app.run(host="0.0.0.0", port=port, debug=debug)
