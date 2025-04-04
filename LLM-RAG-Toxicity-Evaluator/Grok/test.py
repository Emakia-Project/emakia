from langchain_xai import ChatXAI
from langchain.prompts import PromptTemplate
import os
import csv
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the API keys from environment variables
api_key = os.getenv("XAI_API_KEY")
if not api_key:
    raise ValueError("Grok API key - XAI_API_KEY not found in environment variables")

print(api_key)

# Initialize the Grok client
llm = ChatXAI(
    xai_api_key=api_key,
    model="grok-beta",
)

# Define the prompt template for sentiment analysis
template = """You are a sentiment analyst. Analyze the following statement and respond with either "positive" or "negative".

Statement: {content}

YOUR RESPONSE:
"""
prompt_template = PromptTemplate(input_variables=["content"], template=template)

# Create the RunnableSequence for sentiment analysis
content_chain = prompt_template | llm

# Path to your input and output CSV files
input_csv_file_path = 'tweets-labels-emojis.csv'
output_csv_file_path = 'outputgrok.csv'

# Function to process a batch of rows with retry logic
def process_batch(rows, csvwriter, outfile, max_retries=5):
    for row in rows:
        content = row[0]  # Assuming the content is in the first column
        retries = 0
        while retries < max_retries:
            try:
                # Invoke the LLM to analyze the content
                response = content_chain.invoke({"content": content})
                review = response.content

                # Write the processed data to the output file
                csvwriter.writerow([review, row[1], row[0]])
                print(f"Processed: {review}, {row[1]}, {row[0]}")
                break
            except Exception as e:
                print(f"Error processing row: {row}, Error: {e}")
                if 'too many requests' in str(e).lower():
                    retries += 1
                    delay = min(2 ** retries, 60)  # Exponential backoff
                    print(f"Too many requests. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print("An unexpected error occurred. Skipping row.")
                    break
        outfile.flush()  # Ensure data is written to the file immediately

# Read the input CSV file and process each row in batches
batch_size = 1000  # Adjust the batch size as needed
try:
    with open(input_csv_file_path, mode='r', newline='', encoding='utf-8') as infile, \
         open(output_csv_file_path, mode='a', newline='', encoding='utf-8') as outfile:

        csvreader = csv.reader(infile)
        csvwriter = csv.writer(outfile)
        
        batch = []
        for row in csvreader:
            batch.append(row)
            if len(batch) >= batch_size:
                process_batch(batch, csvwriter, outfile)
                batch = []
                time.sleep(70)  # Add delay to respect rate limits
        
        # Process any remaining rows
        if batch:
            process_batch(batch, csvwriter, outfile)
except Exception as e:
    print(f"An error occurred: {e}")
