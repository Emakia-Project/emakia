# Emakia, Machine Learning Project

Emakia was inspired by the urgent need to combat online harassment and its harmful effects on marginalized groups, including women, people of color, and LGBTQI+ individuals. Addressing these issues is essential for protecting mental well-being and ensuring freedom of expression online. We're building an app to filter out toxic content on social media, but first, we need an efficient text classifier model and a smart AI system to validate labels and outputs.

## Project Directory Machine Learning Project Structure

## Main Directory:

## Apple Development
  Core
  Models
  Preview Content/Preview Assets.xcassets
  Services
  TestingTableView.xcdatamodeld/TestingTableView.xcdatamodel
  Persistence.swift
  emakiaTweetsSentimentClassifier.mlmodel
  env.docx

## Google Cloud Server Development 
  # Text Classifier Training
    Notebook: All the Jupyter notebooks used for EDA, visualization, and proof of concept (POC).
    Node.js
    Validation
    evaluate_model_01.py: Different matrices used to validate the model.
    evaluate_model_02.py: Different matrices used to validate the model.
  # gcloud toolkit recent search
    Twitter API Toolkit for Google Cloud: Recent Search
    https://developer.twitter.com/en/docs/tutorials/developer-guide--twitter-api-toolkit-for-google-cloud

## Data:
  external: Data from third-party sources.
  interim: Intermediate data that has been transformed.
  processed: The final, canonical data sets for modeling.
  raw: The original, immutable data dump.

## Sraping Data

## LLM-RAG-Toxicity-Evaluator/lang chain-openai
  First, we are evaluating the label file that we train our text classifier Vertex AI and CoreML with langchain-openai.
  Approach 1
  "You are a sentiment analyst. Analyze the following statement and respond with either 'positive' or 'negative'."
  Approach 2
  "Analyze the following statement and explain your choice of overall sentiment." Focus on analyzing Arrays 3 and 4, representing false negatives and false positives.
  LangChain Overview LangChain is an open-source framework designed to simplify the creation of applications using large language models (LLMs). It provides a standard interface for chaining multiple LLMs together, allowing developers to build more complex and powerful applications.
  LangChain-OpenAI Integration LangChain integrates with OpenAI models to enhance their capabilities by chaining multiple language model calls and incorporating external tools. This is useful for building complex applications that require advanced language understanding and interaction.
  
  # Environment Setup
  Create the .env file with:
  OPENAI_API_KEY=your_openai_api_key
  
  export LANGCHAIN_PROJECT=default
  Virtual Environment (Recommended)
  Create: python3 -m venv env
  Activate: source env/bin/activate
  Install: pip install langchain_openai
  
  # Code 
  evaluateLabelswithLangchain.py
  resultsfromLabelValidation.py
  evaluate-with-lexicon.py
  
  # Results for our label file.
  Evaluation Findings During the evaluation of training labels using the LLM, we found that 2% of the label data contained only return characters, causing them to not match the conditions. These invalid entries need to be cleaned from the training set to improve label accuracy.
  Performance Analysis
  True Positive (TP): Harassment content predicted by LLM and labeled as “0”: 31.50%
  True Negative (TN): Neutral content predicted by LLM and labeled as “1”: 41.68%
  False Negative (FN): Harassment content predicted by LangChainOpenAI and labeled as “1”: 24.68%
  False Positive (FP): Neutral content predicted by LLM and labeled as “0”: 2.12%
  Currently, 73.18% of the labels (31.50% + 41.68%) are correct, while 26.8% (24.68% + 2.12%) are mislabeled. It is still unclear whether this discrepancy is due to poor LLM performance or incorrect labeling.
  
  \***\*Note\*\***: The `data` folder and `.env` file won’t appear in github. It will be in your local folder. This is not pushed to githhub as it will be in the ignore list (`.gitignore` file). If you want to checkin that also, just comment out in `.gitignore` file and add the data folder to github.

# emakia
