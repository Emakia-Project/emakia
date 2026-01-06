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
# Add this function after init_bigquery_client()


# Initialize client and table on startup
client = init_bigquery_client()


# Your existing routes remain the same below...
# @app.route("/")
# def index():
#     ...
#client = init_bigquery_client()

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
    
    Expected JSON payload:
    {
        "tweet_id": "12345",
        "text": "example tweet",
        "prediction": "harassment",
        "score": 0.87,
        "model_version": "CoreML_v1"
    }
    """
    if client is None:
        return jsonify({"error": "BigQuery client not initialized"}), 500

    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "No JSON payload provided"}), 400

        # Validate required fields
        required_fields = ["tweet_id", "text", "prediction", "score"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        # Prepare data for insertion
        table_id = "emakia.politics2024.CoreMLpredictions"
        
        rows_to_insert = [
            {
                "tweet_id": str(data.get("tweet_id")),
                "text": str(data.get("text")),
                "prediction": str(data.get("prediction")),
                "score": float(data.get("score")),
                "model_version": str(data.get("model_version", "unknown")),
                "created_at": datetime.utcnow().isoformat()
            }
        ]

        # Insert into BigQuery
        errors = client.insert_rows_json(table_id, rows_to_insert)
        
        if errors == []:
            return jsonify({
                "status": "success",
                "message": "Prediction stored successfully",
                "tweet_id": data.get("tweet_id")
            }), 200
        else:
            print(f"❌ BigQuery insert errors: {errors}")
            return jsonify({
                "status": "error",
                "message": "Failed to insert data",
                "details": errors
            }), 500

    except ValueError as e:
        return jsonify({"error": f"Invalid data type: {str(e)}"}), 400
    except Exception as e:
        print(f"❌ Prediction insert error: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

#@app.route("/api/tweet-cascade", methods=["GET"])

@app.route("/api/tweet-cascade", methods=["GET"])
def get_tweet_cascade():
    """
    Retrieve tweets with optional filtering
    
    Query parameters:
    - topic: Filter tweets containing this text (case-insensitive)
    - limit: Maximum number of tweets to return (default: 50, max: 1000)
    - sensitive_filter: Filter by sensitivity ("true", "false", or omit for all)
    """
    if client is None:
        return jsonify({"error": "BigQuery client not initialized"}), 500

    # Parse query parameters
    topic = request.args.get("topic")
    limit = min(request.args.get("limit", default=50, type=int), 1000)  # Cap at 1000
    sensitive_filter = request.args.get("sensitive_filter")

    try:
        # Build dynamic filters
        filters = []
        
        if topic:
            # Escape single quotes and use parameterized query for safety
            topic_escaped = topic.replace("'", "\\'").lower()
            filters.append(f"LOWER(t.text) LIKE '%{topic_escaped}%'")
        
        if sensitive_filter == "true":
            filters.append("t.possibly_sensitive = TRUE")
        elif sensitive_filter == "false":
            filters.append("t.possibly_sensitive = FALSE")

        # Build query with enriched user data
        query = """
            SELECT
                t.id AS tweet_id,
                t.text AS content,
                t.author_id,
                t.possibly_sensitive,
                t.created_at,
                u.username,
                u.name,
                u.profile_image_url
            FROM `emakia.politics2024.tweets` AS t
            LEFT JOIN `emakia.politics2024.users` AS u
                ON t.author_id = u.id
        """

        # Add WHERE clause if filters exist
        if filters:
            query += " WHERE " + " AND ".join(filters)
        
        query += f" ORDER BY t.created_at DESC LIMIT {limit}"

        # Execute query
        print(f"📊 Executing query with filters: {filters if filters else 'None'}")
        print(f"🔍 Full query: {query}")  # Debug: print the full query
        query_job = client.query(query)
        results = query_job.result()

        # Format response with debug info
        tweets = []
        for idx, row in enumerate(results):
            tweet_data = {
                "tweet_id": row.tweet_id,
                "content": row.content,
                "author_id": row.author_id,
                "possibly_sensitive": row.possibly_sensitive,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "username": row.username,
                "name": row.name,
                "profile_image_url": row.profile_image_url
            }
            tweets.append(tweet_data)
            
            # Debug: Print first 3 tweets to see if user data exists
            if idx < 3:
                print(f"Tweet {idx + 1}:")
                print(f"  author_id: {row.author_id}")
                print(f"  username: {row.username if row.username else '❌ NULL'}")
                print(f"  name: {row.name if row.name else '❌ NULL'}")
                print(f"  profile_image_url: {row.profile_image_url if row.profile_image_url else '❌ NULL'}")

        # 🔍 Check if ANY tweets have user data
        tweets_with_user_data = sum(1 for t in tweets if t['username'] is not None)
        print(f"📊 Total tweets: {len(tweets)}, Tweets with user data: {tweets_with_user_data}")

        return jsonify({
            "count": len(tweets),
            "data": tweets,  # ✅ Changed from "tweets" to "data" to match your Swift code
            "filters_applied": {
                "topic": topic,
                "sensitive_filter": sensitive_filter,
                "limit": limit
            }
        }), 200

    except Exception as e:
        print(f"❌ Query error: {e}")
        import traceback
        traceback.print_exc()  # Print full error traceback
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
            # Try a simple query to verify connection
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
