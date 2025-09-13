import csv

# File paths
input_file = "gemini_valid_toxic_terms.csv"
single_output = "gemini_single_toxic_llm.csv"
multi_output = "gemini_multi_toxic_llm.csv"

# Arrays to hold rows
single_toxic_rows = []
multi_toxic_rows = []

# Read and classify
with open(input_file, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames

    for row in reader:
        toxic_count = 0
        for model in ["prediction_openai", "prediction_gemini", "prediction_grok", "prediction_llama", "prediction_deepseek"]:
            if row.get(model, "").strip().lower() == "toxic":
                toxic_count += 1

        if toxic_count == 1:
            single_toxic_rows.append(row)
        elif toxic_count > 1:
            multi_toxic_rows.append(row)

# Write single-toxic rows
with open(single_output, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(single_toxic_rows)

# Write multi-toxic rows
with open(multi_output, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(multi_toxic_rows)
