# 🧠 BiasMesh  
*A graph-powered moderation pipeline for bias, toxicity, and misinformation detection.*

## 🚀 Overview

BiasMesh is a modular classification system within the Emakia ecosystem that detects and labels bias, toxicity, and misinformation in tweet data. Leveraging LLM agents, Neo4j graph updates, and BigQuery ingestion, it supports ethical AI goals with traceable metadata and intuitive visualization.

This repository holds the core pipeline, LLM agent definitions, and orchestration logic.

## 🧩 Key Features

- 🧠 Agent-based classification of bias, toxicity, and misinformation via CrewAI  
- 🧵 Dynamic graph updates using Cypher and Neo4j AuraDB  
- 📊 Ingestion of tweet data via BigQuery  
- 🌐 Modular architecture for scaling and agent retraining  
- 📁 Prompt templates and environment-based credential handling  
- 🧪 Unit tests for robustness and experimentation

## 🗂️ Directory Structure

biasmesh/ ├── agents/ # LLM agent definitions ├── pipeline/ # Ingestion and classification logic ├── config/ # Prompts and environment configs ├── utils/ # Logging and retry wrappers ├── tests/ # Unit tests ├── notebooks/ # Exploration notebooks ├── main.py  # Entry point script ├── .env # Local secrets loader ├── requirements.txt  # Dependencies

## 🛠️ Built With

- **Languages:** Python, Cypher  
- **Frameworks:** CrewAI, `python-dotenv`  
- **Cloud Services:** Google BigQuery, Neo4j AuraDB  
- **Models & APIs:** OpenAI GPT-4o, Anthropic Claude 3 (optional fallback)  
- **Visualization (optional):** Streamlit  
- **Hosting (suggested):** GitHub + optional deployment via Vercel or Netlify

## 🧪 Run Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/Emakia-Project/emakia
   cd emakia/biasmesh
   Add your credentials to .env:
env
OPENAI_API_KEY=sk-xxx
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service.json
Install dependencies:
bash
pip install -r requirements.txt
Run classification:
bash
python main.py
