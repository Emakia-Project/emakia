import praw
import os
import requests

import streamlit as st

print("Redditsecret")
print(st.secrets["REDDIT_CLIENT_ID"])
# --- Configure Reddit API ---
reddit = praw.Reddit(
    client_id=st.secrets["REDDIT_CLIENT_ID"],
    client_secret=st.secrets["REDDIT_CLIENT_SECRET"],
    user_agent=st.secrets["REDDIT_USER_AGENT"]
)




from bs4 import BeautifulSoup

def get_article_text_from_url(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        # Try common article content containers
        candidates = ["article", "main", "div#content", "div.article-body", "div#mainArticleDiv"]
        for selector in candidates:
            block = soup.select_one(selector)
            if block and block.get_text(strip=True):
                return block.get_text(strip=True, separator="\n")
        
        # Fallback: all <p> tags
        paragraphs = soup.find_all("p")
        if paragraphs:
            return "\n".join(p.get_text() for p in paragraphs)

        return "No article content found."
    except Exception as e:
        #debug_logs.append(f"Article fetch error for {url}: {e}")
        return f"[link]({url})"

def get_reddit_posts(subreddit="politics", limit=3):
    posts = []
    try:
        for post in reddit.subreddit(subreddit).new(limit=limit):
            content = post.selftext.strip()
            if not content and post.url:
                content = get_article_text_from_url(post.url)

            posts.append({
                "title": post.title,
                "content": content or "[link]({post.url})",
                "link": post.url
            })
    except Exception as e:
        #debug_logs.append(f"Reddit error: {e}")
        print(f"Reddit error: {e}")
    return posts
