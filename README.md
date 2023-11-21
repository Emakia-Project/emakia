# Emakia, Machine Learning Project

# Machine Learning Project Structure

Having a well-organized general Machine Learning project structure makes it easy to understand and make changes.
Here is the full structure for future reference:
https://github.com/ghimiresunil/Machine-Learning-Project-Structure

## Project Directory Structure

```
├── Machine Learning Project Structure <- Project Main Directory
|   |── api <- Consists of scripts which serialize the API calls and act as a endpoint faciliating for project functions.
│   ├── data <- data in different format
|   |   ├── external <- data from third party source
|   |   ├── interim <- Intermediate data that has been transformed
|   |   ├── processed <- The final, canonical data sets for modeling
|   |   ├── raw <- The original, immutable data dump
|   ├── validation
|   |   ├── evaluate_model_01.py <- Different Matries used to validate the model
|   |   ├── evaluate_model_02.py <- Different Matries used to validate the model
│   ├── notebooks <- All the ipython notebooks used for EDA, visualization and verification of concept (POC).
│   ├── src
|   |   ├── dataset
|   |   |   ├── download_dataset.py <- Scripts to download the dataset or accesing dataset from data folder
|   |   ├── model
|   |   |   ├── train_model.py <- Scripts to train the model
|   |   |   ├── test_model.py <- scripts to test the model
|   |   |   ├── predict_model.py <- Scripts to predict the model
│   ├── .gitignore <- tells Git which files to ignore when committing your project to the GitHub repository
│   ├── .env <- used to hide the confidential data like AWS Screte Key, AWS  Access Key, S3 Bucket Name etc...
│   ├── README.md <- The top-level README for developers using this project
```

\***\*Note\*\***: The `data` folder and `.env` file won’t appear in github. It will be in your local folder. This is not pushed to githhub as it will be in the ignore list (`.gitignore` file). If you want to checkin that also, just comment out in `.gitignore` file and add the data folder to github.

# emakia
