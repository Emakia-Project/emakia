import pandas as pd

# Read the tweets-labels.csv file with specified encoding and no header
tweets_labels = pd.read_csv('tweets-labels.csv', encoding='latin1', header=None)

# Read hate-lexicon.csv for lexicon entries and convert to a set
hate_lexicon = pd.read_csv('hate-lexicon.csv', encoding='latin1', header=None)
hate_lexicon_set = set(hate_lexicon.values.flatten())

# Create an empty list to store validation results
validation = []

# Create a column for found vocabulary
tweets_labels['found_vocabulary'] = ''

# Process each row in the DataFrame
for index, row in tweets_labels.iterrows():
    # Assume 'validated neutral label' initially
    label = 'validated neutral label'
    content = str(row[0])  # Assuming the content is in the first column and converting to string
    label_value = int(row[1])  # Assuming the label is in the second column
    
    # Check for harassment vocabulary and label values to determine the validation
    if content != 'nan':
        found_words = [word for word in content.lower().split() if word in hate_lexicon_set]
        if found_words and label_value == 1:
            label = 'not validated'
        elif found_words and label_value == 0:
            label = 'validated harassment'
        elif not found_words and label_value == 0:
            label = 'not validated'
    
    # Update the 'validation' list
    validation.append(label)
    
    # Update 'found_vocabulary' column with the hate lexicon words found in the content
    tweets_labels.at[index, 'found_vocabulary'] = ', '.join(found_words)

# Add the validation column to the tweets-labels DataFrame
tweets_labels['validation'] = validation

# Define column headers in the desired order
column_headers = ['text', 'label', 'found_vocabulary', 'validation']

# Assign headers to the DataFrame
tweets_labels.columns = column_headers

# Save the updated DataFrame to a new CSV file
tweets_labels.to_csv('tweets-labels-processed.csv', index=False)
