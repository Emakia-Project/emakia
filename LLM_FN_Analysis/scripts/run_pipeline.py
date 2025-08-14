#!/usr/bin/env python3
"""
LLM Evaluation Pipeline

This script demonstrates how to use the LLM evaluation framework
to process data with various LLM providers.
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from llm_eval import evaluate_with_llm, batch_evaluate


def main():
    """Main function to run the LLM evaluation pipeline."""
    
    print("🚀 Starting LLM Evaluation Pipeline")
    print("=" * 50)
    
    # Load the sample data
    data_path = Path(__file__).parent.parent / "data" / "tweets-labels-emojis.csv"
    output_path = Path(__file__).parent.parent / "output" / "llm_evaluation_results.csv"
    
    try:
        data = pd.read_csv(data_path)
        print(f"✅ Loaded data: {len(data)} rows from {data_path}")
        print(f"📊 Data columns: {list(data.columns)}")
        print()
        
        # Display first few rows
        print("📋 Sample data:")
        print(data.head())
        print()
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find data file at {data_path}")
        return
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    # Define the task description
    task_description = """
    Analyze the sentiment of the given tweet text. 
    Determine if the sentiment is positive, negative, or neutral.
    Consider the context, tone, and emotional words used.
    """
    
    # Define output columns
    output_columns = ["llm_sentiment", "llm_confidence", "llm_reasoning"]
    
    # Get LLM provider from user or environment
    llm_provider = os.getenv('LLM_PROVIDER', 'openai')
    
    print(f"🤖 Using LLM provider: {llm_provider}")
    print(f"📝 Task: {task_description.strip()}")
    print(f"📤 Output columns: {output_columns}")
    print()
    
    try:
        # Run evaluation
        print("🔄 Running LLM evaluation...")
        
        # Use batch processing for better efficiency
        results = batch_evaluate(
            data=data,
            llm_provider=llm_provider,
            task_description=task_description,
            output_columns=output_columns,
            batch_size=5,  # Process 5 rows at a time
            temperature=0.1,  # Low temperature for consistent results
            max_tokens=200
        )
        
        print("✅ Evaluation completed successfully!")
        print()
        
        # Display results
        print("📊 Results:")
        print(results[["tweet_id", "text", "label", "llm_sentiment", "llm_confidence"]].head(10))
        print()
        
        # Save results
        results.to_csv(output_path, index=False)
        print(f"💾 Results saved to: {output_path}")
        
        # Basic analysis
        print("\n📈 Analysis Summary:")
        print(f"Total tweets processed: {len(results)}")
        
        # Compare original labels with LLM predictions
        if 'label' in results.columns and 'llm_sentiment' in results.columns:
            accuracy = (results['label'] == results['llm_sentiment']).mean()
            print(f"Label accuracy: {accuracy:.2%}")
            
            # Confusion matrix
            print("\n🔍 Label Comparison:")
            comparison = pd.crosstab(results['label'], results['llm_sentiment'], margins=True)
            print(comparison)
        
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure you have the required API keys set as environment variables")
        print("2. Check that the LLM provider is supported")
        print("3. Verify your internet connection and API access")
        return
    
    print("\n🎉 Pipeline completed successfully!")


def test_individual_wrappers():
    """Test individual LLM wrapper functions."""
    
    print("\n🧪 Testing Individual LLM Wrappers")
    print("=" * 40)
    
    # Test data
    test_input = {"text": "This is a test tweet for sentiment analysis."}
    test_prompt = "Analyze the sentiment of this tweet."
    
    # Test each wrapper (will fail without proper API keys, but shows the interface)
    wrappers = {
        'openai': 'call_openai',
        'gemini': 'call_gemini', 
        'grok': 'call_grok',
        'llama': 'call_llama',
        'deepseek': 'call_deepseek'
    }
    
    for provider, wrapper_name in wrappers.items():
        print(f"\n📡 Testing {provider.upper()} wrapper...")
        try:
            # This will fail without API keys, but shows the expected interface
            print(f"   Function: {wrapper_name}")
            print(f"   Expected signature: {wrapper_name}(prompt, input_data, **kwargs)")
            print(f"   Status: ⚠️  Requires {provider.upper()}_API_KEY environment variable")
        except Exception as e:
            print(f"   Error: {e}")


if __name__ == "__main__":
    main()
    
    # Optionally run wrapper tests
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_individual_wrappers()
