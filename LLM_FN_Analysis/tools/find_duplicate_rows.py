import pandas as pd
import os
from collections import defaultdict
import hashlib

def read_csv_files(file_list):
    """Read all CSV files and return a dictionary with filename as key and DataFrame as value"""
    dataframes = {}
    
    for file in file_list:
        try:
            if os.path.exists(file):
                df = pd.read_csv(file)
                dataframes[file] = df
                print(f"Successfully read {file}: {len(df)} rows")
            else:
                print(f"Warning: File {file} not found")
        except Exception as e:
            print(f"Error reading {file}: {str(e)}")
    
    return dataframes

def find_duplicates_across_files(dataframes):
    """Find duplicate rows across all files"""
    # Dictionary to store row hash -> list of (filename, row_index, row_data)
    row_tracker = defaultdict(list)
    
    for filename, df in dataframes.items():
        for idx, row in df.iterrows():
            # Convert row to string and create hash for comparison
            # Remove leading/trailing whitespace and convert to lowercase for better matching
            row_str = '|'.join([str(val).strip().lower() if pd.notna(val) else '' for val in row.values])
            row_hash = hashlib.md5(row_str.encode()).hexdigest()
            
            # Store original row data
            row_tracker[row_hash].append((filename, idx, row.to_dict()))
    
    # Find rows that appear in multiple files
    duplicates = {}
    for row_hash, occurrences in row_tracker.items():
        if len(occurrences) > 1:
            duplicates[row_hash] = occurrences
    
    return duplicates

def write_duplicate_report(duplicates, output_file="duplicate_report.txt"):
    """Write a report of duplicates to a file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("DUPLICATE ROWS REPORT\n")
        f.write("=" * 50 + "\n\n")
        
        if not duplicates:
            f.write("No duplicate rows found across the files.\n")
            return
        
        f.write(f"Found {len(duplicates)} sets of duplicate rows:\n\n")
        
        duplicate_count = 1
        for row_hash, occurrences in duplicates.items():
            f.write(f"DUPLICATE SET #{duplicate_count}\n")
            f.write("-" * 30 + "\n")
            
            # Show the row content (using first occurrence as reference)
            first_occurrence = occurrences[0]
            row_data = first_occurrence[2]
            
            f.write("Row Content:\n")
            for column, value in row_data.items():
                f.write(f"  {column}: {value}\n")
            f.write("\n")
            
            f.write("Found in files:\n")
            for filename, row_idx, _ in occurrences:
                f.write(f"  - {filename} (row {row_idx + 2})  # +2 because of 0-indexing and header\n")
            
            f.write("\n" + "=" * 50 + "\n\n")
            duplicate_count += 1
    
    print(f"Duplicate report written to {output_file}")

def main():
    # List of files to process
    all_files = [
        "gemini_multi_toxic_llm.csv",
        "gemini_rt_or_none_likely_toxic.csv",
        "toxic_terms_lexicon_35000.csv",
        "gemini_single_toxic_llm.csv",
        "gemini_rt_or_none_likely_clean.csv"
    ]
    
    print("Starting duplicate detection across CSV files...")
    print(f"Files to process: {all_files}")
    print()
    
    # Read all CSV files
    dataframes = read_csv_files(all_files)
    
    if not dataframes:
        print("No files could be read. Please check file paths and permissions.")
        return
    
    print(f"\nSuccessfully loaded {len(dataframes)} files")
    print()
    
    # Find duplicates
    duplicates = find_duplicates_across_files(dataframes)
    
    # Write report
    write_duplicate_report(duplicates)
    
    # Print summary
    if duplicates:
        print(f"Summary: Found {len(duplicates)} sets of duplicate rows across files")
        
        # Show which files have duplicates
        files_with_duplicates = set()
        for occurrences in duplicates.values():
            for filename, _, _ in occurrences:
                files_with_duplicates.add(filename)
        
        print("Files containing duplicates:")
        for filename in sorted(files_with_duplicates):
            print(f"  - {filename}")
    else:
        print("No duplicate rows found across the files.")

if __name__ == "__main__":
    main()