import os
import csv
import re
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Google API key not found in environment variables")

# Initialize Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=api_key,
    temperature=0,
)

def invoke_with_retries(client, content, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = client.invoke([{"role": "user", "content": content}])
            return response.content.strip() if hasattr(response, "content") else "PROHIBITED_CONTENT"
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(delay)
    return "Model invocation failed"

def extract_toxic_term(response):
    match = re.search(r'The toxic term in the statement is \*\*"(.*?)"\*\*', response)
    if match:
        return match.group(1).strip()
    quoted = re.findall(r'"(.*?)"', response)
    if quoted:
        return quoted[0].strip()
    return response.strip() if len(response.strip().split()) <= 3 else "No toxic term found"

def screen_with_gemini(input_file, output_file):
    results = []
    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            text = row["text"].strip()
            prompt = f"""Identify the toxic term of the following sentence. Respond with the toxic term.

            Statement: {text}
            YOUR RESPONSE:"""
            response = invoke_with_retries(llm, prompt)
            toxic_term = extract_toxic_term(response)
            results.append([toxic_term, row["label"], text] + [row[model] for model in row if model.startswith("prediction_")])
            print(f"[{i+1}] Toxic term: {toxic_term} | Text: {text}")

    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        header = ["toxic_term", "label", "text", "prediction_openai", "prediction_gemini", "prediction_grok", "prediction_llama", "prediction_deepseek"]
        writer.writerow(header)
        writer.writerows(results)

# Run full Gemini screening
screen_with_gemini(
    input_file="to_screen_with_gemini_35000.csv",
    output_file="toxic_terms_gemini_35000.csv"
)
