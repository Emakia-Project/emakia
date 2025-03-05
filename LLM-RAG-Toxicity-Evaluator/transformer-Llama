import os
import csv
import time
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer
from langchain.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# Access and print value (if you still need this)
api_key = os.getenv("LLAMA_API_KEY")
if not api_key:
    raise ValueError("LLaMA API key not found in environment variables")
print(api_key)

# Load the Llama 3.1-8B-Instruct model from Hugging Face
model_name = "meta-llama/Llama-3.1-8B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)

# Define the prompt template for sentiment analysis
template = """You are a sentiment analyst. Analyze the following statement and respond with either "positive" or "negative".

Statement: {content}

YOUR RESPONSE:
"""
prompt_template = PromptTemplate(input_variables=["content"], template=template)

# Function to analyze sentiment
def analyze_sentiment(statement):
    prompt = prompt_template.format(content=statement)
    #print('statement')
    #print(statement)
    inputs = tokenizer(prompt, return_tensors="pt")
    attention_mask = inputs['attention_mask']
    outputs = model.generate(inputs.input_ids, max_length=100, do_sample=True, attention_mask=attention_mask, pad_token_id=tokenizer.eos_token_id)
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print('generated_text')
    print(generated_text)
    return generated_text

# Path to your input CSV file
input_csv_file_path = 'array_four.csv'

# Path to your output CSV file
output_csv_file_path = 'outputllama2.csv'

# Function to process a batch of rows
def process_batch(rows, csvwriter):
    for row in rows:
        content = row[2]  # Assuming the content is in the third column
        print("content")
        print(content)
        try:
            review = analyze_sentiment(content).strip('"')
            csvwriter.writerow([review, row[1], row[0], row[2]])
            print("review")
            print(review)
            #print( "row[1], row[0]")
            #print( row[1], row[0])
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
batch_size = 1000  # Adjust the batch size as needed
with open(input_csv_file_path, mode='r', newline='', encoding='utf-8') as infile, \
     open(output_csv_file_path, mode='w', newline='', encoding='utf-8') as outfile:
    
    csvreader = csv.reader(infile)
    csvwriter = csv.writer(outfile)
    
    # Write the header to the output file
    csvwriter.writerow(['Review', 'Original Content', 'Label'])
    
    # Skip the first line (header) of the input file
    infile.readline()
    
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
