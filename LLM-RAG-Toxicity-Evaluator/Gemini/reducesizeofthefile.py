import csv

# Path to your file
file_path = 'array_four.csv'
output_file_path = 'endofarray_four.csv'

# Read the file and modify specific rows
with open(file_path, 'r', newline='') as infile:
    reader = csv.reader(infile)
    rows = list(reader)

# Initialize row_smaller_range
row_smaller_range = []

# Modify rows from 15017 to 19380
for i in range(15016, 19380):
    # Remove quotation marks from each element in the row and store in row_smaller_range
    modified_row = [element.replace('positive,""""', '') for element in rows[i]]
    if len(modified_row) > 0:
       row_smaller_range.append(rows[i])

# Write the modified rows back to a new file
with open(output_file_path, 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerows(row_smaller_range)

print(f"Rows from 15017 to 19380 have been modified and saved to {output_file_path}")
