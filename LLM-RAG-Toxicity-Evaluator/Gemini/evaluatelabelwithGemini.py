import os
import csv
import time
import textwrap
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)

# Load environment variables
load_dotenv()

# Access and print value
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Google API key not found in environment variables")
print(api_key)

# Initialize the Gemini client
def get_gemini_model():
    return ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=api_key,
        temperature=0,
    )

llm = get_gemini_model()

# Define the prompt template for sentiment analysis
template = """You are a sentiment analyst. Analyze the following statement and respond with either "positive" or "negative".
Statement: {content}
YOUR RESPONSE:"""

prompt_template = PromptTemplate(input_variables=["content"], template=template)

# Create the RunnableSequence for sentiment analysis
content_chain = prompt_template | llm

# Path to your input csv file
input_text_file_path = 'array_three.csv'

# Path to your output CSV file
output_csv_file_path = 'outputsmallarraygemini.csv'

# Function to process a batch of lines
def process_batch(lines, csvwriter):
    for line in lines:
        content = line.strip()  # Remove leading/trailing whitespace
        try:
            review = content_chain.invoke({"content": content})
            csvwriter.writerow([review.content, content])
            print(review.content, content)
        except Exception as e:
            print(f"Error processing line: {line}, Error: {e}")
        # Flush the writer to ensure all data is written
        outfile.flush()

# Read the input text file and process the first 20 lines
batch_size = 1000  # Adjust the batch size as needed
line_count = 0
with open(input_text_file_path, mode='r', encoding='utf-8') as infile, \
     open(output_csv_file_path, mode='w', newline='', encoding='utf-8') as outfile:
    csvwriter = csv.writer(outfile)
    # Write the header to the output file
    csvwriter.writerow(['Review', 'Original Content'])
    batch = []
    for line in infile:
        if line_count >= 20:
            break
        batch.append(line)
        line_count += 1
        if len(batch) >= batch_size:
            process_batch(batch, csvwriter)
            batch = []
            time.sleep(70)  # Add delay to respect rate limits
    # Process any remaining lines
    if batch:
        process_batch(batch, csvwriter)
