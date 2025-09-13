import csv

# File paths
input_file = "to_screen_with_gemini_35000.csv"
toxic_file = "toxic_terms_gemini_35000.csv"
no_toxic_file = "NO_toxic_terms_gemini_35000.csv"
fp_file = "at_least_one_fp.csv"
lexicon_file = "toxic_terms_lexicon_35000.csv"

# Load input rows
with open(input_file, mode='r', encoding='utf-8') as f:
    input_rows = list(csv.DictReader(f))

# Load toxic term rows
with open(toxic_file, mode='r', encoding='utf-8') as f:
    toxic_reader = csv.DictReader(f)
    toxic_texts = set(row["text"].strip() for row in toxic_reader)

# Identify non-toxic rows
no_toxic_rows = [row for row in input_rows if row["text"].strip() not in toxic_texts]

# Write NO_toxic_terms file
with open(no_toxic_file, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=input_rows[0].keys())
    writer.writeheader()
    writer.writerows(no_toxic_rows)

# Load other files for verification
def count_rows(file_path):
    with open(file_path, mode='r', encoding='utf-8') as f:
        return sum(1 for _ in f) - 1  # subtract header

input_count = count_rows(input_file)
toxic_count = count_rows(toxic_file)
no_toxic_count = count_rows(no_toxic_file)
fp_count = count_rows(fp_file)
lexicon_count = count_rows(lexicon_file)

# Print verification
print(f"✅ Input rows: {input_count}")
print(f"✅ Toxic term rows: {toxic_count}")
print(f"✅ NO toxic term rows: {no_toxic_count}")
print(f"✅ Sum of toxic + NO toxic: {toxic_count + no_toxic_count}")
print(f"✅ FP rows: {fp_count}")
print(f"✅ Lexicon rows: {lexicon_count}")
print(f"✅ FP == Input + Lexicon? {fp_count == input_count + lexicon_count}")
