import csv

# Define file paths
file1_path = "non_matchesAALLfile-1LLM_gemini.csv"
file2_path = "toxic_promptsALLfileLLM_gemini.csv"
file3_path = "matchesALLfile-1LLM_gemini.csv"
output_file_path = "accuracy_results.csv"

# Initialize dictionaries for counting occurrences
llm_names = ["predictionGemini", "predictionDeepSeek", "predictionLlama", "predictionGrok", "predictionOpenAI"]
negative_counts = {llm: 0 for llm in llm_names}
total_rows = 0  # Changed from a list

# Read CSV data and count predictions
def read_and_count_predictions(file_path, negative_counts):
    global total_rows  # Ensure persistence
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            if not reader.fieldnames:
                print(f"Error: No columns found in {file_path}")
                return  # Prevents crashes if CSV is empty

            for row in reader:
                total_rows += 1
                label = row.get("label", "").strip().lower()  # Handle missing keys gracefully
                
                for llm in llm_names:
                    prediction = row.get(llm, "").strip().lower()
                    if prediction == "negative":
                        negative_counts[llm] += 1

        print(f"Completed processing {file_path}, Total rows: {total_rows}")

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

# Process files
for file_path in [file1_path, file2_path, file3_path]:
    read_and_count_predictions(file_path, negative_counts)

# Compute accuracy
accuracy_per_llm = {llm: (negative_counts[llm] / total_rows) * 100 if total_rows > 0 else 0 for llm in negative_counts}

# Write accuracy results to a CSV file
def write_accuracy_to_file(output_file_path, accuracy_data):
    try:
        with open(output_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["LLM Name", "Negative Percentage (%)"])
            for llm, percentage in accuracy_data.items():
                writer.writerow([llm, round(percentage, 2)])  # Round to 2 decimal places
        print(f"Accuracy results saved to {output_file_path}")
    except Exception as e:
        print(f"Error writing to {output_file_path}: {e}")

write_accuracy_to_file(output_file_path, accuracy_per_llm)

# Print results
print("Total rows processed:", total_rows)
print("Negative predictions count:", negative_counts)
print("Accuracy for each LLM:", accuracy_per_llm)
