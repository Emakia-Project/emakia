# LLM False Positive (Previous False Negative) Analysis

This project evaluates multiple Large Language Models (LLMs) for toxicity detection in text content, with a focus on analyzing false positives (FP) and false negatives (FN) across different models.

## Overview

The system evaluates five different LLM providers on a dataset of labeled tweets to assess their performance in toxicity classification. It generates comprehensive metrics including True Positives (TP), True Negatives (TN), False Positives (FP), and False Negatives (FN) for each model, enabling detailed comparative analysis.

## Features

- **Multi-LLM Evaluation**: Supports evaluation across 5 LLM providers:
  - OpenAI
  - Google Gemini (gemini-2.0-flash)
  - Grok (grok-2-1212)
  - Llama (llama-v3p1-8b-instruct via Fireworks)
  - DeepSeek (via Fireworks)

- **Batch Processing**: Processes data in configurable batches with automatic resume capability
- **Comprehensive Metrics**: Calculates TP, TN, FP, FN for each model
- **Consensus Analysis**: Identifies cases where all models agree vs. cases with disagreement
- **Additional Screening**: Uses Gemini for additional toxicity screening and validation
- **Data Analysis Tools**: Includes utilities for calculating accuracy percentages, finding duplicates, and generating summaries

## Project Structure

```
.
├── llm_eval/
│   ├── evaluate_llm.py           # Main evaluation script
│   ├── calculatePercentage.py    # Calculate accuracy percentages
│   ├── gemini_screening.py       # Gemini-based toxicity screening
│   └── llm_wrappers/             # LLM API wrappers
│       ├── openai_wrapper.py
│       ├── gemini_wrapper.py
│       ├── grok_wrapper.py
│       ├── llama_wrapper.py
│       └── deepseek_wrapper.py
├── tools/                        # Analysis and utility scripts
│   ├── calculate_setTP_TN_FNFP.py  # Calculate classification sets
│   ├── summary.py                # Generate classification summary
│   ├── find_duplicate_rows.py    # Find duplicate entries
│   └── ...                       # Other utility scripts
├── data/                         # Data files (CSV datasets and results)
└── fn_cross_eval.py             # Cross-evaluation script for FNs
```

## Prerequisites

- Python 3.13+ (virtual environment recommended)
- API keys for the LLM providers:
  - `OPENAI_API_KEY` for OpenAI
  - `GOOGLE_API_KEY` for Google Gemini
  - `XAI_API_KEY` for Grok (X.AI)
  - `FIREWORKS_API_KEY` for Llama and DeepSeek

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv emakia-env
   source emakia-env/bin/activate  # On Windows: emakia-env\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install pandas langchain langchain-openai langchain-google-genai langchain-xai fireworks python-dotenv
   ```
   
   Note: If you have a `requirements.txt` file, use:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   
   Create a `.env` file in the project root with your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_API_KEY=your_google_api_key
   XAI_API_KEY=your_xai_api_key
   FIREWORKS_API_KEY=your_fireworks_api_key
   ```

## Usage

### Running the Main Evaluation

The main evaluation script processes a CSV file with labeled text data and generates predictions from all LLM models:

```bash
cd llm_eval
python evaluate_llm.py
```

**Configuration**:
- Input file: `data/tweets-labels-emojis.csv` (should have `text` and `label` columns)
- Output file: `data/llm_predictions_log.csv`
- Batch size: 10 (configurable in the script)
- Label format: `0` = toxic, `1` = neutral

The script supports automatic resume - if interrupted, it will continue from where it left off.

### Calculating Classification Sets

After running the evaluation, generate TP/TN/FP/FN classification sets:

```bash
cd tools
python calculate_setTP_TN_FNFP.py
```

This generates the following CSV files in the `data/` directory:
- `common_tp.csv` - True Positives (all models agree, correctly classified as toxic)
- `common_tn.csv` - True Negatives (all models agree, correctly classified as neutral)
- `common_fp.csv` - False Positives (all models agree, incorrectly classified as toxic)
- `common_fn.csv` - False Negatives (all models agree, incorrectly classified as neutral)
- `at_least_one_fp.csv` - Cases where at least one model has a false positive
- `at_least_one_fn.csv` - Cases where at least one model has a false negative
- `classification_summary.csv` - Summary statistics

### Generating Summary Statistics

```bash
cd tools
python summary.py
```

### Calculating Accuracy Percentages

Calculate accuracy percentages for each LLM:

```bash
cd llm_eval
python calculatePercentage.py
```

This generates `llm_percentages.csv` with accuracy metrics for each model.

### Gemini Screening

Run additional toxicity screening using Gemini:

```bash
cd llm_eval
python gemini_screening.py
```

## Input Data Format

The input CSV file should have the following structure:

| text | label |
|------|-------|
| Sample tweet text... | 0 |
| Another tweet... | 1 |

Where:
- `text`: The text content to be classified
- `label`: Ground truth label (`0` = toxic, `1` = neutral)

## Output Data Format

The main evaluation output (`llm_predictions_log.csv`) contains:

| row | label | text | prediction_openai | prediction_gemini | prediction_grok | prediction_llama | prediction_deepseek |
|-----|-------|------|-------------------|-------------------|-----------------|------------------|---------------------|
| 1 | 0 | ... | toxic | toxic | neutral | ... | ... |

Predictions are either `"toxic"` or `"neutral"` for each model.

## Model Configuration

Each LLM wrapper can be configured in the respective files in `llm_eval/llm_wrappers/`:

- **Temperature**: Set to 0 for deterministic outputs
- **Timeout**: Configurable per model (e.g., Gemini uses 60s timeout)
- **Retry Logic**: All wrappers include retry mechanisms with exponential backoff
- **Prompt Template**: Standardized prompt format for consistency across models

## Notes

- The evaluation process can be time-consuming due to API rate limits and the number of models
- Batch processing includes a 1.5-second delay between batches to respect API limits
- All scripts that write to CSV files support resume functionality
- The project includes various utility scripts for data cleaning, duplicate detection, and analysis

## Troubleshooting

1. **API Key Errors**: Ensure all required API keys are set in your `.env` file
2. **Rate Limiting**: If you encounter rate limit errors, the retry logic will handle temporary issues. For persistent issues, consider reducing batch size or increasing delays
3. **Missing Dependencies**: Install all required packages listed in the Installation section
4. **File Path Issues**: Ensure you're running scripts from the correct directory or update paths in the scripts

## License

[Specify your license here]

## Contributing

[Add contribution guidelines if applicable]

