"""
Consensus Analysis for CoreML and LLM Predictions

This script analyzes the predictions from CoreML and multiple LLMs to:
1. Find perfect agreement cases (all models agree)
2. Find disagreement cases (at least one model differs)
3. Perform majority voting to find true labels
4. Analyze possibly_sensitive flag correlations
5. Create deduplicated dataset and re-run analysis
"""

import csv
import os
from collections import Counter
from datetime import datetime

# Configuration
INPUT_FILE = "coreml_llm_predictions_log.csv"
OUTPUT_DIR = "consensus_analysis"

# Output files
UNIQUE_CONTENT_FILE = os.path.join(OUTPUT_DIR, "coreml_llm_predictions_uniquecontent.csv")

# Perfect agreement files
AGREE_TOXIC_FILE = os.path.join(OUTPUT_DIR, "perfect_agreement_toxic.csv")
AGREE_NEUTRAL_FILE = os.path.join(OUTPUT_DIR, "perfect_agreement_neutral.csv")

# Disagreement files
DISAGREE_TOXIC_FILE = os.path.join(OUTPUT_DIR, "disagreement_toxic.csv")
DISAGREE_NEUTRAL_FILE = os.path.join(OUTPUT_DIR, "disagreement_neutral.csv")

# Analysis reports
SUMMARY_REPORT = os.path.join(OUTPUT_DIR, "consensus_summary_report.txt")
MAJORITY_VOTE_FILE = os.path.join(OUTPUT_DIR, "majority_vote_results.csv")

# LLM columns in the CSV
LLM_COLUMNS = [
    "prediction_openai",
    "prediction_gemini", 
    "prediction_grok",
    "prediction_llama",
    "prediction_deepseek",
    "prediction_claude"
]


