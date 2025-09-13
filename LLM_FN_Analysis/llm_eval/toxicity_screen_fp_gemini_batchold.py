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

# Read toxic lexicon
def read_lexicon(file_path):
    with open(file_path, mode='r', encoding='utf-8') as f:
        return set(row[0].strip().lower() for row in csv.reader(f) if row)

# Extract toxic term from Gemini response
def extract_toxic_term(response):
    if not response or not hasattr(response, "content") or not response.content:
        return "PROHIBITED_CONTENT"
    match = re.search(r'\*\*"(.*?)"\*\*', response.content)
    return match.group(1).strip() if match else "No toxic term found"

# Process rows from at_least_one_fp.csv
def process_fp_rows(fp_file, lexicon_file):
    lexicon = read_lexicon(lexicon_file)
    lexicon_hits = []
    gemini_hits = []
    no_toxic_term_found = []
    rows_to_screen = []

    with open(fp_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = row["text"].strip().lower()
            label = row["label"]
            predictions = [row[model] for model in row if model.startswith("prediction_")]

            # Lexicon match
            if any(term in text.split() for term in lexicon):
                toxic_term = next(term for term in lexicon if term in text.split())
                lexicon_hits.append([toxic_term, label, text] + predictions)
            else:
                rows_to_screen.append((row, text, label, predictions))

    # Sequential Gemini calls
    for row, text, label, predictions in rows_to_screen:
        prompt = f"""Identify the toxic term in the following sentence. Respond with the toxic term only.

        Statement: {text}
        YOUR RESPONSE:"""
        try:
            response = llm.invoke([{"role": "user", "content": prompt}])
            toxic_term = extract_toxic_term(response)
        except Exception as e:
            print(f"Gemini error: {e}")
            toxic_term = "PROHIBITED_CONTENT"

        if toxic_term != "No toxic term found":
            gemini_hits.append([toxic_term, label, text] + predictions)
        else:
            no_toxic_term_found.append([label, text] + predictions)

    return lexicon_hits, gemini_hits, no_toxic_term_found

# Write output files
def write_output(file_path, header, rows):
    with open(file_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

# File paths
fp_file = "at_least_one_fp.csv"
lexicon_file = "full_hatebase_element.csv"
lexicon_output = "toxic_terms_lexicon_35000.csv"
gemini_output = "toxic_terms_gemini_35000.csv"
clean_output = "no_toxic_terms_detected_35000.csv"

# Run pipeline
lexicon_hits, gemini_hits, no_toxic_term_found = process_fp_rows(fp_file, lexicon_file)

# Write results
prediction_headers = ["prediction_openai", "prediction_gemini", "prediction_grok", "prediction_llama", "prediction_deepseek"]
write_output(lexicon_output, ["toxic_term", "label", "text"] + prediction_headers, lexicon_hits)
write_output(gemini_output, ["toxic_term", "label", "text"] + prediction_headers, gemini_hits)
write_output(clean_output, ["label", "text"] + prediction_headers, no_toxic_term_found)
