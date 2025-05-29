import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.title("Reddit & Maxnews Fake News & Bias Analysis")

if st.button("Fetch Latest Posts"):
    response = requests.get(f"{API_URL}/fetch_posts")  # Fetch posts from backend

    if response.status_code == 200:
        results = response.json()
        reddit_posts = results.get("reddit_posts", [])
        maxnews_articles = results.get("maxnews_articles", [])  # Changed from Facebook to maxnews

        # Display Reddit Content Analysis
        st.header("🔴 Reddit Content Analysis")
        if not reddit_posts:
            st.write("❌ No Reddit posts found.")
        else:
            for post in reddit_posts:
                st.write(f"**Title:** {post.get('title', 'No title available')}")
                st.write(f"📝 **Content:** {post.get('content', 'No text available')}")
                st.write(f"📌 **Fake News Detection:** {post.get('fake_news', 'No analysis available')}")
                st.write(f"⚖ **Bias Analysis:** {post.get('bias_analysis', 'No bias analysis available')}")
                st.write("---")

        # Display maxnews Content Analysis
        st.header("🔵 maxnews Content Analysis")
        if not maxnews_articles:
            st.write("❌ No Maxnews articles found.")
        else:
            for post in maxnews_articles:
                st.write(f"**Title:** {post.get('title', 'No title available')}")
                st.write(f"🔗 **Source:** [Read more here]({post.get('content', '#')})")  # Link to original article
                st.write(f"📌 **Fake News Detection:** {post.get('fake_news', 'No analysis available')}")
                st.write(f"⚖ **Bias Analysis:** {post.get('bias_analysis', 'No bias analysis available')}")
                st.write("---")
    else:
        st.error("❌ Error fetching social media posts. Please try again.")
