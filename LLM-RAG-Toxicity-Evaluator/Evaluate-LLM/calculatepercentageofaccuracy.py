import csv

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
                if prediction == "negative" and label == 0:
                    correct_counts[llm] += 1

# Initialize dictionaries for counting occurrences
positive_counts = {llm: 0 for llm in ["predictionGemini", "predictionDeepSeek", "predictionLlama", "predictionGrok", "predictionOpenAI"]}
negative_counts = {llm: 0 for llm in ["predictionGemini", "predictionDeepSeek", "predictionLlama", "predictionGrok", "predictionOpenAI"]}
correct_counts = {llm: 0 for llm in ["predictionGemini", "predictionDeepSeek", "predictionLlama", "predictionGrok", "predictionOpenAI"]}
total_rows = [0]  # Track total rows processed

# Define file paths
file1_path = "matchesfile3-1LLM_gemini.csv"
file2_path = "toxic_promptsfile3LLM_gemini.csv"
file3_path = "matchesfile2-1LLM_gemini.csv"
file4_path = "toxic_promptsfile2LLM_gemini.csv"
file5_path = "matchesfile4-1LLM_gemini.csv"
file6_path = "toxic_promptsfile4LLM_gemini.csv"

# Process both files
read_and_count_predictions(file1_path, positive_counts, negative_counts, total_rows, correct_counts)
read_and_count_predictions(file2_path, positive_counts, negative_counts, total_rows, correct_counts)
read_and_count_predictions(file3_path, positive_counts, negative_counts, total_rows, correct_counts)
read_and_count_predictions(file5_path, positive_counts, negative_counts, total_rows, correct_counts)
read_and_count_predictions(file6_path, positive_counts, negative_counts, total_rows, correct_counts)

# Compute accuracy for each LLM based on the formula: (negative count / total rows) * 100
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
