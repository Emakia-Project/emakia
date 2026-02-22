import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

labels = ["GPT-4", "Gemini", "Grok", "LLaMA", "DeepSeek", "Claude"]

# F1 scores from your table
data = np.array([
    [0.107, 0.719, 0.284],   # GPT-4
    [0.096, 0.742, 0.277],   # Gemini
    [0.099, 0.713, 0.266],   # Grok
    [0.108, 0.734, 0.282],   # LLaMA
    [0.098, 0.741, 0.273],   # DeepSeek
    [0.148, 0.229, 0.097],   # Claude
])

columns = ["LLM0 F1", "LLM3 F1", "LLM4 F1"]

def plot_llm_f1_heatmap():
    """Plot heatmap of F1 scores for each adjudicator across LLM0/LLM3/LLM4."""
    plt.figure(figsize=(7, 5))
    sns.heatmap(
        data,
        annot=True,
        xticklabels=columns,
        yticklabels=labels,
        cmap="Blues",
        vmin=0.0,
        vmax=1.0,
        fmt=".3f"
    )
    plt.title("LLM Adjudicator F1 Scores Across Label Variants")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_llm_f1_heatmap()
