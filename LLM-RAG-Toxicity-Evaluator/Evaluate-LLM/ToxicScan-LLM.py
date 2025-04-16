import csv

# Define file paths
file1_path = "non_matchesAALLfile-1LLM_gemini.csv"
file2_path = "toxic_promptsALLfileLLM_gemini.csv"
file3_path = "matchesALLfile-1LLM_gemini.csv"

def read_and_count_predictions(file_path, positive_counts, negative_counts, total_rows, correct_counts):
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            total_rows[0] += 1  # Increment total row count
            label = row["label"].strip().lower()  # Normalize label format

            for llm in positive_counts.keys():
                prediction = row[llm].strip().lower()

                if prediction == "positive":
                    positive_counts[llm] += 1
                elif prediction == "negative":
                    negative_counts[llm] += 1

                # Count correct negative predictions per LLM
                if prediction == "negative" and label == "negative":
                    correct_counts[llm] += 1

# Initialize dictionaries for counting occurrences
llm_names = ["predictionGemini", "predictionDeepSeek", "predictionLlama", "predictionGrok", "predictionOpenAI"]
positive_counts = {llm: 0 for llm in llm_names}
negative_counts = {llm: 0 for llm in llm_names}
correct_counts = {llm: 0 for llm in llm_names}
total_rows = [0]  # Track total rows processed

print("Correct negative predictions per LLM:", correct_counts)
print("Total rows processed:", total_rows[0])



# Process all three files
for file_path in [file1_path, file2_path, file3_path]:
    read_and_count_predictions(file_path, positive_counts, negative_counts, total_rows, correct_counts)

# Compute accuracy for each LLM
#accuracy_per_llm = {llm: (correct_counts[llm] / total_rows[0]) * 100 if total_rows[0] > 0 else 0 for llm in correct_counts}
accuracy_per_llm = {llm: (negative_counts[llm] / total_rows[0]) * 100 if total_rows[0] > 0 else 0 for llm in negative_counts}
# Convert dictionaries to arrays
positive_array = list(positive_counts.values())
negative_array = list(negative_counts.values())
accuracy_array = list(accuracy_per_llm.values())

# Print results
print("Total rows processed:", total_rows[0])
print("Positive predictions count:", positive_array)
print("Negative predictions count:", negative_array)
print("Accuracy for each LLM:", accuracy_array)
