"""
Google Gemini API Wrapper

This module provides a wrapper for the Google Gemini API to simplify LLM interactions.
"""

import os
import json
from typing import Dict, Any, Optional
import google.generativeai as genai


def call_gemini(
    prompt: str,
    input_data: Dict[str, Any],
    model: str = "gemini-pro",
    temperature: float = 0.1,
    max_output_tokens: int = 1000,
    **kwargs
) -> Dict[str, Any]:
    """
    Call Google Gemini API with the given prompt and input data.
    
    Args:
        prompt: The task description or prompt for the LLM
        input_data: Input data to be processed
        model: Gemini model to use (default: gemini-pro)
        temperature: Sampling temperature (default: 0.1)
        max_output_tokens: Maximum tokens in response (default: 1000)
        **kwargs: Additional arguments for Gemini API
        
    Returns:
        Dictionary containing the LLM response
    """
    
    # Check for API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # Get the model
    try:
        model_instance = genai.GenerativeModel(model)
    except Exception as e:
        raise ValueError(f"Invalid Gemini model '{model}': {str(e)}")
    
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
        # Generate content
        response = model_instance.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                **kwargs
            )
        )
        
        # Extract response text
        response_text = response.text
        
        # Try to parse JSON response
        try:
            parsed_response = json.loads(response_text)
            return parsed_response
        except json.JSONDecodeError:
            # If JSON parsing fails, return as plain text
            return {
                "response": response_text,
                "confidence": 0.5,
                "reasoning": "Response could not be parsed as JSON"
            }
            
    except Exception as e:
        raise RuntimeError(f"Gemini API call failed: {str(e)}")


def call_gemini_simple(
    prompt: str,
    input_data: str,
    model: str = "gemini-pro",
    **kwargs
) -> str:
    """
    Simplified Gemini API call that returns just the text response.
    
    Args:
        prompt: The task description or prompt
        input_data: Input data as a string
        model: Gemini model to use
        **kwargs: Additional arguments for Gemini API
        
    Returns:
        String response from the LLM
    """
    
    response = call_gemini(prompt, {"input": input_data}, model, **kwargs)
    return response.get("response", str(response))
