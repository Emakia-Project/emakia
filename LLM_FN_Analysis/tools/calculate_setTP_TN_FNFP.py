import pandas as pd

# Load CSV
df = pd.read_csv("llm_predictions_log.csv")

# Define models
models = ["prediction_openai", "prediction_gemini", "prediction_grok", "prediction_llama", "prediction_deepseek"]

# Initialize sets
common_tp, common_tn, common_fp, common_fn = [], [], [], []
at_least_one_fp = []
at_least_one_fn = []

# Iterate through each row
for _, row in df.iterrows():
    label = int(row["label"])  # 0 = toxic, 1 = neutral
    predictions = [str(row[model]).strip().lower() for model in models]

    # Check if all predictions are the same
    if all(pred == predictions[0] for pred in predictions):
        agreed_prediction = predictions[0]
        if label == 0 and agreed_prediction == "toxic":
            common_tp.append(row)
        elif label == 1 and agreed_prediction == "neutral":
            common_tn.append(row)
        elif label == 1 and agreed_prediction == "toxic":
            common_fp.append(row)
        elif label == 0 and agreed_prediction == "neutral":
            common_fn.append(row)
    else:
        # Check for at least one FP or FN
        fp_flag = any(label == 1 and pred == "toxic" for pred in predictions)
        fn_flag = any(label == 0 and pred == "neutral" for pred in predictions)

        if fp_flag:
            at_least_one_fp.append(row)
        elif fn_flag:
            at_least_one_fn.append(row)

# Sanity check: total rows must match original
total_rows = (
    len(common_tp) + len(common_tn) + len(common_fp) +
    len(common_fn) + len(at_least_one_fp) + len(at_least_one_fn)
)
assert total_rows == len(df), f"Mismatch: {total_rows} rows classified vs {len(df)} in original"

# Save each set to CSV
pd.DataFrame(common_tp).to_csv("common_tp.csv", index=False)
pd.DataFrame(common_tn).to_csv("common_tn.csv", index=False)
pd.DataFrame(common_fp).to_csv("common_fp.csv", index=False)
pd.DataFrame(common_fn).to_csv("common_fn.csv", index=False)
pd.DataFrame(at_least_one_fp).to_csv("at_least_one_fp.csv", index=False)
pd.DataFrame(at_least_one_fn).to_csv("at_least_one_fn.csv", index=False)

# Create and save summary
summary = {
    "common_tp": len(common_tp),
    "common_tn": len(common_tn),
    "common_fp": len(common_fp),
    "common_fn": len(common_fn),
    "at_least_one_fp": len(at_least_one_fp),
    "at_least_one_fn": len(at_least_one_fn),
    "total_classified": (
        len(common_tp) + len(common_tn) + len(common_fp) +
        len(common_fn) + len(at_least_one_fp) + len(at_least_one_fn)
    ),
    "total_original": len(df)
}

pd.DataFrame([summary]).to_csv("classification_summary.csv", index=False)
