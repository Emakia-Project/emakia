import os
import uuid
import time
import requests
import streamlit as st
from dotenv import load_dotenv
import praw
import google.generativeai as genai

from google.adk.sessions import InMemorySessionService
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.genai import types

from google.oauth2 import service_account
from google.cloud import bigquery


from inputs.reddit_scraper import get_reddit_posts
from inputs.maxnews_scraper import get_maxnews_articles
from inputs.bigquery_loader import get_tweets_from_bigquery

import json
import os


import db_dtypes  # 👈 Ensures custom BigQuery types are handled






# --- Load environment variables ---
load_dotenv()




# Access your service account credentials from secrets.toml
bq_creds_dict = dict(st.secrets["bq"]["creds"])

# Fix line breaks in the private key if needed
if "\\n" in bq_creds_dict["private_key"]:
    bq_creds_dict["private_key"] = bq_creds_dict["private_key"].replace("\\n", "\n")

# Create credentials from the in-memory dictionary
creds = service_account.Credentials.from_service_account_info(bq_creds_dict)

# Initialize BigQuery client
client = bigquery.Client(credentials=creds, project=creds.project_id)



# Load credentials from secrets
bq_creds_dict = dict(st.secrets["bq"]["creds"])
print("bq_creds_dict-private_key")
print(bq_creds_dict["private_key"])
# Fix the private key line breaks, if they’ve been escaped
if "\\n" in bq_creds_dict["private_key"]:
    bq_creds_dict["private_key"] = bq_creds_dict["private_key"].replace("\\n", "\n")




# --- Constants ---
APP_NAME = "toxicity_misinformation_analysis"
USER_ID = f"user_{uuid.uuid4()}"
SESSION_ID = f"session_{uuid.uuid4()}"
GEMINI_MODEL = "gemini-2.0-flash"
debug_logs = []

# --- Configure Gemini API ---
try:

    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

    genai.configure(api_key=GOOGLE_API_KEY)
except KeyError:
    st.error("Missing GOOGLE_API_KEY in environment.")
    st.stop()

# --- Define Agents ---
toxicity_agent = LlmAgent(
    name="ToxicityAnalyst",
    model=GEMINI_MODEL,
    instruction="Classify the following statement as 'toxic' or 'non-toxic'.",
    description="Detects toxic language.",
    output_key="toxicity_analysis"
)

bias_agent = LlmAgent(
    name="BiasAnalyst",
    model=GEMINI_MODEL,
    instruction="Classify the statement as 'biased' or 'neutral'. Explain why.",
    description="Assesses bias.",
    output_key="bias_analysis"
)

misinfo_agent = LlmAgent(
    name="MisinformationAnalyst",
    model=GEMINI_MODEL,
    instruction="Determine if this statement contains 'misinformation' or is 'accurate'. Include rationale.",
    description="Detects misinformation.",
    output_key="misinformation_analysis"
)

parallel_agent = ParallelAgent(
    name="ParallelAnalysisAgent",
    sub_agents=[toxicity_agent, bias_agent, misinfo_agent]
)

def write_debug_logs():
    try:
        with open("debug_logs.txt", "w") as file:
            for log in debug_logs:
                file.write(log + "\n")
    except Exception as e:
        print(f"Error writing debug logs: {e}")

def run_analysis(items):
    session_service = InMemorySessionService()
    session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    results = []

    for item in items:
        if "content" not in item:
            debug_logs.append(f"⚠️ Skipping item with missing content: {item}")
            continue

        try:
            runner = Runner(agent=parallel_agent, app_name=APP_NAME, session_service=session_service)
            content = types.Content(role="user", parts=[types.Part(text=item["content"])])
            events = runner.run(user_id=USER_ID, session_id=session.id, new_message=content)

            result = {
                "title": item.get("title", "Untitled"),
                "content": item["content"],
                "toxicity": "No result",
                "bias": "No result",
                "misinformation": "No result"
            }

            for event in events:
                if event and event.content.parts:
                    output = event.content.parts[0].text
                    if "toxic" in output.lower():
                        result["toxicity"] = output
                    elif "bias" in output.lower():
                        result["bias"] = output
                    elif "misinformation" in output.lower() or "accurate" in output.lower():
                        result["misinformation"] = output

            results.append(result)
        except Exception as e:
            debug_logs.append(f"Runner error: {e}")
            st.error(f"🔥 Error during analysis: {e}")

    return results

# --- Streamlit UI ---
st.title("🧠 Multi-Agent Toxicity & Misinformation Analyzer")

if st.button("Analyze Reddit & Maxnews Posts"):
    with st.spinner("Fetching and analyzing posts..."):
        posts = get_reddit_posts("politics", limit=3)
        posts += get_maxnews_articles()
        results = run_analysis(posts)

    if results:
        st.header("📰 Analysis Results")
        for post in results:
            st.subheader(post["title"])
            st.write(f"**Content:** {post['content']}")
            st.markdown(f"🧪 **Toxicity:** `{post['toxicity']}`")
            st.markdown(f"🎯 **Bias:** `{post['bias']}`")
            st.markdown(f"🚫 **Misinformation:** `{post['misinformation']}`")
            st.write("---")
    else:
        st.warning("❌ No articles available for analysis.")

if st.button("Analyze Tweets from BigQuery"):
    with st.spinner("Fetching tweets from BigQuery..."):
        tweets = get_tweets_from_bigquery()
        results = run_analysis(tweets)

    if results:
        st.header("🐦 Tweet Analysis Results")
        for tweet in results:
            st.subheader(tweet["title"])
            st.write(f"**Content:** {tweet['content']}")
            st.markdown(f"🧪 **Toxicity:** `{tweet['toxicity']}`")
            st.markdown(f"🎯 **Bias:** `{tweet['bias']}`")
            st.markdown(f"🚫 **Misinformation:** `{tweet['misinformation']}`")
            st.write("---")
    else:
        st.warning("❌ No tweets could be analyzed.")