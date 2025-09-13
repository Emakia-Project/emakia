import sys
import os
import csv

# Dynamically add llm_eval to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "llm_eval")))

from llm_wrappers.openai_wrapper import call_openai
from llm_wrappers.gemini_wrapper import call_gemini
from llm_wrappers.grok_wrapper import call_grok
from llm_wrappers.llama_wrapper import call_llama
from llm_wrappers.deepseek_wrapper import call_deepseek


# Path to your test CSV file
input_csv_file = "array_three.csv"

# Read first 20 rows
def load_test_rows(path, limit=20):
    rows = []
    with open(path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0:
                continue  # Skip header
            if len(row) < 3:
                continue
            rows.append({"text": row[2].strip(), "meta": row[:2]})
            if len(rows) >= limit:
                break
    return rows

# Run all LLMs
def test_all_llms(rows):
    print("Evaluating on", len(rows), "rows...\n")

    llm_outputs = {
        "openai": call_openai([r["text"] for r in rows]),
        "gemini": call_gemini([r["text"] for r in rows]),
        "grok": call_grok([r["text"] for r in rows]),
        "llama": call_llama([r["text"] for r in rows]),
        "deepseek": call_deepseek([r["text"] for r in rows]),
    }

    # Print results
    for i, row in enumerate(rows):
        print(f"\nRow {i+1}: {row['text']}")
        for model, preds in llm_outputs.items():
            print(f"  {model:<8}: {'neutral' if preds[i] == 1 else 'toxic'}")

if __name__ == "__main__":
    test_rows = load_test_rows(input_csv_file)
    test_all_llms(test_rows)

