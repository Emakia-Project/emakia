import os
import csv
import time
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Access and print value
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OpenAI API key not found in environment variables")

print(api_key)

# Initialize the OpenAI client
llm = OpenAI(temperature=0, openai_api_key=api_key)

# Define the prompt template for sentiment analysis
template = """You are a sentiment analyst. Analyze the following statement and respond with either "positive" or "negative".

Statement: {content}

YOUR RESPONSE:
"""
prompt_template = PromptTemplate(input_variables=["content"], template=template)

# Create the RunnableSequence for sentiment analysis
content_chain = prompt_template | llm

# Path to your input CSV file
input_csv_file_path = 'tweets-labels-emojis.csv'

# Path to your output CSV file
#output_csv_file_path = 'outputfeb15.csv'
output_csv_file_path = 'output-openai4.csv'

# Function to process a batch of rows
def process_batch(rows, csvwriter):
    for row in rows:
        content = row[0]  # Assuming the content is in the first column
        try:
            review = content_chain.invoke({"content": content}).strip('"')
            csvwriter.writerow([review.strip().replace('"', ''), row[1], row[0]])
            print(review, row[1], row[0])
        except Exception as e:
            print(f"Error processing row: {row}, Error: {e}")
        # Flush the writer to ensure all data is written
        outfile.flush()

# Function to process data with a delay every 1500 rows
def process_data(rows):
    for i, row in enumerate(rows):
        # Your processing logic here
        if (i + 1) % 1500 == 0:
            time.sleep(61)  # Wait for 1 minute

# Read the input CSV file and process each row in batches
batch_size = 100  # Adjust the batch size as needed
with open(input_csv_file_path, mode='r', newline='', encoding='utf-8') as infile, \
     open(output_csv_file_path, mode='a', newline='', encoding='utf-8') as outfile:
    
    csvreader = csv.reader(infile)
    csvwriter = csv.writer(outfile)
    
    # Skip lines up to 67630
    for _ in range(67630):
        next(csvreader)
    
    batch = []
    for row in csvreader:
        batch.append(row)
        if len(batch) >= batch_size:
            process_batch(batch, csvwriter)
            batch = []
            time.sleep(70)  # Add delay to respect rate limits
    
    # Process any remaining rows
    if batch:
        process_batch(batch, csvwriter)

# Main function to handle the input and output file arguments
def main():
    # Read the input text file and process the lines in batches of 100
    batch_size = 1000
    with open(input_csv_file_path, mode='r', encoding='utf-8') as infile, \
         open(output_csv_file_path, mode='a', newline='', encoding='utf-8') as outfile:
        csvwriter = csv.writer(outfile)
        # Skip lines up to 68799
        for _ in range(68799):
            next(infile)
        batch = []
        for line in infile:
            batch.append(line)
            if len(batch) >= batch_size:
                process_batch(batch, csvwriter)
                batch = []
                time.sleep(70)  # Add delay to respect rate limits
        # Process any remaining lines
        if batch:
            process_batch(batch, csvwriter)

if __name__ == "__main__":
    main()
