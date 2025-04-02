import os
import csv
import time
import re
import sys
from dotenv import load_dotenv
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

# Retrieve the API key from environment variables
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

def invoke_with_retries(client, content, retries=3, delay=5):
    if not isinstance(content, str):  # Validate the content type
        raise TypeError(f"Expected 'content' to be a string, but got {type(content)} instead.")

    for attempt in range(retries):
        try:
            print(f"Attempt {attempt + 1}: Sending content to model...\n{content}")
            response = client.invoke([{"role": "user", "content": content}])  # Ensure 'content' is correct
            #print(f"Model response: {response}")  # Debug log
            
            if hasattr(response, 'content'):  # Access the content attribute
                #print(f"Emakia Model response: {response.content}")
                debug = response.content
                print(f"Emakia Model response debug: {debug}")
                return debug
                #return response.content
            else:
                raise ValueError(f"Unexpected response format: {response}")
        except Exception as e:
            print(f"Error during API call: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    raise Exception("All retry attempts failed")


# Extract the toxic term from the model's response


def extract_toxic_term(response):
    if not isinstance(response, str):  # Validate input type
        return f"Unexpected response type: {type(response)}"

    match = re.search(r'The toxic term in the statement is \*\*"(.*?)"\*\*', response)
    if match:
        return match.group(1).strip()  # Extract the term inside quotation marks
    return "No toxic term found"

def check_toxicity(sentence):
    target_sentence = "This statement does not contain any toxic terms"
    if sentence.strip() == target_sentence:
        return "No toxic term found"
    return "Sentence does not match the target."


def read_list_from_csv(file_path):
    items = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row and row[0].strip():  # Assuming list is in the first column
                items.append(row[0].strip())
    return items 

def write_matches_and_non_matches_to_files(content_file, list_file, match_file, non_match_file, toxic_prompt_file, non_match_fileLLM_path):
    items_list = read_list_from_csv(list_file)

    with open(content_file, mode='r', encoding='utf-8') as content_file, \
         open(match_file, mode='w', newline='', encoding='utf-8') as match_file, \
         open(non_match_file, mode='w', newline='', encoding='utf-8') as non_match_file, \
         open(toxic_prompt_file, mode='w', newline='', encoding='utf-8') as toxic_prompt_file, \
         open(non_match_fileLLM_path, mode='w', newline='', encoding='utf-8') as non_match_fileLLM:

        content_reader = csv.reader(content_file)
        match_writer = csv.writer(match_file)
        non_match_writer = csv.writer(non_match_file)
        toxic_writer = csv.writer(toxic_prompt_file)
        non_match_fileLLM_writer = csv.writer(non_match_fileLLM)  # Added new writer

        match_writer.writerow(["MatchedItem", "predictionGemini","predictionDeepSeek","predictionLlama","predictionGrok","predictionOpenAI","label","content" ])
        non_match_writer.writerow([ "predictionGemini","predictionDeepSeek","predictionLlama","predictionGrok","predictionOpenAI","label","content"])
        toxic_writer.writerow(["ToxicTerm", "predictionGemini","predictionDeepSeek","predictionLlama","predictionGrok","predictionOpenAI","label","content"])
        non_match_fileLLM_writer.writerow([ "predictionGemini","predictionDeepSeek","predictionLlama","predictionGrok","predictionOpenAI","label","content"])  # New file header

        for row in content_reader:
            if len(row) > 6 and row[6].strip():
                words = row[6].split()
                match_found = False

                for item in items_list:
                    if item in words:
                        cleaned_row = [str(field).replace("[", "").replace("]", "").replace('"', '') for field in row]
                        match_writer.writerow([item, cleaned_row[0], cleaned_row[1], cleaned_row[2], cleaned_row[3], cleaned_row[4],cleaned_row[5], cleaned_row[6]])
                        match_found = True
                        break

                if not match_found:
                    non_match_writer.writerow(row)

                    if not isinstance(row[6], str):
                        print(f"Skipping invalid content: {row[6]} (type {type(row[6])})")
                        continue

                    content = row[6].strip()
                    prompt = f"""Identify the toxic term of the following sentence. Respond with the toxic term.

                    Statement: {content}
                    YOUR RESPONSE:"""

                    try:
                        toxic_term = invoke_with_retries(llm, prompt)

                        if len(toxic_term) > 30:
                            toxic_term = "No toxic term found"

                        cleaned_row = [field.replace("|", "") for field in row]

                        if toxic_term == "No toxic term found":
                            non_match_fileLLM_writer.writerow(cleaned_row)  # Write to new file
                        else:
                            toxic_writer.writerow([toxic_term, cleaned_row[0], cleaned_row[1], cleaned_row[2], cleaned_row[3], cleaned_row[4],cleaned_row[5], cleaned_row[6]])

                    except Exception as e:
                        print(f"Error invoking model for content: {content} - {e}")
                        toxic_writer.writerow(["Model invocation failed", row])

            else:
                non_match_writer.writerow(row)


# Example usage
content_file_path = 'file4.csv'
list_file_path = 'full_hatebase_element.csv'
match_file_path = 'matchesfile4-1LLM_gemini.csv'
non_match_file_path = 'non_matchesfile4-1LLM_gemini.csv'
non_match_fileLLM_path = 'non_matchesLLMfile4-1LLM_gemini.csv'
toxic_prompt_file_path = 'toxic_promptsfile4LLM_gemini.csv'

try:
    write_matches_and_non_matches_to_files(
        content_file_path,
        list_file_path,
        match_file_path,
        non_match_file_path,
        toxic_prompt_file_path,
        non_match_fileLLM_path
    )
except KeyboardInterrupt:
    print("\nProcess interrupted by user.")
    sys.exit(0)

