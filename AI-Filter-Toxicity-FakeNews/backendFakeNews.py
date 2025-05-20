import os
from fastapi import FastAPI, HTTPException
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OpenAI API key not found in environment variables")

print("✅ OpenAI API Key Loaded")

# Initialize OpenAI client
llm = OpenAI(temperature=0, openai_api_key=api_key)

# Bias & Fake News Detection Prompts
bias_prompt_template = PromptTemplate(
    input_variables=["content"],
    template="Analyze the following statement for political bias.\n\nStatement: {content}\nBias Analysis:"
)

fake_news_prompt_template = PromptTemplate(
    input_variables=["content"],
    template="You are a fake news analyst. Determine if the following fact is fake news.\n\nFact: {content}\nYOUR RESPONSE:"
)

bias_chain = bias_prompt_template | llm
fake_news_chain = fake_news_prompt_template | llm

# Initialize FastAPI App
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to the Fake News & Bias Detection API!"}


@app.post("/analyze/")
async def analyze_text(data: dict):
    text = data.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    bias_result = bias_chain.invoke({"content": text})
    fake_news_result = fake_news_chain.invoke({"content": text})

    return {"bias": bias_result.strip(), "fake_news": fake_news_result.strip()}
