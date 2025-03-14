import csv

# Initialize four empty arrays for different conditions
array_one = []  # Positive reviews with Original content 1
array_two = []  # Negative reviews with Original content 0
array_three = []  # Positive reviews with Original content 0
array_four = []  # Negative reviews with Original content 1
unmatched_condition = []  # Cash errors

# Read the CSV file
with open('output.csv', mode='r', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=',')  # Changed delimiter to comma
    next(csv_reader)  # Skip header row
    
    total_rows = 0
    for row in csv_reader:
        if len(row) < 3:  # Ensure the row has at least 3 columns
            continue
        
        total_rows += 1
        review_sentiment = row[0].strip().strip('"').lower()  # Normalize case and remove newline characters
        
        # Convert "neutral" to "positive"
        if review_sentiment in ["positive", "neutral"]:
            review_sentiment = "positive"
        
        label = int(row[1])
        
        if (review_sentiment == "positive" and label == 1):
            array_one.append(row)
        elif (review_sentiment == "negative" and label == 0):
            array_two.append(row)
        elif (review_sentiment == "positive" and label == 0):
            array_three.append(row)
        elif (review_sentiment == "negative" and label == 1):
            array_four.append(row)
        else:
            original_content = row[0]
            print(f"Raw row data: {row}")
            print(f"Unmatched condition: '{review_sentiment}', {label}, original content, {original_content} ")
            unmatched_condition.append(row)

# Calculate percentages
if total_rows > 0:
    percent_array_one = (len(array_one) / total_rows) * 100
    percent_array_two = (len(array_two) / total_rows) * 100
    percent_array_three = (len(array_three) / total_rows) * 100
    percent_array_four = (len(array_four) / total_rows) * 100
    percent_unmatched_condition = (len(unmatched_condition) / total_rows) * 100
else:
    percent_array_one = percent_array_two = percent_array_three = percent_array_four = 0

# Write results to a file
with open('sorted_reviews.csv', mode='w', encoding='utf-8', newline='') as outfile:
    csv_writer = csv.writer(outfile, delimiter=',')
    csv_writer.writerow(['Review Sentiment', 'Original Content', 'Text'])
    
    csv_writer.writerow(['Array One (Positive, Original Content 1)'])
    csv_writer.writerows(array_one)
    
    csv_writer.writerow(['Array Two (Negative, Original Content 0)'])
    csv_writer.writerows(array_two)
    
    csv_writer.writerow(['Array Three (Positive, Original Content 0)'])
    csv_writer.writerows(array_three)
    
    csv_writer.writerow(['Array Four (Negative, Original Content 1)'])
    csv_writer.writerows(array_four)

# Write array_three to a separate file
with open('array_three.csv', mode='w', encoding='utf-8', newline='') as array_three_file:
    csv_writer = csv.writer(array_three_file, delimiter=',')
    csv_writer.writerow(['Review Sentiment', 'Original Content', 'Text'])
    csv_writer.writerows(array_three)

# Write array_four to a separate file
with open('array_four.csv', mode='w', encoding='utf-8', newline='') as array_four_file:
    csv_writer = csv.writer(array_four_file, delimiter=',')
    csv_writer.writerow(['Review Sentiment', 'Original Content', 'Text'])
    csv_writer.writerows(array_four)

# Write percentages to another file
with open('percentages.csv', mode='w', encoding='utf-8', newline='') as percent_file:
    csv_writer = csv.writer(percent_file, delimiter=',')
    csv_writer.writerow(['Array', 'Percentage'])
    csv_writer.writerow(['Array One (Positive, Original Content 1)', f'{percent_array_one:.2f}%'])
    csv_writer.writerow(['Array Two (Negative, Original Content 0)', f'{percent_array_two:.2f}%'])
    csv_writer.writerow(['Array Three (Positive, Original Content 0)', f'{percent_array_three:.2f}%'])
    csv_writer.writerow(['Array Four (Negative, Original Content 1)', f'{percent_array_four:.2f}%'])

# Print out the percentages
print(f"Percentage of Array One: {percent_array_one:.2f}%")
print(f"Percentage of Array Two: {percent_array_two:.2f}%")
print(f"Percentage of Array Three: {percent_array_three:.2f}%")
print(f"Percentage of Array Four: {percent_array_four:.2f}%")
if len(unmatched_condition) > 0:
    print(f"Percentage of Error Array: {percent_unmatched_condition:.2f}%")
