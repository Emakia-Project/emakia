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

        return invoke_with_retries(self.client, "accounts/fireworks/models/llama-v3p1-8b-instruct", content)

llm = FireworksWrapper(api_key=fireworks_api_key)

# Define the prompt template for sentiment analysis
template = """You are a sentiment analyst. Analyze the following statement and respond with either "positive" or "negative".

Statement: {content} 
YOUR RESPONSE:"""
prompt_template = PromptTemplate(input_variables=["content"], template=template)

# Create the RunnableSequence for sentiment analysis
content_chain = prompt_template | llm

# Path to your input CSV file
input_csv_file_path = 'tweets-labels-emojis.csv'

# Path to your output CSV file
output_csv_file_path = 'llama-v3p1-8b-instruct-outputtweets-labels.csv'

# Function to process rows starting from a specific position
#def process_rows_from_position(start_position, csvreader, csvwriter):
def process_rows_from_position( csvreader, start_position csvwriter):
    current_row = 0  # Track row index
    for row in csvreader:
        current_row += 1
        # Skip rows until the start position
        if current_row < start_position:
            continue

        # Process rows from the start position onwards
        content = row[0]  # Assuming the content is in the first column
        try:
            review = content_chain.invoke({"content": content}).strip('"')

            # Check if the length of the review is greater than 10
            if len(review) > 5:
                # Search for terms such as "positive", "negative", or "neutral"
                if "positive" in review.lower():
                    review = "positive"
                elif any(term in review.lower() for term in ["harmful", "sensitive","derogatory", "dangerous", "violence", "hatred"]):
                    review = "negative"
                elif "neutral" in review.lower():
                    review = "neutral"
                elif "negative" in review.lower():
                    review = "negative"
                else:
                    review = review

            csvwriter.writerow([review, row[1], row[0]])
            print(f" {review}, {row[1]}, {row[0]}")
        except Exception as e:
            print(f"Error processing row  {row}, Error: {e}")

# Read the input CSV file and process rows starting from row 52,607
start_position = 0
with open(input_csv_file_path, mode='r', newline='', encoding='utf-8') as infile, \
     open(output_csv_file_path, mode='w', newline='', encoding='utf-8') as outfile:
    
    csvreader = csv.reader(infile)
    csvwriter = csv.writer(outfile)
    
    # Write the header to the output file
    csvwriter.writerow(['Review', 'Original Content', 'Label'])
    
    # Process rows starting from the specified position
    process_rows_from_position(start_position, csvreader, csvwriter)
    #process_rows_from_position( csvreader, csvwriter)
