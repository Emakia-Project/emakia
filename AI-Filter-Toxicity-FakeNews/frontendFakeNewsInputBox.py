import streamlit as st
import requests

API_URL = "http://localhost:8000/analyze/"

st.title("Fake News & Bias Dashboard")
text = st.text_area("Enter text to analyze")

if st.button("Analyze"):
    response = requests.post(API_URL, json={"text": text})
    if response.status_code == 200:
        results = response.json()
        st.write("Bias Analysis:", results["bias"])
        st.write("Fake News Detection:", results["fake_news"])
    else:
        st.error("Error analyzing text")