def ensure_output_dir():
    """Create output directory if it doesn't exist"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"✅ Created output directory: {OUTPUT_DIR}")


def load_predictions(filepath):
    """Load predictions from CSV file"""
    rows = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def normalize_prediction(pred):
    """Normalize prediction to 0 (toxic) or 1 (neutral)"""
    if pred is None or pred == "Error":
        return None
    pred_lower = str(pred).lower()
    if "neutral" in pred_lower or pred_lower == "1":
        return 1
    elif "harassment" in pred_lower or "toxic" in pred_lower or pred_lower == "0":
        return 0
    return None


def get_all_predictions(row):
    """Extract all model predictions including CoreML"""
    predictions = {}
    
    # CoreML prediction
    coreml_pred = int(row.get("coreml_prediction", -1))
    predictions["coreml"] = coreml_pred if coreml_pred in [0, 1] else None
    
    # LLM predictions
    for col in LLM_COLUMNS:
        model_name = col.replace("prediction_", "")
        predictions[model_name] = normalize_prediction(row.get(col))
    
    return predictions


def check_agreement(predictions, coreml_value):
    """
    Check if all models agree with CoreML
    Returns: (all_agree, disagreeing_models)
    """
    disagreeing = []
    
    for model, pred in predictions.items():
        if model == "coreml":
            continue
        if pred is None:  # Skip errors
            continue
        if pred != coreml_value:
            disagreeing.append(model)
    
    all_agree = len(disagreeing) == 0
    return all_agree, disagreeing


def get_majority_vote(predictions):
    """
    Get majority vote from all predictions (including CoreML)
    Returns: (majority_value, vote_counts, confidence)
    """
    valid_predictions = [p for p in predictions.values() if p is not None]
    
    if not valid_predictions:
        return None, {}, 0.0
    
    vote_counts = Counter(valid_predictions)
    majority_value = vote_counts.most_common(1)[0][0]
    majority_count = vote_counts[majority_value]
    confidence = majority_count / len(valid_predictions)
    
    return majority_value, dict(vote_counts), confidence


def create_deduplicated_dataset(rows):
    """
    Create deduplicated dataset based on tweet text
    Keep first occurrence of each unique text
    """
    print("\n" + "="*60)
    print("📋 CREATING DEDUPLICATED DATASET")
    print("="*60)
    
    seen_texts = set()
    unique_rows = []
    duplicate_count = 0
    
    for row in rows:
        text = row.get("text", "").strip()
        
        if text not in seen_texts:
            seen_texts.add(text)
            unique_rows.append(row)
        else:
            duplicate_count += 1
    
    print(f"   Total rows: {len(rows)}")
    print(f"   Unique rows: {len(unique_rows)}")
    print(f"   Duplicates removed: {duplicate_count}")
    
    # Write unique dataset
    if unique_rows:
        with open(UNIQUE_CONTENT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=unique_rows[0].keys())
            writer.writeheader()
            writer.writerows(unique_rows)
        print(f"   ✅ Saved to: {UNIQUE_CONTENT_FILE}")
    
    return unique_rows


def analyze_dataset(rows, dataset_name="Full Dataset"):
    """
    Perform consensus analysis on a dataset
    Returns statistics dictionary
    """
    print("\n" + "="*60)
    print(f"🔍 ANALYZING: {dataset_name}")
    print("="*60)
    
    # Categorize rows
    agree_toxic = []
    agree_neutral = []
    disagree_toxic = []
    disagree_neutral = []
    majority_results = []
    
    stats = {
        "total_rows": len(rows),
        "agree_toxic": 0,
        "agree_neutral": 0,
        "disagree_toxic": 0,
        "disagree_neutral": 0,
        "possibly_sensitive_stats": {
            "agree_toxic": {"yes": 0, "no": 0},
            "agree_neutral": {"yes": 0, "no": 0},
            "disagree_toxic": {"yes": 0, "no": 0},
            "disagree_neutral": {"yes": 0, "no": 0}
        }
    }
    
    for row in rows:
        # Handle both text and numeric CoreML predictions
        coreml_value = row.get("coreml_prediction", "")
        if isinstance(coreml_value, str):
            coreml_value_lower = coreml_value.lower()
            if "neutral" in coreml_value_lower:
                coreml_pred = 1
            elif "harassment" in coreml_value_lower or "toxic" in coreml_value_lower:
                coreml_pred = 0
            else:
                continue  # Skip invalid values
        else:
            try:
                coreml_pred = int(coreml_value)
                if coreml_pred not in [0, 1]:
                    continue
            except (ValueError, TypeError):
                continue
        
        # Handle both text and numeric possibly_sensitive values
        sensitive_value = row.get("possibly_sensitive", 0)
        if isinstance(sensitive_value, str):
            sensitive_lower = sensitive_value.lower()
            if sensitive_lower in ["true", "1", "yes"]:
                possibly_sensitive = 1
            else:
                possibly_sensitive = 0
        else:
            try:
                possibly_sensitive = int(sensitive_value)
            except (ValueError, TypeError):
                possibly_sensitive = 0
        
        # Get all predictions
        predictions = get_all_predictions(row)
        
        # Check agreement
        all_agree, disagreeing = check_agreement(predictions, coreml_pred)
        
        # Get majority vote
        majority, vote_counts, confidence = get_majority_vote(predictions)
        
        # Add majority vote info to row
        majority_row = row.copy()
        majority_row["majority_vote"] = "Neutral" if majority == 1 else "Harassment"
        majority_row["vote_confidence"] = f"{confidence:.2%}"
        majority_row["vote_breakdown"] = str(vote_counts)
        majority_row["disagrees_with_coreml"] = "Yes" if majority != coreml_pred else "No"
        majority_results.append(majority_row)
        
        # Track possibly_sensitive
        sensitive_key = "yes" if possibly_sensitive == 1 else "no"
        
        # Categorize by agreement and CoreML prediction
        if coreml_pred == 0:  # Toxic
            if all_agree:
                agree_toxic.append(row)
                stats["agree_toxic"] += 1
                stats["possibly_sensitive_stats"]["agree_toxic"][sensitive_key] += 1
            else:
                disagree_toxic.append(row)
                stats["disagree_toxic"] += 1
                stats["possibly_sensitive_stats"]["disagree_toxic"][sensitive_key] += 1
        else:  # Neutral
            if all_agree:
                agree_neutral.append(row)
                stats["agree_neutral"] += 1
                stats["possibly_sensitive_stats"]["agree_neutral"][sensitive_key] += 1
            else:
                disagree_neutral.append(row)
                stats["disagree_neutral"] += 1
                stats["possibly_sensitive_stats"]["disagree_neutral"][sensitive_key] += 1
    
    # Write categorized files
    prefix = "unique_" if "Unique" in dataset_name else ""
    
    write_csv(agree_toxic, os.path.join(OUTPUT_DIR, f"{prefix}perfect_agreement_toxic.csv"))
    write_csv(agree_neutral, os.path.join(OUTPUT_DIR, f"{prefix}perfect_agreement_neutral.csv"))
    write_csv(disagree_toxic, os.path.join(OUTPUT_DIR, f"{prefix}disagreement_toxic.csv"))
    write_csv(disagree_neutral, os.path.join(OUTPUT_DIR, f"{prefix}disagreement_neutral.csv"))
    write_csv(majority_results, os.path.join(OUTPUT_DIR, f"{prefix}majority_vote_results.csv"))
    
    # Print statistics
    print(f"\n📊 {dataset_name} Statistics:")
    print(f"   Total rows analyzed: {stats['total_rows']}")
    print(f"\n   Perfect Agreement:")
    print(f"      Toxic (all agree): {stats['agree_toxic']}")
    print(f"      Neutral (all agree): {stats['agree_neutral']}")
    print(f"\n   Disagreements:")
    print(f"      Toxic (at least 1 disagrees): {stats['disagree_toxic']}")
    print(f"      Neutral (at least 1 disagrees): {stats['disagree_neutral']}")
    
    # Possibly sensitive analysis
    print(f"\n   Possibly Sensitive Flag Analysis:")
    for category, counts in stats["possibly_sensitive_stats"].items():
        total = counts["yes"] + counts["no"]
        if total > 0:
            pct = (counts["yes"] / total) * 100
            print(f"      {category}: {counts['yes']}/{total} ({pct:.1f}% sensitive)")
    
    return stats


def write_csv(rows, filepath):
    """Write rows to CSV file"""
    if not rows:
        return
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"   ✅ Wrote {len(rows)} rows to: {filepath}")


def generate_summary_report(full_stats, unique_stats):
    """Generate comprehensive summary report"""
    with open(SUMMARY_REPORT, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("CONSENSUS ANALYSIS SUMMARY REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")
        
        # Full dataset
        f.write("FULL DATASET (including duplicates)\n")
        f.write("-"*60 + "\n")
        f.write(f"Total rows: {full_stats['total_rows']}\n")
        f.write(f"Perfect agreement (toxic): {full_stats['agree_toxic']}\n")
        f.write(f"Perfect agreement (neutral): {full_stats['agree_neutral']}\n")
        f.write(f"Disagreements (toxic): {full_stats['disagree_toxic']}\n")
        f.write(f"Disagreements (neutral): {full_stats['disagree_neutral']}\n\n")
        
        # Unique dataset
        f.write("UNIQUE CONTENT DATASET (duplicates removed)\n")
        f.write("-"*60 + "\n")
        f.write(f"Total rows: {unique_stats['total_rows']}\n")
        f.write(f"Perfect agreement (toxic): {unique_stats['agree_toxic']}\n")
        f.write(f"Perfect agreement (neutral): {unique_stats['agree_neutral']}\n")
        f.write(f"Disagreements (toxic): {unique_stats['disagree_toxic']}\n")
        f.write(f"Disagreements (neutral): {unique_stats['disagree_neutral']}\n\n")
        
        # Key insights
        f.write("KEY INSIGHTS\n")
        f.write("-"*60 + "\n")
        
        total_full = full_stats['total_rows']
        total_unique = unique_stats['total_rows']
        
        if total_full > 0:
            agree_pct = ((full_stats['agree_toxic'] + full_stats['agree_neutral']) / total_full) * 100
            f.write(f"Full dataset agreement rate: {agree_pct:.1f}%\n")
        
        if total_unique > 0:
            agree_pct_unique = ((unique_stats['agree_toxic'] + unique_stats['agree_neutral']) / total_unique) * 100
            f.write(f"Unique dataset agreement rate: {agree_pct_unique:.1f}%\n")
        
        f.write(f"\nDuplicates in dataset: {total_full - total_unique}\n")
        
    print(f"\n   ✅ Summary report saved to: {SUMMARY_REPORT}")


def main():
    print("="*60)
    print("🔍 CONSENSUS ANALYSIS - CoreML vs LLM Predictions")
    print("="*60)
    
    # Check if input file exists
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input file not found: {INPUT_FILE}")
        print("   Please run evaluate_CoreML.py first to generate predictions.")
        return
    
    # Create output directory
    ensure_output_dir()
    
    # Load predictions
    print(f"\n📂 Loading predictions from: {INPUT_FILE}")
    rows = load_predictions(INPUT_FILE)
    print(f"   ✅ Loaded {len(rows)} rows")
    
    # Analyze full dataset
    full_stats = analyze_dataset(rows, "Full Dataset")
    
    # Create deduplicated dataset
    unique_rows = create_deduplicated_dataset(rows)
    
    # Analyze unique dataset
    unique_stats = analyze_dataset(unique_rows, "Unique Content Dataset")
    
    # Generate summary report
    print("\n" + "="*60)
    print("📝 GENERATING SUMMARY REPORT")
    print("="*60)
    generate_summary_report(full_stats, unique_stats)
    
    print("\n" + "="*60)
    print("✅ CONSENSUS ANALYSIS COMPLETE")
    print("="*60)
    print(f"\nAll results saved to: {OUTPUT_DIR}/")
    print("\nGenerated files:")
    print("   - Unique content dataset")
    print("   - Perfect agreement files (toxic & neutral)")
    print("   - Disagreement files (toxic & neutral)")
    print("   - Majority vote results")
    print("   - Summary report")
    print("="*60)


if __name__ == "__main__":
    main()