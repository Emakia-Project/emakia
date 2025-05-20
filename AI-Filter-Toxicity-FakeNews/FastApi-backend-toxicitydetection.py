import os
import requests
import praw
from fastapi import FastAPI
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API keys
openai_api_key = os.getenv("OPENAI_API_KEY")
reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
facebook_access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")

if not openai_api_key:
    raise ValueError("Missing OpenAI API key")
if not reddit_client_id or not reddit_client_secret:
    raise ValueError("Missing Reddit API credentials")
if not facebook_access_token:
    raise ValueError("Missing Facebook API token")

# Initialize FastAPI
app = FastAPI()

# Initialize OpenAI model
llm = OpenAI(temperature=0, openai_api_key=openai_api_key)

# Toxic Comment Detection Prompt
toxic_comment_template = """Analyze the following comment and determine if it contains toxic language.
Comment: {comment}
Response (toxic / not toxic):"""
toxic_prompt = PromptTemplate(input_variables=["comment"], template=toxic_comment_template)
toxic_chain = toxic_prompt | llm

# Initialize Reddit API
reddit = praw.Reddit(client_id=reddit_client_id,
                     client_secret=reddit_client_secret,
                     user_agent="toxicity_detector")

# Function to analyze Reddit comments
@app.get("/reddit_toxicity")
def check_reddit_toxicity(subreddit: str, threshold: float = 0.5):
    subreddit = reddit.subreddit(subreddit)
    toxic_comments = []
    
    for comment in subreddit.comments(limit=10):  # Limit results for testing
        result = toxic_chain.invoke({"comment": comment.body}).strip().lower()
        if result == "toxic" and threshold >= 0.5:
            toxic_comments.append(comment.body)

    return {"subreddit": subreddit.display_name, "toxic_comments": toxic_comments}

# Function to analyze Facebook comments
@app.get("/facebook_toxicity")
def check_facebook_toxicity(post_id: str, threshold: float = 0.5):
    url = f"https://graph.facebook.com/{post_id}/comments?access_token={facebook_access_token}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return {"error": "Failed to retrieve comments"}

    comments = response.json().get("data", [])
    toxic_comments = []

    for comment in comments:
        result = toxic_chain.invoke({"comment": comment['message']}).strip().lower()
        if result == "toxic" and threshold >= 0.5:
            toxic_comments.append(comment['message'])

    return {"post_id": post_id, "toxic_comments": toxic_comments}
