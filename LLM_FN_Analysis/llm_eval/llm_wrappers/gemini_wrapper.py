import os
import time
import csv
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Google API key not found in environment variables")

# Initialize Gemini client with longer timeout
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=api_key,
    temperature=0,
    timeout=60  # ⏱️ Increased timeout to avoid 504 errors
)

# Define prompt template
template = """You are a sentiment analyst. Analyze the following statement and respond with either "positive" or "negative".

Statement: {content}
YOUR RESPONSE:"""
prompt_template = PromptTemplate(input_variables=["content"], template=template)
content_chain = prompt_template | llm

# Optional: Clean and truncate input
def clean_text(text, max_len=1000):
    return text.strip()[:max_len]

# ✅ Final callable for FN pipeline
def call_gemini(texts, save_path=None):
    predictions = []
    logs = []

    for i, text in enumerate(texts):
        cleaned = clean_text(text)

        for attempt in range(3):  # 🔁 Retry logic
            try:
                response = content_chain.invoke({"content": cleaned})
                review_text = response.content.strip().lower()

                if len(review_text) > 10:
                    prediction = 0  # Treat long/ambiguous responses as toxic
                elif "positive" in review_text or "neutral" in review_text or "happy" in review_text:
                    prediction = 1
                elif "negative" in review_text or any(term in review_text for term in [
                    "harmful", "sexual", "slur", "violence", "hate", "discriminatory", "abuse", "harassment",
                    "graphic", "explicit", "threat", "danger", "profanity", "stalking", "bullying", "racism"
                ]):
                    prediction = 0
                else:
                    prediction = 0  # Default to toxic if uncertain

                predictions.append(prediction)
                logs.append({"text": text, "response": review_text, "prediction": prediction})
                break  # ✅ Success, break retry loop

            except Exception as e:
                print(f"⚠️ Gemini attempt {attempt+1} failed on input {i}: {e}")
                time.sleep(2 * (attempt + 1))  # ⏳ Exponential backoff

        else:
            predictions.append(0)
            logs.append({"text": text, "response": "ERROR", "prediction": 0})

        time.sleep(1.2)  # Respect rate limits

    # ✅ Optional: Save results to CSV
    if save_path:
        with open(save_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["text", "response", "prediction"])
            writer.writeheader()
            writer.writerows(logs)
        print(f"📁 Results saved to {save_path}")

    return predictions
