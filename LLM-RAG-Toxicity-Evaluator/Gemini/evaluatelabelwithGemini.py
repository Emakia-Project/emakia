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
        model="gemini-2.0-flash",
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

# Main function to handle the input and output file arguments
def main(inputfile, outputfile):
    batch_size = 100  # Define batch size for memory efficiency

    with open(inputfile, mode='r', encoding='utf-8') as infile, \
         open(outputfile, mode='w', newline='', encoding='utf-8') as outfile:
        csvwriter = csv.writer(outfile)

        # Write the header to the output file
        csvwriter.writerow(['Gemini', 'OpenAI', 'Label', 'Content'])

        # Read all lines from the input file
        lines = infile.readlines()

        # Skip the header
        header = lines[0]  # The first line is the header
        print(f"Skipping header: {header}")
        lines = lines[1:]  # Exclude the header from processing

        # Process lines in batches
        batch = []
        for line in lines:
            batch.append(line)
            if len(batch) >= batch_size:
                process_batch(batch, csvwriter, outfile)
                batch = []

        # Process any remaining lines
        if batch:
            process_batch(batch, csvwriter, outfile)

# Function to process a batch of lines
def process_batch(lines, csvwriter, outfile):
    for line in lines:
        row = line.strip().split(',')  # Split the line into columns
        if len(row) < 3:
            print(f"Skipping line due to insufficient columns: {line}")
            continue

        # Evaluate only the third column for sentiment
        content = row[2]
        try:
            # Invoke the content chain for sentiment analysis
            review = content_chain.invoke({"content": content})

            # Add additional processing logic here (if needed)
        except Exception as e:
            print(f"Error processing content: {content}, Error: {e}")
def main(inputfile, outputfile):
    batch_size = 100  # Define batch size for memory efficiency

    with open(inputfile, mode='r', encoding='utf-8') as infile, \
         open(outputfile, mode='w', newline='', encoding='utf-8') as outfile:
        csvwriter = csv.writer(outfile)

        # Write the header to the output file
        csvwriter.writerow(['Gemini', 'OpenAI', 'Label', 'Content'])

        # Read all lines from the input file
        lines = infile.readlines()

        # Skip the header
        header = lines[0]  # The first line is the header
        print(f"Skipping header: {header}")
        lines = lines[1:]  # Exclude the header from processing
#

        # Start processing from line 310 (adjusting for zero-based index)
        #start_line = 310
        #lines = lines[start_line - 1:] 
        # Process lines in batches
        batch = []
        for line in lines:
            batch.append(line)
            if len(batch) >= batch_size:
                process_batch(batch, csvwriter, outfile)
                batch = []

        # Process any remaining lines
        if batch:
            process_batch(batch, csvwriter, outfile)

# Function to process a batch of lines
def process_batch(lines, csvwriter, outfile):
    for line in lines:
        row = line.strip().split(',')  # Split the line into columns
        if len(row) < 3:
            print(f"Skipping line due to insufficient columns: {line}")
            continue

        # Evaluate only the third column for sentiment
        content = row[2]
        try:
            # Invoke the content chain for sentiment analysis
            review = content_chain.invoke({"content": content})

           # Clean and format the data
            review_text = review.content.strip().replace("\n", " ").replace('"', '').replace("'", '')
            review_lower = review_text.lower()
            print(len(review_text))
            print(review_text)
            if (len(review_text)) > 10:
                 print("not defined - hardcoded")
                 prediction = "not defined"
                 print(prediction)
            elif "positive" in review_lower or "happy" in review_lower:
                 prediction = "positive"
            elif "negative" in review_lower:
                 prediction = "negative"
            elif "neutral" in review_lower:
                 prediction = "neutral"
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
                    prediction = "negative"
            else:
                    prediction = "not defined"
           
            cleaned_row = [col.strip().replace("\n", " ").replace('"', '').replace("'", '') for col in row]
            
            # Write the formatted row to the CSV
            csvwriter.writerow([prediction] + cleaned_row)
            print(f"Processed row: {[prediction] + cleaned_row}")
        except Exception as e:
            print(f"Error processing line: {line}, Error: {e}")

        # Flush the writer to ensure immediate writing
        outfile.flush()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python script.py <inputfile> <outputfile>")
    else:
        main(sys.argv[1], sys.argv[2])
