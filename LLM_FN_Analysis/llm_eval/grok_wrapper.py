import os
import time
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_xai import ChatXAI

# Load environment variables
load_dotenv()
api_key = os.getenv("XAI_API_KEY")
if not api_key:
    raise ValueError("Grok API key (XAI_API_KEY) not found in environment variables")

# Initialize Grok client
llm = ChatXAI(xai_api_key=api_key, model="grok-2-1212")

# Define prompt template
template = """You are a sentiment analyst. Analyze the following statement and respond with either "positive" or "negative".

Statement: {content}

YOUR RESPONSE:
"""
prompt_template = PromptTemplate(input_variables=["content"], template=template)
content_chain = prompt_template | llm

# Retry logic with exponential backoff
def invoke_with_retries(content_chain, content, retries=3, delay=10):
    for attempt in range(retries):
        try:
            response = content_chain.invoke({"content": content})
            return response.content
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if 'too many requests' in str(e).lower():
                time.sleep(min(2 ** attempt, delay))
            else:
                raise
    raise Exception("All attempts failed.")

# Final callable for FN pipeline
def call_grok(texts):
    predictions = []
    for text in texts:
        response = invoke_with_retries(content_chain, text).lower()

        if "positive" in response or "neutral" in response or "happy" in response:
            predictions.append(1)
        elif "negative" in response or any(term in response for term in [
            "harmful", "sexual", "slur", "violence", "hate", "discriminatory", "abuse", "harassment",
            "graphic", "explicit", "threat", "danger", "profanity", "stalking", "bullying", "racism"
        ]):
            predictions.append(0)
        else:
            predictions.append(0)  # Default to toxic if uncertain
    return predictions
