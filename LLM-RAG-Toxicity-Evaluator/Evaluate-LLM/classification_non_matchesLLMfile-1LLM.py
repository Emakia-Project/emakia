import pandas as pd

# Load weights dynamically from CSV file (correct column name)
weights_file = "accuracy_results.csv"
try:
    weights_df = pd.read_csv(weights_file)
    
    # Change "Weight" to the correct column name: "Negative Percentage (%)"
    weights = {row["LLM Name"]: float(row["Negative Percentage (%)"]) for _, row in weights_df.iterrows()}
    print(f"Loaded weights: {weights}")  # Debugging print to verify weights
except Exception as e:
    print(f"Error reading {weights_file}: {e}")
    weights = {}  # Default to empty dictionary if file not found

# Load dataset
input_filename = "non_matchesAALLfile-1LLM_gemini.csv"

output_filename = "classification_non_matchesAALLfile-1LLM_gemini.csv"
df = pd.read_csv(input_filename)

# Initialize results
final_results = []

# Process each row
for _, row in df.iterrows():
    tempNegative = 0

    for key in weights.keys():
        if key in df.columns:  # Ensure column exists
            value = str(row[key]).strip().lower()  # Normalize case

            if value == "negative":
                tempNegative += weights.get(key, 0)  # Sum weights of negative predictions
                print(f"Row {_}: {key} -> {tempNegative}")  # Debugging print

    # Determine final classification based on threshold > 60
    classification = "negative" if tempNegative > 80 else "positive"

    # Store results
    final_results.append([classification] + row.tolist())

# Save results to file
columns = ["classification"] + df.columns.tolist()
results_df = pd.DataFrame(final_results, columns=columns)
results_df.to_csv(output_filename, index=False)

# Print confirmation
print(f"Results saved to {output_filename}")

