import csv

# Path to the input file
input_file_path = 'updated_predictions.csv'

# Function to process predictions and write to separate files
def write_rows_by_positive_count(file_path):
    # Output file paths for each category
    output_files = {
        0: 'file0.csv',
        1: 'file1.csv',
        2: 'file2.csv',
        3: 'file3.csv',
        4: 'file4.csv',
        5: 'file5.csv',
    }

    # Open all output files in advance
    output_writers = {}
    for count, file_name in output_files.items():
        output_writers[count] = open(file_name, mode='w', newline='', encoding='utf-8')
    
    try:
        # Create CSV writers for each output file
        csv_writers = {}
        for count, file_obj in output_writers.items():
            csv_writers[count] = csv.writer(file_obj)

        # Read the input file
        with open(file_path, mode='r', encoding='utf-8') as infile:
            csvreader = csv.reader(infile)
            header = next(csvreader)  # Read the header row
            
            # Write the header row to each output file
            for writer in csv_writers.values():
                writer.writerow(header)

            # Process each row and categorize based on positive predictions
            for row in csvreader:
                # Extract predictions from the row (first 5 columns)
                predictions = row[:5]

                # Count the number of "positive" predictions
                positive_count = sum(1 for prediction in predictions if prediction.lower() == "positive")

                # Write the row to the corresponding file based on the count of "positives"
                if positive_count in csv_writers:
                    csv_writers[positive_count].writerow(row)
                else:
                    print(f"Unexpected positive count ({positive_count}) in row: {row}")

    finally:
        # Close all output files
        for file_obj in output_writers.values():
            file_obj.close()

# Run the function
write_rows_by_positive_count(input_file_path)
