import pandas as pd

# === Step 1: Read CSV files ===
multi_toxic = pd.read_csv("gemini_multi_toxic_llm.csv")
rt_toxic = pd.read_csv("gemini_rt_or_none_likely_toxic.csv")
lexicon_toxic = pd.read_csv("toxic_terms_lexicon_35000.csv")

single_toxic = pd.read_csv("gemini_single_toxic_llm.csv")
rt_clean = pd.read_csv("gemini_rt_or_none_likely_clean.csv")

# === Step 2: Build truth sets using 'text' column ===
toxic_truth = set(multi_toxic['text']) | set(rt_toxic['text']) | set(lexicon_toxic['text'])
neutral_truth = set(single_toxic['text']) | set(rt_clean['text'])

print(f"Toxic truth set size: {len(toxic_truth)}")
print(f"Neutral truth set size: {len(neutral_truth)}")

# === Step 3: Accuracy calculation function ===
def calc_percentage(df, truth_ids, target_label):
    """Percentage of truth_ids predicted as target_label."""
    predicted_ids = set(df.loc[df == target_label].index)
    if not truth_ids:
        return 0.0
    return len(predicted_ids & truth_ids) / len(truth_ids) * 100

# === Step 4: Combine all rows for evaluation ===
# Merge all unique rows from all files into one DataFrame
all_dfs = [multi_toxic, rt_toxic, lexicon_toxic, single_toxic, rt_clean]
df_all = pd.concat(all_dfs, ignore_index=True).drop_duplicates(subset=['text'])

# === Step 5: Evaluate each LLM ===
llm_cols = [
    'prediction_openai',
    'prediction_gemini',
    'prediction_grok',
    'prediction_llama',
    'prediction_deepseek'
]

results = []
for col in llm_cols:
    toxic_pct = calc_percentage(df_all.set_index('text')[col], toxic_truth, 'toxic')
    neutral_pct = calc_percentage(df_all.set_index('text')[col], neutral_truth, 'neutral')
    results.append({
        "LLM": col.replace("prediction_", ""),
        "Toxic %": toxic_pct,
        "Neutral %": neutral_pct
    })

# === Step 6: Save results ===
results_df = pd.DataFrame(results)
results_df.to_csv("llm_percentages.csv", index=False)

print("\nPercentages written to llm_percentages.csv")
print(results_df)
