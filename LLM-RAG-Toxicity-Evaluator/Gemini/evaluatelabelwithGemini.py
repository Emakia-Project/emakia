import os
import csv
import time
import textwrap
import sys
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

# Function to process a batch of lines
def process_batch(lines, csvwriter, outfile):
    for line in lines:
        row = line.strip().split(',')  # Split the line into columns
        if len(row) < 3:
            print("Skipping line due to insufficient columns:", line)
            continue
        content = row[2]  # Evaluate only the third column
        try:
            review = content_chain.invoke({"content": content})
            review_text = review.content.replace("'", "").replace("[", "").replace("]", "").replace("\"", "")
            if review_text == "":
                review_text = "No prediction"
            row_text = ', '.join([element.replace("'", "").replace("[", "").replace("]", "").replace("\"", "") for element in row])
            csvwriter.writerow([review_text, row_text])
            print(review_text, row_text)
        except Exception as e:
            print(f"Error processing line: {line}, Error: {e}")
        # Flush the writer to ensure all data is written
        outfile.flush()

# Main function to handle the input and output file arguments
def main(inputfile, outputfile):
    # Read the input text file and process the lines in batches of 100
    batch_size = 100
    with open(inputfile, mode='r', encoding='utf-8') as infile, \
         open(outputfile, mode='w', newline='', encoding='utf-8') as outfile:
        csvwriter = csv.writer(outfile)
        # Write the header to the output file
        csvwriter.writerow(['Review', 'Original Content'])
        batch = []
        for line in infile:
            batch.append(line)
            if len(batch) >= batch_size:
                process_batch(batch, csvwriter, outfile)
                batch = []
                time.sleep(70)  # Add delay to respect rate limits
        # Process any remaining lines
        if batch:
            process_batch(batch, csvwriter, outfile)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python script.py <inputfile> <outputfile>")
    else:
        main(sys.argv[1], sys.argv[2])
