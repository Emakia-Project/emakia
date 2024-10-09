import pandas as pd
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import torch

# Load pre-trained models
model = SentenceTransformer('all-MiniLM-L6-v2')
classifier = pipeline('text-classification', model='unitary/toxic-bert', device=0 if torch.cuda.is_available() else -1)

# Function to analyze a string
def analyze_string(input_string):
    # Classify the input string
    classification = classifier(input_string)
    
    # Check if the input string is harassing
    is_harassing = any(label['label'] == 'toxic' and label['score'] > 0.5 for label in classification)
    
    return "harassing" if is_harassing else "neutral"

# Read the CSV file
file_path = 'XXXX change to the correct path and file - not_found_items-in-array-3.csv'
df = pd.read_csv(file_path, header=None, encoding='latin1')

# Analyze the second column and store results
results = []
for content in df[2]:
    print(content)
    result = analyze_string(content)
    results.append(result)

# Add results to the DataFrame
df['result'] = results

# Write the results to a new CSV file
df.to_csv('outputRAG_array3.csv', index=False, header=False)

print("Analysis complete. Results saved to 'outputRAG.csv'.")
