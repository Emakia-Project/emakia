import csv

# Input and output file paths
input_file = "toxic_terms_gemini_35000.csv"
rt_or_none_file = "gemini_flagged_rt_or_none.csv"
valid_toxic_terms_file = "gemini_valid_toxic_terms.csv"

# Arrays to hold rows
rt_or_none_rows = []
valid_toxic_rows = []

# Read and split
with open(input_file, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames

    for row in reader:
        toxic_term = row["toxic_term"].strip().lower()
        if toxic_term == "rt" or toxic_term == "no toxic term found":
            rt_or_none_rows.append(row)
        else:
            valid_toxic_rows.append(row)

# Write rt or none
with open(rt_or_none_file, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rt_or_none_rows)

# Write valid toxic terms
with open(valid_toxic_terms_file, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(valid_toxic_rows)
