import csv

# Path to the input file
input_file_path = 'predictions.csv'
output_file_path = 'updated_predictions.csv'

def replace_neutral_with_positive(input_path, output_path):
    with open(input_path, mode='r', encoding='utf-8') as infile, \
         open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
        
        csvreader = csv.reader(infile)
        csvwriter = csv.writer(outfile)
        
        # Read and write the header row
        header = next(csvreader)
        csvwriter.writerow(header)
        
        # Process each row
        for row in csvreader:
            # Replace "Neutral" with "Positive" in the first 5 columns (predictions)
            updated_row = [col.replace("Neutral", "Positive") if col.lower() == "neutral" else col for col in row]
            csvwriter.writerow(updated_row)

# Run the function
replace_neutral_with_positive(input_file_path, output_file_path)
