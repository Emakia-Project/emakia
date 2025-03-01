import csv
import os
import time
from dotenv import load_dotenv
from langchain_core.runnables.base import Runnable
from langchain.prompts import PromptTemplate
from fireworks.client import Fireworks

# Load environment variables from .env file
load_dotenv()

# Retrieve the API keys from environment variables
fireworks_api_key = os.getenv("FIREWORKS_API_KEY")

# Retry logic
def invoke_with_retries(client, model, content, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": content}]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    raise Exception("All retry attempts failed")

# Initialize the Fireworks client wrapper with your API key
class FireworksWrapper(Runnable):
    def __init__(self, api_key):
        self.client = Fireworks(api_key=api_key)

    def invoke(self, input_data, *args, **kwargs):
        if isinstance(input_data, dict):
            content = input_data.get("content", "")
        else:
            content = str(input_data)

        return invoke_with_retries(self.client, "/sentientfoundation/models/dobby-mini-unhinged-llama-3-1-8b#accounts/sentientfoundation/deployments/81e155fc", content)

llm = FireworksWrapper(api_key=fireworks_api_key)

# Define the prompt template for sentiment analysis
template = """You are a sentiment analyst. Analyze the following statement and explain your choice of overall sentiment. 
Statement: {content} 
YOUR RESPONSE:"""
prompt_template = PromptTemplate(input_variables=["content"], template=template)

# Create the RunnableSequence for sentiment analysis
content_chain = prompt_template | llm

# Path to your input CSV file
input_csv_file_path = 'tweets-labels.csv'

# Path to your output CSV file
output_csv_file_path = 'output.csv'

# Function to process a batch of rows
def process_batch(rows, csvwriter):
    for row in rows:
        content = row[0]  # Assuming the content is in the first column
        try:
            review = content_chain.invoke({"content": content}).strip('"')
            csvwriter.writerow([review, row[1], row[0]])
            print(review, row[1], row[0])
        except Exception as e:
            print(f"Error processing row: {row}, Error: {e}")

# Read the input CSV file and process each row in batches
batch_size = 1000  # Adjust the batch size as needed
with open(input_csv_file_path, mode='r', newline='', encoding='utf-8') as infile, \
     open(output_csv_file_path, mode='w', newline='', encoding='utf-8') as outfile:
    
    csvreader = csv.reader(infile)
    csvwriter = csv.writer(outfile)
    
    # Write the header to the output file
    csvwriter.writerow(['Review', 'Original Content', 'Label'])
    
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
