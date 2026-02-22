import pandas as pd

df = pd.read_csv("coreml_llm_predictions_log.csv")

col = "prediction_claude"

print(df[col].value_counts(dropna=False))
