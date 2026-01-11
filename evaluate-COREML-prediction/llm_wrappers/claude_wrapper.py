import os
import time
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    raise ValueError("Anthropic API key not found in environment variables")

# Initialize Claude client
client = Anthropic(api_key=api_key)

# System prompt for sentiment analysis
SYSTEM_PROMPT = """You are a sentiment analyst. Analyze the following statement and respond with either "positive" or "negative".

YOUR RESPONSE:"""

# Retry logic with exponential backoff
def invoke_with_retries(client, content, retries=3, delay=10):
    for attempt in range(retries):
        try:
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=100,
                temperature=0,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": f"Statement: {content}"}
                ]
            )
            return message.content[0].text
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if 'rate' in str(e).lower() or 'too many' in str(e).lower():
                time.sleep(min(2 ** attempt, delay))
            elif attempt < retries - 1:
                time.sleep(2)
            else:
                raise
    raise Exception("All attempts failed.")

def call_claude(texts):
    """
    Call Claude API for batch predictions
    
    Args:
        texts: List of text strings to classify
    
    Returns:
        List of predictions (1 for positive/neutral, 0 for negative/toxic)
    """
    predictions = []
    
    for i, text in enumerate(texts):
        try:
            response = invoke_with_retries(client, text).lower()
            
            # Interpret response into binary prediction
            if any(term in response for term in ["positive", "neutral", "happy"]):
                predictions.append(1)
            elif any(term in response for term in [
                "negative", "harmful", "sexual", "slur", "violence", "hate", 
                "discriminatory", "abuse", "harassment", "graphic", "explicit", 
                "threat", "danger", "profanity", "stalking", "bullying", "racism"
            ]):
                predictions.append(0)
            else:
                print(f"⚠️ Unclear response from Claude on input {i}: {response}")
                predictions.append(0)  # Default to toxic if uncertain
                
        except Exception as e:
            print(f"❌ Claude failed on input {i}: {text[:100]}")
            print(f"   ↪️ Error: {e}")
            predictions.append(None)  # Preserve index alignment
        
        time.sleep(1.2)  # Respect rate limits
    
    return predictions