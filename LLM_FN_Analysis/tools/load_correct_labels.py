import csv

# Load correct labels from tweets-labels-emojis.csv
def load_correct_labels(path):
    label_map = {}
    with open(path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = row['text'].strip()
            label = row['Label'].strip()
            try:
                label_num = int(label)
                label_map[text] = label_num
            except ValueError:
                continue
    return label_map

# Replace labels in llm_predictions_log.csv
def correct_labels(input_predictions, label_map, output_path):
    with open(input_predictions, mode='r', encoding='utf-8') as infile, \
         open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            original_text = row['text'].strip()
            if original_text in label_map:
                row['label'] = label_map[original_text]
            writer.writerow(row)

# File paths
labels_file = "tweets-labels-emojis.csv"
predictions_file = "llm_predictions_log.csv"
output_file = "llm_predictions_log_new.csv"

# Run correction
label_map = load_correct_labels(labels_file)
correct_labels(predictions_file, label_map, output_file)

print("✅ Labels corrected and saved to llm_predictions_log_new.csv")
