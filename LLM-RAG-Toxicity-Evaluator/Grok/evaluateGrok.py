from langchain_xai import ChatXAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables.base import RunnableSequence
from dotenv import load_dotenv
import os
import csv
import time

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
    model="grok-2-1212",
)

# Define the prompt template for sentiment analysis
template = """You are a sentiment analyst. Analyze the following statement and respond with either "positive" or "negative".

Statement: {content}

YOUR RESPONSE:
"""
prompt_template = PromptTemplate(input_variables=["content"], template=template)

# Create the RunnableSequence for sentiment analysis
content_chain = prompt_template | llm

# Retry logic
def invoke_with_retries(content_chain, content, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = content_chain.invoke({"content": content})
            return response
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if 'too many requests' in str(e).lower():
                time.sleep(min(2 ** attempt, delay))
            else:
                raise
    raise Exception("All attempts failed.")


# Path to your input CSV file
input_csv_file_path = 'array_three.csv'

# Path to your output CSV file
output_csv_file_path = 'outputgrokarraythree.csv'




def process_batch(rows, csvwriter, outfile, max_retries=5):
    for row in rows:
        content = row[2]  # Assuming the content is in the third column
        print(f"Processing: {content}")
        retries = 0
        delay = 10  # Start with an initial delay of 10 seconds
        while retries < max_retries:
            try:
                response = invoke_with_retries(content_chain, content)
                review = response.content
                print(f"Processed: {review}")
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

                # Write processed data to output CSV
                csvwriter.writerow([review, row[0], row[1], row[2]])
                outfile.flush()  # Save data immediately
                break  # Exit the retry loop on success
            except Exception as e:
                print(f"Error processing row: {row}, Error: {e}")
                if 'too many requests' in str(e).lower():
                    retries += 1
                    print(f"Too many requests. Retrying in {delay} seconds...")
                    time.sleep(delay)  # Wait before retrying
                    delay = min(delay * 2, 60)  # Exponential backoff (max 60 seconds)
                else:
                    print("Unexpected error occurred. Skipping row.")
                    break





# Function to process data with a delay every 1500 rows
def process_data(rows):
    for i, row in enumerate(rows):
        if (i + 1) % 1500 == 0:
            time.sleep(61)  # Wait for 1 minute

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

def main():
    batch_size = 1000
    try:
        with open(input_csv_file_path, mode='r', newline='', encoding='utf-8') as infile, \
             open(output_csv_file_path, mode='a', newline='', encoding='utf-8') as outfile:
            
            csvreader = csv.reader(infile)  # Use csvreader consistently
            csvwriter = csv.writer(outfile)

            batch = []
            for row in csvreader:  # Process rows using csvreader, not infile
                if not row:  # Skip empty lines
                    continue

                batch.append(row)
                if len(batch) >= batch_size:
                    process_batch(batch, csvwriter, outfile)
                    batch = []  # Reset batch after processing

            # Process any remaining rows
            if batch:
                process_batch(batch, csvwriter, outfile)
                
            print("Processing completed successfully!")
    
    except Exception as e:
        print(f"An error occurred in main: {e}")


if __name__ == "__main__":
    main()

