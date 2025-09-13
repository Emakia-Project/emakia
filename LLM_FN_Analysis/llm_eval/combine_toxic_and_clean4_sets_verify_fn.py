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

# Read and combine
toxic_term_rows = []
non_toxic_term_rows = []

for file in toxic_files:
    toxic_term_rows.extend(read_csv_rows(file))

for file in non_toxic_files:
    non_toxic_term_rows.extend(read_csv_rows(file))

# Verify total matches at_least_one_fn.csv
fn_rows = read_csv_rows(fn_file)
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
