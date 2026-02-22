import matplotlib.pyplot as plt

# Hypothetical data based on your metrics
recall_llm0 = [0.055, 0.1, 0.2]  # low
precision_llm0 = [0.778, 0.7, 0.6]
recall_llm3 = [0.0, 0.666, 1.0]
precision_llm3 = [1.0, 0.808, 0.5]  # dominant
recall_llm4 = [0.0, 0.164, 1.0]
precision_llm4 = [1.0, 0.735, 0.4]


def plot_precision_recall_curves():
    """Plot simple precision–recall curves for three CoreML/LLM models."""
    plt.figure(figsize=(6, 4))
    plt.plot(recall_llm0, precision_llm0, marker="o", label="LLM0 (baseline)")
    plt.plot(recall_llm3, precision_llm3, marker="o", label="LLM3 (optimal)")
    plt.plot(recall_llm4, precision_llm4, marker="o", label="LLM4 (conservative)")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision–Recall Curves vs. Weighted Ensemble Ground Truth")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_precision_recall_curves()
