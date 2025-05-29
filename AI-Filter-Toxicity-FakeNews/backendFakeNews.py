from fastapi import FastAPI, HTTPException
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
import os
import requests
import time
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


def get_maxnews_articles():
    main_url = 'https://www.newsmax.com'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }

    response = requests.get(main_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.findAll('div', class_='nmNewsfrontHead')

    parsed_articles = []  # Store extracted data
    for index, article in enumerate(articles[:3]):  # Limit to 3 articles
        a_tag = article.find('a')
        if not a_tag:
            continue

        title = a_tag.text.strip()
        link = a_tag['href']
        if link.startswith('/'):
            link = f'{main_url}{link}'

        try:
            article_response = requests.get(link, headers=headers)
            article_soup = BeautifulSoup(article_response.content, 'html.parser')
            content_div = article_soup.find('div', attrs={'id': 'mainArticleDiv'})
            content = content_div.get_text(strip=True, separator='\n') if content_div else "No content found."

            parsed_articles.append({"title": title, "link": link, "content": content})
        except Exception as e:
            print(f'Error fetching article: {e}')
        
        time.sleep(1)  # Wait before fetching next article
    
    return parsed_articles  # Return structured data
@app.get("/fetch_posts")
async def fetch_social_media_posts():
    """Fetch 2 Reddit & 2 max News articles, analyze bias, and detect fake news."""
    reddit_data = get_reddit_posts("politics", limit=2)  # Fetching fewer articles for speed
    maxnews_data = get_maxnews_articles()  # Fetching fewer max News articles

    if not maxnews_data:
        print("❌ No data retrieved from max News.")
    else:
        print(f"✅ max News Data: {maxnews_data}")

    
    # Analyze fake news and bias detection on each post
    for post in reddit_data + maxnews_data:
        
        if "content" in post and post["content"]:
            post["fake_news"] = fake_news_chain.invoke({"content": post["content"]}).strip()
            post["bias_analysis"] = bias_chain.invoke({"content": post["content"]}).strip()
        else:
            post["fake_news"] = "❌ No content available for analysis."
            post["bias_analysis"] = "❌ No content available for analysis."

    return {"reddit_posts": reddit_data, "maxnews_articles": maxnews_data}




