from langchain_openai import OpenAI
from dotenv import load_dotenv
import os

# ✅ Load environment variables from .env file
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found in environment.")

llm = OpenAI(openai_api_key=api_key, model_name="gpt-4", temperature=0.7)

prompt = "Write a 5-line bedtime story about a unicorn."

try:
    response = llm.invoke(prompt)
    print("✅ Response received:")
    print(response)
except Exception as e:
    print("❌ API call failed:")
    print(e)


