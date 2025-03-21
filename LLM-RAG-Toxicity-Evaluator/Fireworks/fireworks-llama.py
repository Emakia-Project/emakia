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
input_csv_file_path = 'array_three.csv'

# Path to your output CSV file
output_csv_file_path = 'llama-array_three.csv'

# Function to process rows starting from a specific position
def process_rows_from_position(csvreader, start_position, csvwriter):
    current_row = 0  # Track row index
    for row in csvreader:
        current_row += 1
        # Skip rows until the start position
        if current_row < start_position:
            continue

        # Process rows from the start position onwards
        try:
            # Ensure the row has sufficient columns
            if len(row) < 3:
                continue

            content = row[2].strip()  # Assuming the text content is in the third column

            # Get sentiment review
            review = content_chain.invoke({"content": content}).strip('"')



# Convert the review to lowercase to handle case insensitivity
            review_lower = review.lower()

            if "positive" in review_lower or "happy" in review_lower:
                review = "positive"
            elif "negative" in review_lower:
                review = "negative"
            elif "neutral" in review_lower:
                review = "neutral"
            elif any(term in review_lower for term in [
    "harmful", "sexual comment", "profanity", "reach out for help", 
    "information of a minor", "dangerous", "violence", "hatred", "discriminatory",
    "illegal", "theft", "harassment", "abuse", "stalking", "substance abuse", 
    "bullying", "contains a minor", "danger", "threat", "crime", "discriminator",
    "romantic relationship with a minor", "sexualisation of minors", "hate",
    "stereotype a group of people based on their race", "graphic", 
    "explicit", "derogatory", "sexual attraction to a minor", "sexualizes",
    "sexual references to a minor", "cunnilingus damn", "specific punishment",
    "derogatory or sexist", "hate speech", "defamatory", "derogatory", "spam",
    "to condone or promote harm towards an individual", "biased perspective",
    "potentially suggestive statement", "sexist language", "sexist", "hateful",
    "discriminates against women", "discriminate", "sexism", "hitting a child"
    "hoax", "a conspiracy theory","sexual intercourse"
]):
                review = "negative"
            else:
                review += "not defined"

           
            # Write processed row to the output file
            csvwriter.writerow([review, row[0], row[1], row[2]])
        except Exception:
            pass

# Read the input CSV file and process rows starting from row 52,607
start_position = 0
with open(input_csv_file_path, mode='r', newline='', encoding='utf-8') as infile, \
     open(output_csv_file_path, mode='w', newline='', encoding='utf-8') as outfile:
    
    csvreader = csv.reader(infile)
    csvwriter = csv.writer(outfile)
    
    # Write the header to the output file
    csvwriter.writerow(['Review', 'Sentiment', 'Original Content', 'Text'])
    
    # Process rows starting from the specified position
    process_rows_from_position(csvreader, start_position, csvwriter)
