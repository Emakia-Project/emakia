import pandas as pd

# Load each classification file
common_tp = pd.read_csv("common_tp.csv")
common_tn = pd.read_csv("common_tn.csv")
common_fp = pd.read_csv("common_fp.csv")
common_fn = pd.read_csv("common_fn.csv")
at_least_one_fp = pd.read_csv("at_least_one_fp.csv")
at_least_one_fn = pd.read_csv("at_least_one_fn.csv")
df = pd.read_csv("llm_predictions_log.csv")

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
