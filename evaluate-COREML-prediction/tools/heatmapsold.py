import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

labels = ["GPT-4", "Gemini", "Grok", "LLaMA", "DeepSeek", "Claude"]

# Hypothetical kappa matrix (high diagonal, varied off-diagonal)
data = np.array(
    [
        [1.0, 0.85, 0.78, 0.82, 0.80, 0.65],
        [0.85, 1.0, 0.82, 0.88, 0.84, 0.70],
        [0.78, 0.82, 1.0, 0.79, 0.81, 0.55],  # lower with Claude
        [0.82, 0.88, 0.79, 1.0, 0.86, 0.68],
        [0.80, 0.84, 0.81, 0.86, 1.0, 0.62],
        [0.65, 0.70, 0.55, 0.68, 0.62, 1.0],
    ]
)


def plot_llm_agreement_heatmap():
    """Plot pairwise LLM agreement heatmap (Cohen's kappa-style)."""
    plt.figure(figsize=(6, 5))
    sns.heatmap(
        data,
        annot=True,
        xticklabels=labels,
        yticklabels=labels,
        cmap="Blues",
        vmin=0.0,
        vmax=1.0,
    )
    plt.title("Pairwise LLM Agreement Heatmap (Cohen's Kappa)")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_llm_agreement_heatmap()