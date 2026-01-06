# Emakia System

A machine learning project designed to combat online harassment by filtering toxic content on social media platforms. Emakia addresses the urgent need to protect marginalized groups, including women, people of color, and LGBTQI+ individuals, from harmful online interactions.

## Overview

Emakia is building an application to filter toxic content on social media. The project focuses on developing an efficient text classifier model and an AI system to validate labels and outputs. The system includes:

- **Text Classifier Training**: Machine learning models for toxicity detection
- **Label Validation**: LLM-based validation system using LangChain and OpenAI
- **Apple Development**: iOS application with CoreML integration
- **Google Cloud Integration**: Server-side processing and model deployment
- **Data Processing**: Tools for data scraping, labeling, and preparation

## Project Structure

```
emakia-system/
├── apple_development/          # iOS application development
│   ├── Enaelle/               # Main iOS app
│   └── Models/                # CoreML models and playground files
│
├── backend-Google-iPhone/     # Backend services for iOS integration
│   └── app.py                 # Main Flask/FastAPI application
│
├── google_cloud_server_development/
│   ├── text_classifier_training/  # Model training pipelines
│   │   ├── notebook/              # Jupyter notebooks for EDA and POC
│   │   ├── emakia-node/           # Node.js training scripts
│   │   └── validation/            # Model evaluation scripts
│   └── gcloud-toolkit-recent-search/  # Twitter API integration
│
├── LLM-RAG-Toxicity-Evaluator/  # Label validation using LLMs
│   ├── lang-chain-openai/       # OpenAI-based validation
│   ├── Gemini/                  # Google Gemini integration
│   ├── Grok/                    # Grok API integration
│   └── Fireworks/               # Fireworks AI integration
│
├── LLM_FN_Analysis/            # False Negative analysis
├── LLM_FP-Analysis/            # False Positive analysis
├── load-Neo4j/                 # Graph database integration
├── createnewlabels/            # Label generation and processing
├── Scrapping/                  # Data scraping tools
└── data/                       # Data storage (not in git)
    ├── raw/                    # Original, immutable data
    ├── interim/                # Intermediate transformed data
    ├── processed/              # Final datasets for modeling
    └── external/               # Third-party data sources
```

## Key Components

### Text Classifier Training

Training pipelines for toxicity detection models:
- Jupyter notebooks for exploratory data analysis (EDA) and proof of concept
- Node.js scripts for data processing
- Validation scripts for model evaluation (`evaluate_model_01.py`, `evaluate_model_02.py`)

### LLM-Based Label Validation

The system uses multiple LLM providers to validate training labels:
- **LangChain-OpenAI**: Primary validation system
- **Gemini**: Google's model integration
- **Grok**: X.AI integration
- **Fireworks**: Additional validation provider

#### Label Validation Results

Evaluation findings from LLM-based validation:
- **True Positive (TP)**: 31.50% - Harassment correctly identified
- **True Negative (TN)**: 41.68% - Neutral content correctly identified
- **False Negative (FN)**: 24.68% - Harassment missed (mislabeled as neutral)
- **False Positive (FP)**: 2.12% - Neutral content flagged as harassment

**Overall Accuracy**: 73.18% (TP + TN)
**Error Rate**: 26.82% (FN + FP)

**Note**: 2% of training labels contained only return characters and need to be cleaned.

### Apple Development

iOS application components:
- SwiftUI/Cocoa application
- CoreML model integration (`emakiaTweetsSentimentClassifier.mlmodel`)
- Data persistence layer

### Google Cloud Integration

- Vertex AI model training and deployment
- BigQuery data processing
- Twitter API toolkit integration for data collection

## Setup Instructions

### Prerequisites

- Python 3.x
- Node.js (for backend services)
- Xcode (for iOS development)
- Google Cloud SDK (for cloud services)
- OpenAI API key (for LLM validation)

### Environment Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Emakia-Project/emakia.git
   cd emakia-system
   ```

2. **Python Virtual Environment**:
   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   pip install -r requirements.txt
   ```

3. **LangChain-OpenAI Setup**:
   ```bash
   pip install langchain_openai
   export LANGCHAIN_PROJECT=default
   ```

4. **Environment Variables**:
   Create a `.env` file in the `LLM-RAG-Toxicity-Evaluator/lang-chain-openai/` directory:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

5. **Node.js Backend** (if using):
   ```bash
   cd google_cloud_server_development/text_classifier_training/emakia-node
   npm install
   ```

## Data Management

### Data Directory Structure

The `data/` directory follows a standard ML project structure:
- `raw/`: Original, immutable data dumps
- `interim/`: Intermediate data that has been transformed
- `processed/`: Final, canonical datasets for modeling
- `external/`: Data from third-party sources

**Important**: The `data/` folder and `.env` files are excluded from git via `.gitignore`. These must be set up locally. To include them in version control, modify the `.gitignore` file accordingly.

## Model Validation Approaches

The system uses two main approaches for label validation:

1. **Direct Classification**: 
   - Prompt: "You are a sentiment analyst. Analyze the following statement and respond with either 'positive' or 'negative'."

2. **Explanation-Based Analysis**:
   - Prompt: "Analyze the following statement and explain your choice of overall sentiment."
   - Focuses on analyzing false negatives and false positives for model improvement

## Key Scripts

- `evaluateLabelswithLangchain.py`: Main label validation script
- `evaluate_model_01.py`, `evaluate_model_02.py`: Model evaluation with various metrics
- `evaluate-with-lexicon.py`: Lexicon-based evaluation
- `generateCOREMLtraining_file.py`: CoreML training data preparation

## References

- [Twitter API Toolkit for Google Cloud](https://developer.twitter.com/en/docs/tutorials/developer-guide--twitter-api-toolkit-for-google-cloud)

## License

See [LICENSE](LICENSE) file for details.

## Contributing

This is a private project. Please contact the maintainers for contribution guidelines.

---

**Note**: This project is under active development. Documentation and code are subject to change.
