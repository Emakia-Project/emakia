import os
import csv
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Google API key not found in environment variables")

# File paths
fp_file = "at_least_one_fp.csv"
lexicon_file = "full_hatebase_element.csv"
lexicon_output = "toxic_terms_lexicon_35000.csv"
to_screen_file = "to_screen_with_gemini_35000.csv"

# Read toxic lexicon
def read_lexicon(file_path):
    with open(file_path, mode='r', encoding='utf-8') as f:
        return set(row[0].strip().lower() for row in csv.reader(f) if row)

# Process rows and split by lexicon match
def screen_with_lexicon(fp_file, lexicon_file):
    lexicon = read_lexicon(lexicon_file)
    lexicon_hits = []
    to_screen = []

    with open(fp_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = row["text"].strip().lower()
            label = row["label"]
            predictions = [row[model] for model in row if model.startswith("prediction_")]

            # Lexicon match
            if any(term in text.split() for term in lexicon):
                toxic_term = next(term for term in lexicon if term in text.split())
                lexicon_hits.append([toxic_term, label, row["text"]] + predictions)
            else:
                to_screen.append(row)

    return lexicon_hits, to_screen

# Write output
def write_csv(file_path, header, rows):
    with open(file_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

def write_dict_csv(file_path, rows):
    if not rows:
        return
    with open(file_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

# Run pipeline
lexicon_hits, to_screen = screen_with_lexicon(fp_file, lexicon_file)

# Write results
prediction_headers = ["prediction_openai", "prediction_gemini", "prediction_grok", "prediction_llama", "prediction_deepseek"]
write_csv(lexicon_output, ["toxic_term", "label", "text"] + prediction_headers, lexicon_hits)
write_dict_csv(to_screen_file, to_screen)
