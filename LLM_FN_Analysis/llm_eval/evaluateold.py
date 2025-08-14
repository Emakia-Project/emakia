"""
LLM Evaluation Module

This module provides the main evaluation functionality for testing LLM performance.
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from .llm_wrapper import (
    call_openai, call_gemini, call_grok, 
    call_llama, call_deepseek
)


def evaluate_with_llm(
    data: pd.DataFrame,
    llm_provider: str,
    task_description: str,
    output_columns: List[str],
    **kwargs
) -> pd.DataFrame:
    """
    Evaluate LLM performance on a given dataset.
    
    Args:
        data: Input DataFrame containing the data to evaluate
        llm_provider: Name of the LLM provider ('openai', 'gemini', 'grok', 'llama', 'deepseek')
        task_description: Description of the task for the LLM
        output_columns: List of column names for the expected output
        **kwargs: Additional arguments to pass to the LLM wrapper
        
    Returns:
        DataFrame with original data plus LLM-generated outputs
    """
    
    # Map provider names to wrapper functions
    provider_map = {
        'openai': call_openai,
        'gemini': call_gemini,
        'grok': call_grok,
        'llama': call_llama,
        'deepseek': call_deepseek
    }
    
    if llm_provider not in provider_map:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")
    
    llm_function = provider_map[llm_provider]
    
    # Create a copy of the input data
    result_df = data.copy()
    
    # Process each row
    for idx, row in data.iterrows():
        try:
            # Prepare input for LLM
            input_text = row.to_dict()
            
            # Call the appropriate LLM wrapper
            response = llm_function(
                prompt=task_description,
                input_data=input_text,
                **kwargs
            )
            
            # Parse response and add to output columns
            if isinstance(response, dict):
                for col in output_columns:
                    if col in response:
                        result_df.at[idx, col] = response[col]
                    else:
                        result_df.at[idx, col] = None
            else:
                # If response is not a dict, try to parse it
                for col in output_columns:
                    result_df.at[idx, col] = response
                    
        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            # Set all output columns to None for failed rows
            for col in output_columns:
                result_df.at[idx, col] = None
    
    return result_df


def batch_evaluate(
    data: pd.DataFrame,
    llm_provider: str,
    task_description: str,
    output_columns: List[str],
    batch_size: int = 10,
    **kwargs
) -> pd.DataFrame:
    """
    Evaluate LLM performance in batches for better efficiency.
    
    Args:
        data: Input DataFrame containing the data to evaluate
        llm_provider: Name of the LLM provider
        task_description: Description of the task for the LLM
        output_columns: List of column names for the expected output
        batch_size: Number of rows to process in each batch
        **kwargs: Additional arguments to pass to the LLM wrapper
        
    Returns:
        DataFrame with original data plus LLM-generated outputs
    """
    
    result_df = data.copy()
    
    # Process data in batches
    for start_idx in range(0, len(data), batch_size):
        end_idx = min(start_idx + batch_size, len(data))
        batch_data = data.iloc[start_idx:end_idx]
        
        print(f"Processing batch {start_idx//batch_size + 1}: rows {start_idx}-{end_idx-1}")
        
        batch_result = evaluate_with_llm(
            data=batch_data,
            llm_provider=llm_provider,
            task_description=task_description,
            output_columns=output_columns,
            **kwargs
        )
        
        # Update the result DataFrame with batch results
        for col in output_columns:
            result_df.iloc[start_idx:end_idx, result_df.columns.get_loc(col)] = batch_result[col]
    
    return result_df
