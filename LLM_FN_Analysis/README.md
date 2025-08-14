# Emakia LLM Evaluation Framework

A comprehensive framework for evaluating Large Language Models (LLMs) across multiple providers and tasks.

## 🏗️ Project Structure

```
emakia/
├── llm_eval/                    # Core evaluation package
│   ├── __init__.py             # Package initialization
│   ├── evaluate.py             # Main evaluation functions
│   └── llm_wrappers/           # LLM provider wrappers
│       ├── __init__.py         # Wrappers package init
│       ├── openai_wrapper.py   # OpenAI API wrapper
│       ├── gemini_wrapper.py   # Google Gemini wrapper
│       ├── grok_wrapper.py     # Grok API wrapper
│       ├── llama_wrapper.py    # Llama API wrapper
│       └── deepseek_wrapper.py # DeepSeek API wrapper
├── data/                        # Input data directory
│   └── tweets-labels-emojis.csv # Sample tweet dataset
├── output/                      # Output results directory
│   └── outputretryopenAI.csv   # Sample output format
├── scripts/                     # Utility scripts
│   └── run_pipeline.py         # Main evaluation pipeline
└── README.md                    # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install pandas openai google-generativeai requests
```

### 2. Set Environment Variables

Set the required API keys for your chosen LLM provider:

```bash
# For OpenAI
export OPENAI_API_KEY="your-openai-api-key"

# For Google Gemini
export GOOGLE_API_KEY="your-google-api-key"

# For Grok
export GROK_API_KEY="your-grok-api-key"
export GROK_API_ENDPOINT="https://api.grok.x.ai/v1/chat/completions"

# For Llama
export LLAMA_API_KEY="your-llama-api-key"
export LLAMA_API_ENDPOINT="https://api.llama.ai/v1/chat/completions"

# For DeepSeek
export DEEPSEEK_API_KEY="your-deepseek-api-key"
export DEEPSEEK_API_ENDPOINT="https://api.deepseek.com/v1/chat/completions"
```

### 3. Run the Pipeline

```bash
cd emakia/scripts
python run_pipeline.py
```

## 🔧 Core Functions

### `evaluate_with_llm()`

Main function for evaluating data with any supported LLM provider.

```python
from llm_eval import evaluate_with_llm

results = evaluate_with_llm(
    data=your_dataframe,
    llm_provider='openai',  # or 'gemini', 'grok', 'llama', 'deepseek'
    task_description='Your task description here',
    output_columns=['output_col1', 'output_col2'],
    temperature=0.1,
    max_tokens=1000
)
```

### `batch_evaluate()`

Process data in batches for better efficiency and error handling.

```python
from llm_eval import batch_evaluate

results = batch_evaluate(
    data=your_dataframe,
    llm_provider='openai',
    task_description='Your task description here',
    output_columns=['output_col1', 'output_col2'],
    batch_size=10
)
```

## 🤖 Supported LLM Providers

| Provider | Wrapper Function | Required Env Vars | Default Model |
|----------|------------------|-------------------|---------------|
| OpenAI | `call_openai()` | `OPENAI_API_KEY` | `gpt-4` |
| Google Gemini | `call_gemini()` | `GOOGLE_API_KEY` | `gemini-pro` |
| Grok | `call_grok()` | `GROK_API_KEY`, `GROK_API_ENDPOINT` | `grok-beta` |
| Llama | `call_llama()` | `LLAMA_API_KEY`, `LLAMA_API_ENDPOINT` | `llama-2-70b-chat` |
| DeepSeek | `call_deepseek()` | `DEEPSEEK_API_KEY`, `DEEPSEEK_API_ENDPOINT` | `deepseek-chat` |

## 📊 Data Format

### Input Data
Your input DataFrame should contain the data you want to process. The framework will pass each row to the LLM.

### Output Format
The framework expects LLM responses in JSON format:

```json
{
    "response": "main response content",
    "confidence": 0.95,
    "reasoning": "explanation of the response"
}
```

If the LLM doesn't return valid JSON, the framework will wrap the response in a default structure.

## 🎯 Example Use Cases

### Sentiment Analysis
```python
task_description = """
Analyze the sentiment of the given tweet text. 
Determine if the sentiment is positive, negative, or neutral.
Consider the context, tone, and emotional words used.
"""

output_columns = ["sentiment", "confidence", "reasoning"]
```

### Text Classification
```python
task_description = """
Classify the given text into one of the following categories:
- Technology
- Sports
- Politics
- Entertainment
- Science
"""

output_columns = ["category", "confidence", "reasoning"]
```

### Content Generation
```python
task_description = """
Generate a creative response based on the input text.
The response should be engaging and relevant to the context.
"""

output_columns = ["generated_text", "creativity_score", "relevance_score"]
```

## 🛠️ Customization

### Adding New LLM Providers

1. Create a new wrapper file in `llm_eval/llm_wrappers/`
2. Implement the required interface (similar to existing wrappers)
3. Add the wrapper to `llm_wrappers/__init__.py`
4. Update the provider map in `evaluate.py`

### Custom Response Parsing

Override the default response parsing by modifying the `evaluate_with_llm()` function or creating a custom evaluation function.

## 🔍 Error Handling

The framework includes comprehensive error handling:

- **API Errors**: Catches and reports API-specific errors
- **JSON Parsing**: Gracefully handles malformed JSON responses
- **Batch Processing**: Continues processing even if individual rows fail
- **Rate Limiting**: Built-in delays and retry logic (can be customized)

## 📈 Performance Tips

1. **Use Batch Processing**: Process data in batches for better efficiency
2. **Adjust Temperature**: Lower temperatures (0.1-0.3) for consistent results
3. **Limit Tokens**: Set appropriate `max_tokens` to control response length
4. **Parallel Processing**: Consider implementing parallel processing for large datasets

## 🧪 Testing

Test individual wrappers:

```bash
python run_pipeline.py --test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section in the error messages
2. Review the environment variable setup
3. Verify API key permissions and quotas
4. Check the API provider's status page

## 🔮 Future Enhancements

- [ ] Support for more LLM providers
- [ ] Advanced caching and rate limiting
- [ ] Web interface for easy configuration
- [ ] Integration with evaluation metrics
- [ ] Support for multimodal inputs
- [ ] Real-time streaming responses
