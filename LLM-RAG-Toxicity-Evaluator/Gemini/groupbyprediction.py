import csv

# Paths to your files
file_path1 = 'endofoutputfourarraygemini.csv'
file_path2 = 'outputfourarraygemini.csv'
output_negative_file1 = 'matching_negative_rows_file1.csv'
output_positive_file1 = 'matching_positive_rows_file1.csv'
output_negative_file2 = 'matching_negative_rows_file2.csv'
output_positive_file2 = 'matching_positive_rows_file2.csv'

# Function to read and process a file
def read_and_process_file(file_path):
    with open(file_path, 'r', newline='') as infile:
        reader = csv.reader(infile)
        rows = list(reader)
        return rows

# Read and process both files
rows_file1 = read_and_process_file(file_path1)
rows_file2 = read_and_process_file(file_path2)

# Initialize lists for storing matching rows
matching_negative_rows_file1 = []
matching_positive_rows_file1 = []
matching_negative_rows_file2 = []
matching_positive_rows_file2 = []

# Function to find and store matching rows
def find_matching_rows(rows, matching_negative_rows, matching_positive_rows):
    for row in rows:
        for i in range(len(row) - 1):
            if row[i] == 'negative' and ('Negative' in row[i + 1] or 'negative' in row[i + 1]):
                matching_negative_rows.append(row)
                break
            elif row[i] == 'positive' and ('Negative' in row[i + 1] or 'negative' in row[i + 1]):
                matching_positive_rows.append(row)
                break

# Find matching rows for both files
find_matching_rows(rows_file1, matching_negative_rows_file1, matching_positive_rows_file1)
find_matching_rows(rows_file2, matching_negative_rows_file2, matching_positive_rows_file2)

# Write the matching negative rows to a new file
with open(output_negative_file1, 'w', newline='') as outfile1:
    writer = csv.writer(outfile1)
    writer.writerows(matching_negative_rows_file1)

with open(output_positive_file1, 'w', newline='') as outfile2:
    writer = csv.writer(outfile2)
    writer.writerows(matching_positive_rows_file1)

with open(output_negative_file2, 'w', newline='') as outfile3:
    writer = csv.writer(outfile3)
    writer.writerows(matching_negative_rows_file2)

with open(output_positive_file2, 'w', newline='') as outfile4:
    writer = csv.writer(outfile4)
    writer.writerows(matching_positive_rows_file2)

# Print the number of rows in each array
num_matching_negative_rows_file1 = len(matching_negative_rows_file1)
num_matching_positive_rows_file1 = len(matching_positive_rows_file1)
num_matching_negative_rows_file2 = len(matching_negative_rows_file2)
num_matching_positive_rows_file2 = len(matching_positive_rows_file2)

print(f"File 1 - Number of matching negative rows: {num_matching_negative_rows_file1}")
print(f"File 1 - Number of matching positive rows: {num_matching_positive_rows_file1}")
print(f"File 2 - Number of matching negative rows: {num_matching_negative_rows_file2}")
print(f"File 2 - Number of matching positive rows: {num_matching_positive_rows_file2}")

# Calculate and print the total number of rows
total_rows = (num_matching_negative_rows_file1 + num_matching_positive_rows_file1 + 
              num_matching_negative_rows_file2 + num_matching_positive_rows_file2)
print(f"Total number of matching rows: {total_rows}")
