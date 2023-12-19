from evaluate_model_02_first_script import extract_tweet_content
from evaluate_model_02_second_script import evaluate
import os
import shutil
import pandas as pd

YOUR_NAME = 'mie'
THRESHOLDS = [0.600, 0.750, 0.775, 0.800, 0.825, 0.850, 0.900]
input_jsonl_file = f'{YOUR_NAME}_all_prediction.jsonl'
tweet_content_file = 'tweet_contents.csv'

# Extract folder name from the input_jsonl_file
folder_name = os.path.splitext(input_jsonl_file)[0]

# Create a folder if it doesn't exist
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Move tweet_contents_file to the created folder if it doesn't exist there
destination_tweet_contents = os.path.join(folder_name, tweet_content_file)
if not os.path.exists(destination_tweet_contents):
    shutil.move(tweet_content_file, destination_tweet_contents)

for t in THRESHOLDS:
    extract_tweet_content(input_jsonl_file, destination_tweet_contents, t)
    evaluate(destination_tweet_contents, t)

    threshold_filename = f'batchvalidation-threshold-{str(t).split(".")[1]}.csv'
    output_path = os.path.join(folder_name, threshold_filename)

    # Move the file to the created folder
    os.rename(threshold_filename, output_path)

    validated_harassment_count = 0  # Initialize count

    # Check if the file exists before attempting to read it
    if os.path.exists(output_path):
        df = pd.read_csv(output_path)
        validated_harassment_count = df[df['validation'] == 'validated harassment'].shape[0]

    print(f"Validation completed for threshold {t}.")
    print(f"File: {output_path} - {validated_harassment_count} validated harassment")

# Remove __pycache__ folder if it exists
pycache_folder = os.path.join(os.getcwd(), '__pycache__')
if os.path.exists(pycache_folder):
    shutil.rmtree(pycache_folder)
