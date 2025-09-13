import pandas as pd

# Load both files
array3_df = pd.read_csv("array_three.csv")
common_tp_df = pd.read_csv("common_fn.csv")

# Normalize text for comparison
array3_texts = array3_df["Text"].str.strip().str.lower()
common_tp_texts = common_tp_df["text"].str.strip().str.lower()

# Identify matches
is_similar = array3_texts.isin(common_tp_texts)

# Split into similar and different
similar_array3 = array3_df[is_similar]
different_array3 = array3_df[~is_similar]

# Write to CSV
similar_array3.to_csv("similar_array3.csv", index=False)
different_array3.to_csv("different_array3.csv", index=False)
