import sys
import os
import csv
import time
from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "llm_eval")))

from llm_wrappers.openai_wrapper import call_openai
from llm_wrappers.gemini_wrapper import call_gemini
from llm_wrappers.grok_wrapper import call_grok
from llm_wrappers.llama_wrapper import call_llama
from llm_wrappers.deepseek_wrapper import call_deepseek

input_csv_file = "tweets-labels-emojis.csv"
output_file = "llm_predictions_log.csv"
batch_size = 10

def load_all_rows(path):
    rows = []
    with open(path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0 or len(row) < 2:
                continue
            text = row[0].strip()
            try:
                label_num = int(row[1].strip())
                if label_num not in [0, 1]:
                    continue
            except ValueError:
                continue
            rows.append({"label": label_num, "text": text})
    print(f"✅ Loaded {len(rows)} rows from {path}")
    return rows

def get_last_processed_index(log_path):
    if not os.path.exists(log_path):
        return 0
    with open(log_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        return sum(1 for _ in reader) - 1  # subtract header
    return 0

def update_metrics(metrics, model, pred, label):
    if pred == 1 and label == 1:
        metrics[model]["TP"] += 1
    elif pred == 0 and label == 0:
        metrics[model]["TN"] += 1
    elif pred == 1 and label == 0:
        metrics[model]["FP"] += 1
    elif pred == 0 and label == 1:
        metrics[model]["FN"] += 1

def write_batch_results(start_index, rows, llm_outputs, log_path, metrics):
    file_exists = os.path.exists(log_path)
    with open(log_path, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        
        if not file_exists:
            writer.writerow([
                "row", "label", "text",
                "prediction_openai", "prediction_gemini",
                "prediction_grok", "prediction_llama", "prediction_deepseek"
            ])
        
        for i, row in enumerate(rows):
            row_num = start_index + i + 1
            label_num = row["label"]
            text = row["text"].replace("\n", " ").replace("\r", " ").strip()
            
            predictions = {
                model: "neutral" if llm_outputs[model][i] == 1 else "toxic"
                for model in llm_outputs
            }
            
            writer.writerow([
                row_num,
                label_num,
                text,
                predictions["openai"],
                predictions["gemini"],
                predictions["grok"],
                predictions["llama"],
                predictions["deepseek"]
            ])
            
            for model in llm_outputs:
                pred = 1 if predictions[model] == "neutral" else 0
                update_metrics(metrics, model, pred, label_num)

def process_batches(rows, start_index=0):
    metrics = defaultdict(lambda: {"TP": 0, "TN": 0, "FP": 0, "FN": 0})
    total = len(rows)
    for i in range(start_index, total, batch_size):
        batch = rows[i:i+batch_size]
        print(f"\n🔄 Processing rows {i+1} to {i+len(batch)}...")

        texts = [r["text"] for r in batch]
        try:
            llm_outputs = {
                "openai": call_openai(texts),
                "gemini": call_gemini(texts),
                "grok": call_grok(texts),
                "llama": call_llama(texts),
                "deepseek": call_deepseek(texts),
            }
        except Exception as e:
            print(f"❌ Error during LLM calls at batch {i+1}-{i+len(batch)}: {e}")
            for idx, text in enumerate(texts):
                print(f"  ↪️ Row {i+1+idx}: {text[:100]}")
            continue

        try:
            write_batch_results(i, batch, llm_outputs, output_file, metrics)
        except Exception as e:
            print(f"❌ Error writing results at batch {i+1}-{i+len(batch)}: {e}")
            continue

        time.sleep(1.5)

    print("\n✅ Evaluation Summary:")
    for model, counts in metrics.items():
        print(f"{model}: TP={counts['TP']} TN={counts['TN']} FP={counts['FP']} FN={counts['FN']}")

def evaluate_llm():
    print("🚀 Starting LLM evaluation...")
    all_rows = load_all_rows(input_csv_file)
    resume_index = get_last_processed_index(output_file)
    process_batches(all_rows, start_index=resume_index)

if __name__ == "__main__":
    evaluate_llm()
