# call_llama()
# Llama API wrapper
import os
import time
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
#from langchain.prompts import PromptTemplate
from langchain_core.runnables.base import Runnable
from fireworks.client import Fireworks

load_dotenv()
fireworks_api_key = os.getenv("FIREWORKS_API_KEY")

def invoke_with_retries(client, model, content, retries=3, delay=5):
    last_exception = None
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": content}]
            )
            return response.choices[0].message.content
        except Exception as e:
            last_exception = e
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    raise Exception(f"All retry attempts failed. Last error: {last_exception}") from last_exception

class FireworksWrapper(Runnable):
    def __init__(self, api_key, model_name):
        self.client = Fireworks(api_key=api_key)
        self.model_name = model_name

    def invoke(self, input_data, *args, **kwargs):
        # Handle different input types from langchain chains
        if isinstance(input_data, dict):
            content = input_data.get("content", "")
        elif hasattr(input_data, "text"):  # PromptValue objects
            content = input_data.text
        elif hasattr(input_data, "content"):  # Alternative PromptValue format
            content = input_data.content
        else:
            content = str(input_data)
        return invoke_with_retries(self.client, self.model_name, content)

llm = FireworksWrapper(api_key=fireworks_api_key, model_name="accounts/fireworks/models/llama-v3p3-70b-instruct")

template = """You are a sentiment analyst. Analyze the following statement and respond with either "positive" or "negative".

Statement: {content}
YOUR RESPONSE:"""
prompt_template = PromptTemplate(input_variables=["content"], template=template)
content_chain = prompt_template | llm

def call_llama(texts):
    predictions = []
    for text in texts:
        response = content_chain.invoke({"content": text}).strip('"').lower()
        if "positive" in response or "neutral" in response:
            predictions.append(1)
        elif "negative" in response or any(term in response for term in [
            "harmful", "sexual", "slur", "violence", "hate", "discriminatory", "abuse", "harassment"
        ]):
            predictions.append(0)
        else:
            predictions.append(0)  # Default to toxic if uncertain
    return predictions


