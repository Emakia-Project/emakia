import os
import praw
from google.adk.agents.parallel_agent import ParallelAgent
from .sub_agents.toxicity_agent import get_toxicity_agent
from .sub_agents.bias_agent import get_bias_agent
from .sub_agents.misinformation_agent import get_misinformation_agent

# Reddit API configuration (expects environment variables to be set)
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "fake-news-detector")

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

def get_reddit_posts(subreddit: str, limit=5):
    """
    Fetch latest Reddit posts from a subreddit.
    Returns a list of dicts with 'title', 'content', and 'link'.
    """
    posts = []
    try:
        subreddit_obj = reddit.subreddit(subreddit)
        for post in subreddit_obj.new(limit=limit):
            content = post.selftext.strip() if post.selftext else f"[Read more]({post.url})"
            posts.append({"title": post.title, "content": content, "link": post.url})
    except Exception as e:
        print(f"Reddit API Error: {e}")
    return posts

def get_root_agent():
    """
    Returns a ParallelAgent that runs toxicity, bias, and misinformation analysis in parallel.
    """
    return ParallelAgent(
        name="RootParallelAnalysisAgent",
        sub_agents=[
            get_toxicity_agent(),
            get_bias_agent(),
            get_misinformation_agent()
        ]
    )
