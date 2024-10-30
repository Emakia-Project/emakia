import csv

# Function to read the list from a CSV file
def read_list_from_csv(file_path):
    with open(file_path, 'r', newline='', encoding='latin-1') as file:
        reader = csv.reader(file)
        return [row[0].strip() for row in reader]  # Assuming the list is in the first column

# Function to read the content and check each word from the third column
def check_items_in_list(content_file, list_file):
    # Read the list from the list file
    items_list = read_list_from_csv(list_file)
    print(items_list)
    
    found_items = []
    not_found_items = []

    with open(content_file, 'r', newline='', encoding='latin-1') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) > 2:
                third_column_item = row[2].strip().strip('"')
                #print(third_column_item)
                words = third_column_item.split()
                found = False
                for word in words:
                    word = word.replace("!", "")
                    if word in items_list:
                        found = True
                        found_items.append([word, row ])
                        break
                if not found:
                    not_found_items.append(row)

    # Write found items to a new CSV file
    with open('found_items-in-array-4.csv', 'w', newline='', encoding='latin-1') as file:
        writer = csv.writer(file)
        writer.writerows(found_items)

    # Write not found items to a new CSV file
    with open('not_found_items-in-array-4.csv', 'w', newline='', encoding='latin-1') as file:
        writer = csv.writer(file)
        writer.writerows(not_found_items)

# Example usage
content_file_path = 'array_four.csv'  # Path to the file containing the content
list_file_path = 'full_hatebase_element2.csv'  # Path to the file containing the list

check_items_in_list(content_file_path, list_file_path)

