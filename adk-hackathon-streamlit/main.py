import streamlit as st
import os
import uuid
import requests
import time
from dotenv import load_dotenv
import google.generativeai as genai
import praw
from bs4 import BeautifulSoup
from google.adk.sessions import InMemorySessionService
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.genai import types

# Load environment variables
load_dotenv()

# --- Constants ---
APP_NAME = "toxicity_misinformation_analysis"
USER_ID = "analysis_user_streamlit_01"
SESSION_ID = f"session_{uuid.uuid4()}"
GEMINI_MODEL = "gemini-2.0-flash"

debug_logs = []

# --- API Key Configuration ---
try:
    GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except KeyError:
    st.error("ERROR: GOOGLE_API_KEY environment variable not set.")
    st.stop()
except Exception as e:
    st.error(f"Error configuring Generative AI: {e}")
    st.stop()

# --- Reddit API Configuration ---
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="fake-news-detector"
)

# --- Define AI Agents ---
toxicity_agent = LlmAgent(
    name="ToxicityAnalyst",
    model=GEMINI_MODEL,
    instruction="""You are an AI Toxicity Analyst. Analyze the following statement and determine if it contains toxic language.
    Respond with either 'toxic' or 'non-toxic'.""",
    description="Analyzes statements for toxicity.",
    output_key="toxicity_analysis"
)
bias_agent = LlmAgent(
    name="BiasAnalyst",
    model=GEMINI_MODEL,
    instruction="""You are an AI Bias Analyst. Assess the following statement for bias.
    Indicate whether the statement contains 'bias' or is 'neutral'and Provide your analysis and include:
- Whether the fact is likely true or false.
- References to sources that support or contradict the fact.
- The author or organization responsible for the content.
.""",
    description="Analyzes statements for bias.",
    output_key="bias_analysis"
)

misinformation_agent = LlmAgent(
    name="MisinformationAnalyst",
    model=GEMINI_MODEL,
    instruction="""You are a fake news analyst. Determine if the following fact is fake news.

    Respond with either 'misinformation' or 'accurate' and 
        Provide your analysis and include:
        - Whether the fact is likely true or false.
        - References to sources that support or contradict the fact.
        - The author or organization responsible for the content..""",
    description="Detects misinformation in statements.",
    output_key="misinformation_analysis"
)

# --- Create Parallel Agent ---
parallel_analysis_agent = ParallelAgent(
    name="ParallelAnalysisAgent",
    sub_agents=[toxicity_agent, misinformation_agent, bias_agent]
)

# --- Function to Create Session ---
def create_session():
    try:
        session_service = InMemorySessionService()
        session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
        debug_logs.append(f"ADK Session created: {session.id}. State is initially empty.")
        return session, session_service
    except Exception as e:
        st.error(f"Error creating session: {e}")
        return None, None

# --- Function to Write Debug Logs ---
def write_debug_logs():
    log_file = "debug_logs.txt"
    try:
        with open(log_file, "w") as file:
            for log in debug_logs:
                file.write(log + "\n")  # Write each log entry in a new line
        print(f"Debug logs saved to {log_file}")
    except Exception as e:
        print(f"Error writing debug logs: {e}")

# --- Function to Fetch Reddit Posts ---
def get_reddit_posts(subreddit: str, limit=5):
    """Fetch latest Reddit posts with error handling and structure."""
    posts = []
    try:
        subreddit_obj = reddit.subreddit(subreddit)
        for post in subreddit_obj.new(limit=limit):
            content = post.selftext.strip() if post.selftext else f"[Read more]({post.url})"
            posts.append({"title": post.title, "content": content, "link": post.url})
    except Exception as e:
        debug_logs.append(f"Reddit API Error: {e}")
    return posts



# --- Function to Fetch Maxnews Articles ---
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

    parsed_articles = []
    for article in articles[:3]:
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

        time.sleep(1)  
    
    return parsed_articles

# --- Function to Run Analysis on Reddit & Maxnews Content ---
def run_analysis_on_articles():
    session, session_service = create_session()
    if not session:
        return [], []

    reddit_posts = get_reddit_posts("politics", limit=3)
    maxnews_articles = get_maxnews_articles()

    analyzed_results = []

    for post in reddit_posts + maxnews_articles:
        statement = post["content"]
        debug_logs.append(f"Analyzing statement: {statement}")
        
        try:
            runner = Runner(agent=parallel_analysis_agent, app_name=APP_NAME, session_service=session_service)
            content = types.Content(role='user', parts=[types.Part(text=statement)])
            events = runner.run(user_id=USER_ID, session_id=session.id, new_message=content)

            toxicity_result = None
            bias_result = None
            misinformation_result = None
            


            for event in events:
                if hasattr(event.content, "parts") and event.content.parts:
                    text_output = event.content.parts[0].text
                    debug_logs.append(f"Extracted text: {text_output}")

                    if "toxic" in text_output.lower():
                        toxicity_result = text_output
                    elif "bias" in text_output.lower():
                        bias_result = text_output
                    elif "misinformation" in text_output.lower():
                        misinformation_result = text_output

            analyzed_results.append({
                "title": post.get("title", "No title available"),
                "content": statement,
                "toxicity": toxicity_result or "No toxicity detected",
                "bias": bias_result or "No bias detected",
                "misinformation": misinformation_result or "No misinformation detected"
            })

        except Exception as e:
            debug_logs.append(f"Error running analysis: {e}")

    write_debug_logs()
    return analyzed_results

# --- Streamlit UI ---
st.title("🔍 Reddit & Maxnews AI Toxicity & Misinformation Analyzer")

if st.button("Fetch & Analyze Latest Posts"):
    with st.spinner("Fetching and analyzing posts..."):
        analyzed_articles = run_analysis_on_articles()

    if analyzed_articles:
        st.header("📰 Analysis Results")
        for post in analyzed_articles:
            st.subheader(post["title"])
            st.write(f"**Content:** {post['content']}")
            st.write(f"📌 **Toxicity Analysis:** {post['toxicity']}")
            st.write(f"📌 **bias Analysis:** {post['bias']}")
            st.write(f"⚖ **Misinformation Analysis:** {post['misinformation']}")
            st.write("---")
    else:
        st.warning("❌ No articles available for analysis.")
