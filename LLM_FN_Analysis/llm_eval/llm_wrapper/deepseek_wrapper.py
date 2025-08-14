import os
import time
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_core.runnables.base import Runnable
from fireworks.client import Fireworks

load_dotenv()
fireworks_api_key = os.getenv("FIREWORKS_API_KEY")

def invoke_with_retries(client, model, content, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": content}]
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
    raise Exception("All retry attempts failed")

class FireworksWrapper(Runnable):
    def __init__(self, api_key, model_name):
        self.client = Fireworks(api_key=api_key)
        self.model_name = model_name

    def invoke(self, input_data, *args, **kwargs):
        content = input_data.get("content", "") if isinstance(input_data, dict) else str(input_data)
        return invoke_with_retries(self.client, self.model_name, content)

llm = FireworksWrapper(api_key=fireworks_api_key, model_name="accounts/fireworks/models/deepseek-r1")

template = """You are a sentiment analyst. Analyze the following statement and respond with either "positive" or "negative".

Statement: {content}
YOUR RESPONSE:"""
prompt_template = PromptTemplate(input_variables=["content"], template=template)
content_chain = prompt_template | llm

def call_deepseek(texts):
    predictions = []
    for text in texts:
        response = content_chain.invoke({"content": text}).strip('"').lower()
        if "positive" in response or "neutral" in response:
            predictions.append(1)
        elif "negative" in response or any(term in response for term in [
            "harmful", "sensitive", "derogatory", "dangerous", "violence", "hatred"
        ]):
            predictions.append(0)
        else:
            predictions.append(0)  # Default to toxic if uncertain
    return predictions
