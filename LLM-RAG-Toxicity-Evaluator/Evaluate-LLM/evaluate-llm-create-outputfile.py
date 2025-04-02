import csv

# Function to read specific columns (prediction, OpenAI, label, content) from a file
def read_file(file_path, prediction_column_name):
    data = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as infile:
        csvreader = csv.reader(infile)
        next(csvreader)  # Skip the header
        for row in csvreader:
            if len(row) >= 4:  # Ensure the row has enough columns
                # Append the prediction column (column[0]) and other shared columns
                data.append({
                    prediction_column_name: row[0].strip(),  # Prediction from this specific file
                    "predictionOpenAI": row[1].strip(),
                    "label": row[2].strip(),
                    "content": row[3].strip()
                })
    return data

# Paths to input CSV files
file1_path = 'deepseek-array_three.csv'  # DeepSeek file
file2_path = 'llama-array_three.csv'  # Llama file
file3_path = 'outputarraythreeGemini.csv'  # Gemini file
file4_path = 'outputgrokarraythree.csv'  # Grok file

# Read data from each file
file1_data = read_file(file1_path, "predictionDeepSeek") if file1_path else []
file2_data = read_file(file2_path, "predictionLlama") if file2_path else []
file3_data = read_file(file3_path, "predictionGemini") if file3_path else []
file4_data = read_file(file4_path, "predictionGrok") if file4_path else []

# Ensure all lists are the same length by padding with empty dictionaries
max_length = max(len(file1_data), len(file2_data), len(file3_data), len(file4_data))
file1_data += [{}] * (max_length - len(file1_data))
file2_data += [{}] * (max_length - len(file2_data))
file3_data += [{}] * (max_length - len(file3_data))
file4_data += [{}] * (max_length - len(file4_data))

# Combine data into rows for output
output_data = []
for i in range(max_length):
    output_data.append([
        file3_data[i].get("predictionGemini", ""),  # Prediction from Gemini
        file1_data[i].get("predictionDeepSeek", ""),  # Prediction from DeepSeek
        file2_data[i].get("predictionLlama", ""),  # Prediction from Llama
        file4_data[i].get("predictionGrok", ""),  # Prediction from Grok
        file1_data[i].get("predictionOpenAI", ""),  # Label (consistent across files)
        file1_data[i].get("label", ""),  # Label (consistent across files)
        file1_data[i].get("content", "")  # Content (consistent across files)
    ])

# Path to the output file
output_file_path = 'output.csv'

# Write combined data to the output file
with open(output_file_path, mode='w', newline='', encoding='utf-8') as outfile:
    csvwriter = csv.writer(outfile)
    # Write the header
    csvwriter.writerow([
        'predictionGemini', 'predictionDeepSeek', 'predictionLlama', 'predictionGrok', 'predictionOpenAI','label', 'content'
    ])
    # Write the rows
    csvwriter.writerows(output_data)

print(f"Data successfully written to {output_file_path}")
