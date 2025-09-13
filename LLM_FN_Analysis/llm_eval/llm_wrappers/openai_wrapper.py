# call_openai()
# OpenAI API wrapper
import os
import time
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
llm = OpenAI(temperature=0, openai_api_key=api_key)

template = """You are a sentiment analyst. Analyze the following statement and respond with either "positive" or "negative".

Statement: {content}

YOUR RESPONSE:
"""
prompt_template = PromptTemplate(input_variables=["content"], template=template)
content_chain = prompt_template | llm

def invoke_with_retries(content_chain, content, retries=3, delay=5):
    for attempt in range(retries):
        try:
            return content_chain.invoke({"content": content}).strip('"')
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    raise Exception("All retry attempts failed")



def call_openai(texts):
    predictions = []
    for text in texts:
        try:
            response = invoke_with_retries(content_chain, text).lower()
            # Interpret response into binary prediction
            if "positive" in response or "neutral" in response:
                predictions.append(1)
            elif "negative" in response or any(term in response for term in [
                "harmful", "sexual", "slur", "violence", "hate", "discriminatory", "abuse", "harassment"
            ]):
                predictions.append(0)
            else:
                predictions.append(0)  # Default to toxic
        except Exception as e:
            print(f"OpenAI failed on: {text[:50]}... → {e}")
            predictions.append(0)  # Fail-safe
        time.sleep(1.2)  # Optional: throttle between successful requests
    return predictions


