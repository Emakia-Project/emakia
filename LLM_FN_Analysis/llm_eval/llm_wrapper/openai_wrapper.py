"""
OpenAI API Wrapper

This module provides a wrapper for the OpenAI API to simplify LLM interactions.
"""

import os
import json
from typing import Dict, Any, Optional
import openai
from openai import OpenAI


def call_openai(
    prompt: str,
    input_data: Dict[str, Any],
    model: str = "gpt-4",
    temperature: float = 0.1,
    max_tokens: int = 1000,
    **kwargs
) -> Dict[str, Any]:
    """
    Call OpenAI API with the given prompt and input data.
    
    Args:
        prompt: The task description or prompt for the LLM
        input_data: Input data to be processed
        model: OpenAI model to use (default: gpt-4)
        temperature: Sampling temperature (default: 0.1)
        max_tokens: Maximum tokens in response (default: 1000)
        **kwargs: Additional arguments for OpenAI API
        
    Returns:
        Dictionary containing the LLM response
    """
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
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
    
    try:
        # Make API call
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant that provides structured responses in JSON format."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Extract response content
        response_content = response.choices[0].message.content
        
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
            
    except Exception as e:
        raise RuntimeError(f"OpenAI API call failed: {str(e)}")


def call_openai_simple(
    prompt: str,
    input_data: str,
    model: str = "gpt-4",
    **kwargs
) -> str:
    """
    Simplified OpenAI API call that returns just the text response.
    
    Args:
        prompt: The task description or prompt
        input_data: Input data as a string
        model: OpenAI model to use
        **kwargs: Additional arguments for OpenAI API
        
    Returns:
        String response from the LLM
    """
    
    response = call_openai(prompt, {"input": input_data}, model, **kwargs)
    return response.get("response", str(response))
