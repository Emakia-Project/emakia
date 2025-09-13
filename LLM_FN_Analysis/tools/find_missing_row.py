import csv

def load_texts_with_index(path, text_column_name, max_rows=None):
    text_map = {}
    with open(path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            if max_rows and i > max_rows:
                break
            text = row[text_column_name].strip()
            text_map[text] = i
    return text_map

# Load first 43,511 rows from original file
original_map = load_texts_with_index("tweets-labels-emojis.csv", "text", max_rows=43511)

# Load all rows from predictions file
predicted_map = load_texts_with_index("llm_predictions_log_new.csv", "text")

# Compare
missing_texts = set(original_map.keys()) - set(predicted_map.keys())

if missing_texts:
    print(f"❌ Missing {len(missing_texts)} row(s) in llm_predictions_log_new.csv:")
    for text in missing_texts:
        print(f"→ Row {original_map[text]}: {text}")
else:
    print("✅ All 43,511 rows are matched.")
