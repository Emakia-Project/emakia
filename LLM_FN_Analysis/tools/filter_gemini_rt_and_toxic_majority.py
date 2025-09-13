import csv

# File paths
input_file = "gemini_flagged_rt_or_none.csv"
toxic_output = "gemini_rt_or_none_likely_toxic.csv"
clean_output = "gemini_rt_or_none_likely_clean.csv"

# Arrays to hold rows
likely_toxic_rows = []
likely_clean_rows = []

# Read and classify
with open(input_file, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames

    for row in reader:
        toxic_count = 0
        for model in ["prediction_openai", "prediction_gemini", "prediction_grok", "prediction_llama", "prediction_deepseek"]:
            if row.get(model, "").strip().lower() == "toxic":
                toxic_count += 1

        if toxic_count >= 3:
            likely_toxic_rows.append(row)
        else:
            likely_clean_rows.append(row)

# Write toxic rows
with open(toxic_output, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(likely_toxic_rows)

# Write clean rows
with open(clean_output, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(likely_clean_rows)
