import pandas as pd

# Load your data
df = pd.read_csv("coreml_llm_predictions_log.csv")

# List of prediction columns you want to analyze
prediction_columns = [
    "prediction", "prediction_ll0", "prediction_llm3",
    "prediction_llm4", "prediction_openai", "prediction_gemini",
    "prediction_grok", "prediction_llama", "prediction_deepseek", "prediction_claude"
]

# Create a results table
results = []




"""col = "prediction_claude"

# Keep only non‑neutral rows for Claude
claude_non_neutral = df[df[col] != "Neutral"]

# Count Harassment only
harassment_count = (claude_non_neutral[col] == "Harassment").sum()

print("Claude – Harassment (non‑neutral only):", harassment_count)
"""



for col in prediction_columns:
    if col in df.columns:
        counts = df[col].value_counts()
        results.append({
            "Column": col,
            "Neutral": counts.get("Neutral", 0),
            "Harassment": counts.get("Harassment", 0)
        })

# Convert to DataFrame for display
summary_df = pd.DataFrame(results)

print(summary_df) 
