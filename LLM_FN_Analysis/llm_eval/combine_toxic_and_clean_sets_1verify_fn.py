import csv

# Input files
toxic_files = [
    "gemini_multi_toxic_llm.csv",
    "gemini_rt_or_none_likely_toxic.csv",
    "toxic_terms_lexicon_35000.csv"
]

non_toxic_files = [
    "gemini_single_toxic_llm.csv",
    "gemini_rt_or_none_likely_clean.csv"
]

fn_file = "at_least_one_fn.csv"

# Output files
toxic_output = "combined_toxic_term_rows.csv"
non_toxic_output = "combined_non_toxic_term_rows.csv"

# Helper to read CSV rows
def read_csv_rows(file_path):
    with open(file_path, mode='r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

# Deduplicate by text
def deduplicate_by_text(rows):
    seen = set()
    unique_rows = []
    for row in rows:
        text = row.get("text", "").strip()
        if text and text not in seen:
            seen.add(text)
            unique_rows.append(row)
    return unique_rows

# Read and combine
toxic_term_rows = []
non_toxic_term_rows = []

for file in toxic_files:
    toxic_term_rows.extend(read_csv_rows(file))

for file in non_toxic_files:
    non_toxic_term_rows.extend(read_csv_rows(file))

# Deduplicate both sets
toxic_term_rows = deduplicate_by_text(toxic_term_rows)
non_toxic_term_rows = deduplicate_by_text(non_toxic_term_rows)

# Verify total matches at_least_one_fn.csv
fn_rows = read_csv_rows(fn_file)
fn_texts = set(row["text"].strip() for row in fn_rows if "text" in row)

# Filter only rows that exist in at_least_one_fn.csv
toxic_term_rows = [row for row in toxic_term_rows if row.get("text", "").strip() in fn_texts]
non_toxic_term_rows = [row for row in non_toxic_term_rows if row.get("text", "").strip() in fn_texts]

total_combined = len(toxic_term_rows) + len(non_toxic_term_rows)
expected_total = len(fn_rows)

assert total_combined == expected_total, f"Mismatch: {total_combined} combined vs {expected_total} in at_least_one_fn.csv"

print(f"✅ Verified: {total_combined} rows match at_least_one_fn.csv")

# Write outputs
def write_csv(file_path, rows):
    if not rows:
        return
    with open(file_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

write_csv(toxic_output, toxic_term_rows)
write_csv(non_toxic_output, non_toxic_term_rows)
