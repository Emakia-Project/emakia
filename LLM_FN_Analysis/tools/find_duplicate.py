import csv
from collections import defaultdict

# Input files
toxic_files = [
    "gemini_multi_toxic_llm.csv",
    "gemini_rt_or_none_likely_toxic.csv",
    "toxic_terms_lexicon_35000.csv"
]

non_toxic_files = [
    "gemini_single_toxic_llm.csv",
    "gemini_rt_or_none_likely_clean.csv"
]

# Label files for clarity
file_labels = {path: f"toxic_{i+1}" for i, path in enumerate(toxic_files)}
file_labels.update({path: f"non_toxic_{i+1}" for i, path in enumerate(non_toxic_files)})

# Load text entries
text_map = defaultdict(set)  # text → set of file labels

for path in toxic_files + non_toxic_files:
    label = file_labels[path]
    with open(path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = row["text"].strip()
            text_map[text].add(label)

# Identify duplicates
duplicates = {text: sources for text, sources in text_map.items() if len(sources) > 1}

# Print summary
print(f"🔍 Found {len(duplicates)} duplicate texts across toxic/non-toxic files.\n")

# Breakdown by file pair
pairwise_counts = defaultdict(int)
for sources in duplicates.values():
    sorted_sources = sorted(sources)
    for i in range(len(sorted_sources)):
        for j in range(i + 1, len(sorted_sources)):
            pair = (sorted_sources[i], sorted_sources[j])
            pairwise_counts[pair] += 1

print("📊 Duplicate counts by file pair:")
for pair, count in sorted(pairwise_counts.items()):
    print(f"  {pair[0]} ↔ {pair[1]}: {count} duplicates")

# Optional: Print sample duplicates
print("\n🧾 Sample duplicate entries:")
for i, (text, sources) in enumerate(duplicates.items()):
    print(f"[{i+1}] Appears in: {', '.join(sorted(sources))}")
    print(f"     Text: {text}")
    if i >= 9: break  # limit to 10 samples
