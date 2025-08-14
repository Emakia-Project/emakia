"""
Grok API Wrapper

This module provides a wrapper for the Grok API to simplify LLM interactions.
"""

import os
import json
import requests
from typing import Dict, Any, Optional


def call_grok(
    prompt: str,
    input_data: Dict[str, Any],
    model: str = "grok-beta",
    temperature: float = 0.1,
    max_tokens: int = 1000,
    **kwargs
) -> Dict[str, Any]:
    """
    Call Grok API with the given prompt and input data.
    
    Args:
        prompt: The task description or prompt for the LLM
        input_data: Input data to be processed
        model: Grok model to use (default: grok-beta)
        temperature: Sampling temperature (default: 0.1)
        max_tokens: Maximum tokens in response (default: 1000)
        **kwargs: Additional arguments for Grok API
        
    Returns:
        Dictionary containing the LLM response
    """
    
    # Check for API key
    api_key = os.getenv('GROK_API_KEY')
    if not api_key:
        raise ValueError("GROK_API_KEY environment variable not set")
    
    # Check for API endpoint
    api_endpoint = os.getenv('GROK_API_ENDPOINT')
    if not api_endpoint:
        raise ValueError("GROK_API_ENDPOINT environment variable not set")
    
    # Prepare the full prompt
    full_prompt = f"""
{prompt}

Input data:
{json.dumps(input_data, indent=2)}

Please provide your response in the following JSON format:
{{
    "response": "your main response here",
    "confidence": 0.95,
    "reasoning": "brief explanation of your reasoning"
}}
"""
    
    # Prepare request payload
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant that provides structured responses in JSON format."},
            {"role": "user", "content": full_prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        **kwargs
    }
    
    # Set headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # Make API call
        response = requests.post(
            api_endpoint,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        # Check for HTTP errors
        response.raise_for_status()
        
        # Parse response
        response_data = response.json()
        
        # Extract content from response
        if "choices" in response_data and len(response_data["choices"]) > 0:
            response_content = response_data["choices"][0]["message"]["content"]
        else:
            raise RuntimeError("Unexpected response format from Grok API")
        
        # Try to parse JSON response
        try:
            parsed_response = json.loads(response_content)
            return parsed_response
        except json.JSONDecodeError:
            # If JSON parsing fails, return as plain text
            return {
                "response": response_content,
                "confidence": 0.5,
                "reasoning": "Response could not be parsed as JSON"
            }
            
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Grok API request failed: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Grok API call failed: {str(e)}")


def call_grok_simple(
    prompt: str,
    input_data: str,
    model: str = "grok-beta",
    **kwargs
) -> str:
    """
    Simplified Grok API call that returns just the text response.
    
    Args:
        prompt: The task description or prompt
        input_data: Input data as a string
        model: Grok model to use
        **kwargs: Additional arguments for Grok API
        
    Returns:
        String response from the LLM
    """
    
    response = call_grok(prompt, {"input": input_data}, model, **kwargs)
    return response.get("response", str(response))
