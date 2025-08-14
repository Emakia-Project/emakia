import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Google API key not found in environment variables")

# Initialize Gemini client
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=api_key,
    temperature=0,
)

# Define prompt template
template = """You are a sentiment analyst. Analyze the following statement and respond with either "positive" or "negative".

Statement: {content}
YOUR RESPONSE:"""
prompt_template = PromptTemplate(input_variables=["content"], template=template)
content_chain = prompt_template | llm

# Final callable for FN pipeline
def call_gemini(texts):
    predictions = []
    for text in texts:
        try:
            response = content_chain.invoke({"content": text})
            review_text = response.content.strip().lower()

            if len(review_text) > 10:
                predictions.append(0)  # Treat long or ambiguous responses as toxic
            elif "positive" in review_text or "neutral" in review_text or "happy" in review_text:
                predictions.append(1)
            elif "negative" in review_text or any(term in review_text for term in [
                "harmful", "sexual", "slur", "violence", "hate", "discriminatory", "abuse", "harassment",
                "graphic", "explicit", "threat", "danger", "profanity", "stalking", "bullying", "racism"
            ]):
                predictions.append(0)
            else:
                predictions.append(0)  # Default to toxic if uncertain
        except Exception as e:
            print(f"Error processing text: {text}, Error: {e}")
            predictions.append(0)  # Fail-safe: treat as toxic
    return predictions
