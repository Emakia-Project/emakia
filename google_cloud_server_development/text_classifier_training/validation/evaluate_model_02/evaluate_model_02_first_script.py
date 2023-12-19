# These 3 lines are for name variables in the name config file
import sys
sys.path.append('../../../config.py')
from config import YOUR_NAME

import csv
import json

# Function to extract tweet content from JSONL file
def extract_tweet_content(jsonl_file, output_csv, threshold):
    with open(jsonl_file, 'r', encoding='utf-8') as infile, open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['ID', 'Tweet Content', 'Threshold', 'Label'])  # Header for the CSV file

        for line_number, line in enumerate(infile, start=1):
            try:
                # Parse as JSON after replacing quotes
                data = json.loads(line)

                if 'tweet content' in data:
                    tweet_id = data['id']
                    tweet_content = data['tweet content']
                    confidences = data['prediction']['confidences']

                    label = '1' if confidences[0] > threshold else '0' if confidences[1] > threshold else 'threshold too high'

                    writer.writerow([tweet_id, tweet_content, threshold, label])
            except json.JSONDecodeError as e:
                print(f"Error in line {line_number}: {e}")
                continue

# Replace 'all_predictions.jsonl' with your JSONL file name
# Replace 'tweet_contents.csv' with the desired output CSV file name
extract_tweet_content(f'{YOUR_NAME}_all_prediction.jsonl', 'tweet_contents.csv', 0.75)

