from fastapi import FastAPI, HTTPException
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
import os
import requests
from dotenv import load_dotenv
import praw  # Reddit API
from bs4 import BeautifulSoup  # Web scraping

# Load API keys
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")

if not api_key:
    raise ValueError("❌ OpenAI API key not found")

# Initialize OpenAI Model
llm = OpenAI(temperature=0, openai_api_key=api_key)

# Bias Detection Prompt
bias_prompt_template = PromptTemplate(
    input_variables=["content"],
    template="Analyze the following statement for political bias.\n\nStatement: {content}\nBias Analysis:"
)

# Fake News Detection Prompt
fake_news_prompt_template = PromptTemplate(
    input_variables=["content"],
    template="""
You are a fake news analyst. Determine if the following fact is fake news.

Fact: {content}

Provide your analysis and include:
- Whether the fact is likely true or false.
- References to sources that support or contradict the fact.
- The author or organization responsible for the content.

YOUR RESPONSE:
"""
)

bias_chain = bias_prompt_template | llm
fake_news_chain = fake_news_prompt_template | llm

# Initialize FastAPI App
app = FastAPI()

# Initialize Reddit API client
reddit = praw.Reddit(
    client_id=reddit_client_id,
    client_secret=reddit_client_secret,
    user_agent="fake-news-detector"
)

def get_reddit_posts(subreddit: str, limit=2):
    """Fetch 2 latest Reddit posts with complete content."""
    posts = []
    try:
        for post in reddit.subreddit(subreddit).new(limit=limit):
            content = post.selftext if post.selftext else f"[Read more]({post.url})"
            posts.append({"title": post.title, "content": content})
    except Exception as e:
        print(f"Reddit API Error: {e}")
    return posts

def get_foxnews_articles():
    articles = []

    """Fetch latest foxnews articles and verify output."""
    url = "https://www.foxnews.com"

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Adjust selector based on foxnews structure
            headlines = soup.find_all("h2", class_="article-title")  # Example class name

            if headlines:
                print("✅ Successfully retrieved foxnewsTV articles.")
                for i, headline in enumerate(headlines[:5]):  # Get top 5 articles
                    print(f"🔹 Article {i+1}: {headline.text.strip()}")
                    articles.append({"title": headline.text.strip(), "content": headline['href']})
            else:
                print("❌ No headlines found. Check the selector.")
        else:
            print(f"❌ foxnews Scraper Error: {response.status_code}")
    except Exception as e:
        print(f"🚨 foxnews Scraper Request Error: {e}")
    return articles

@app.get("/fetch_posts")
async def fetch_social_media_posts():
    """Fetch 2 Reddit & 2 Fox News articles, analyze bias, and detect fake news."""
    reddit_data = get_reddit_posts("politics", limit=2)  # Fetching fewer articles for speed
    foxnews_data = get_foxnews_articles()  # Fetching fewer Fox News articles

    if not foxnews_data:
        print("❌ No data retrieved from Fox News.")
    else:
        print(f"✅ Fox News Data: {foxnews_data}")

    # Analyze fake news and bias detection on each post
    for post in reddit_data + foxnews_data:
        post["fake_news"] = fake_news_chain.invoke({"content": post["content"]}).strip()
        post["bias_analysis"] = bias_chain.invoke({"content": post["content"]}).strip()

    return {"reddit_posts": reddit_data, "foxnews_articles": foxnews_data}
