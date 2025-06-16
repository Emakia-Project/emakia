# 🧠 Multi-Agent Analyzer for Toxicity, Bias & Misinformation (Built with Google ADK)

This project is a multi-agent system built with Google's Agent Development Kit (ADK) and Gemini Flash, designed for the [Hackathon Name]. It automates the detection of **toxicity**, **bias**, and **misinformation** from real-world sources (Reddit, Maxnews, etc.) and optionally derives further insights via BigQuery analysis.

Streamlit powers the interactive front end, while each step is modularized into ADK-compliant agents to ensure extensibility, transparency, and replicability.

---

## 📌 Features

- 🤖 **LLM Agents** using Gemini 2.0 Flash
- 🧠 **Sequential and Parallel Execution** powered by Google ADK
- 📊 **BigQuery Integration** for data-driven trend analysis (optional)
- 📰 **Live Data** pulled from Reddit and news sites
- 📦 Easy-to-install: hosted app, public repo, plug-and-play `.env` setup
- 📺 Demo-ready via Streamlit UI

---

## 🛠️ Tech Stack

| Layer         | Technology                                 |
|---------------|---------------------------------------------|
| Agent Framework | Google ADK (python package `google-adk`) |
| LLM APIs      | Gemini 2.0 Flash via `google-generativeai` |
| Data Pipeline | Reddit API, Custom News Scrapers           |
| UI            | Streamlit                                  |
| Storage       | (Optional) Google BigQuery for Analysis    |
| Orchestration | `ParallelAgent`, `SequentialAgent`, `LlmAgent` (ADK) |

---

## 📁 Project Structure

```bash
adk-hackathon-streamlit/
├── main.py                  # Streamlit app and runner logic
├── agents/                  # Modular ADK agent definitions
├── diagram.png              # Architecture overview
├── requirements.txt         # All Python dependencies
├── .env.example             # Template for required secrets
├── debug_logs.txt           # Runtime debug logs
├── README.md                # You're reading it :)

## 🧪 Local Setup

### Clone & Enter the Repo
```bash
git clone https://github.com/your-username/adk-hackathon-streamlit.git
cd adk-hackathon-streamlit


###Create Environment & Install Dependencies
```bash
python3 -m venv env && source env/bin/activate
pip install -r requirements.txt
Configure Environment Variables
```bash
cp .env.example .env  # then fill in your API keys and credentials
Run the App
```bash
streamlit run main.py
🎯 How It Works
Data Fetching
Pulls the latest Reddit posts (/r/politics) and headlines from Maxnews.
Sequential Agent Chain
Passes each item through LLM agents:
ToxicityAnalyst
BiasAnalyst
MisinformationAnalyst
(Optional) BigQuery Agent
Aggregates high-risk patterns into data queries for trend summarization.
UI Output
Displays per-item analysis results inside Streamlit.
Logs are persisted for review and scoring.
###📊 Architecture Diagram
###🚀 Submission Checklist
[x] ✅ Hosted Project with working UI
[x] ✅ Public GitHub repository
[x] ✅ Text description (you're reading it!)
[x] ✅ Architecture diagram (diagram.png)
[x] ✅ 3-minute demo video on YouTube/Vimeo (link goes here)
[x] ✅ Code supports English language input/output
[x] ✅ Original work using public/open API keys only
###📝 Environment Variables
See .env.example for a full list, including:
GOOGLE_API_KEY
REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET
GOOGLE_CLOUD_PROJECT_ID
GOOGLE_APPLICATION_CREDENTIALS
Optionally: BROWSERBASE_API_KEY, OPENAI_API_KEY, FACEBOOK_ACCESS_TOKEN, etc.
###📚 Learnings & Takeaways
Building modular ADK agents made error isolation and debugging easy.
Gemini’s performance with focused instructions significantly improved result quality.
Streamlit offered a fast way to iterate on visualization and feedback loops.
Managing environment variables securely and scalably across platforms remains essential.
Custom agents can be deeply personalized to specific content types and domains.
###🧑‍💻 Authors
Created by Corinne David, with support from Microsoft Copilot and Google’s ADK framework.
📄 License
MIT License – please see LICENSE for details.
