from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# ✅ Load environment variables
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found in environment.")

# ✅ Use ChatOpenAI for GPT-4 or GPT-3.5
llm = ChatOpenAI(openai_api_key=api_key, model_name="gpt-4", temperature=0.7)

prompt = "Write a 5-line bedtime story about a unicorn."

try:
    response = llm.invoke(prompt)
    print("✅ Response received:")
    print(response)
except Exception as e:
    print("❌ API call failed:")
    print(e)
