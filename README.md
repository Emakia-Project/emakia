

# Emakia, Machine Learning Project

Emakia is a non-profit organization dedicated to developing a system to filter out toxicity from social media data. Our mission is to create a safer and more positive online environment and providing universities with a system to validate labels and output models.

# Technologies Used

## Vertex AI: 
Leveraging Google Cloud’s Vertex AI for text classifier model training.

## Core ML: 
Utilizing Core ML text classifier for iPhone to  for text classifier model training and performance on iOS devices.

## Big Query:
stored social media data ( Twitter data)
data with text classifier model prediction

## Large Language Models (LLM) 

## Retrieval-Augmented Generation (RAG)

# Project Focus
We are focused on validating labeled data to train our models and the output of our models using Large Language Models (LLM) and Retrieval-Augmented Generation (RAG).
Create a MLOP with training, prediction, evaluation of the prediction, and retraining the model with unknown data to the model.

# Collaboration
Our project is a collaborative effort with:
Montclair NLP Lab, Montclair State University
PAU University
We share our progress, code, and data with these institutions to foster innovation and collective growth.

# Emakia Tech
Emakia Tech is our for-profit branch.

# Machine Learning Project Structure

Set up the config.py with your name

## Project Directory Structure

```
├── Machine Learning Project Structure <- Project Main Directory
|   |── Apple development
|   |── Google Cloud Server Development
|   |   ├── Text Classifier Training
|   |   |   ├── Notebook <- All the ipython notebooks used for EDA, visualization and verification of concept (POC).
|   |   |   ├── Node.js
|   |   |   ├── Validation
|   |   |   |   ├── evaluate_model_01.py <- Different Matries used to validate the model
|   |   |   |   ├──  evaluate_model_02.py <- Different Matries used to validate the model
│   ├── data <- data in different format
|   |   ├── external <- data from third party source
|   |   ├── interim <- Intermediate data that has been transformed
|   |   ├── processed <- The final, canonical data sets for modeling
|   |   ├── raw <- The original, immutable data dump
│   ├── .gitignore <- tells Git which files to ignore when committing your project to the GitHub repository
│   ├── .env <- used to hide the confidential data like AWS Screte Key, AWS  Access Key, S3 Bucket Name etc...
│   ├── README.md <- The top-level README for developers using this project
```

\***\*Note\*\***: The `data` folder and `.env` file won’t appear in github. It will be in your local folder. This is not pushed to githhub as it will be in the ignore list (`.gitignore` file). If you want to checkin that also, just comment out in `.gitignore` file and add the data folder to github.

# emakia
