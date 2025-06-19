import os
import google.generativeai as genai
from google.adk.agents.llm_agent import LlmAgent

GEMINI_MODEL = "gemini-2.0-flash"

# Ensure the API key is configured (should be done once in your app)
if os.environ.get("GOOGLE_API_KEY"):
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


def get_toxicity_agent():
    """
    Returns an LlmAgent configured for toxicity analysis.
    """
    return LlmAgent(
        name="ToxicityAnalyst",
        model=GEMINI_MODEL,
        instruction=(
            """You are an AI Toxicity Analyst. Analyze the following statement and determine if it contains toxic language.\n"
            "Respond with either 'toxic' or 'non-toxic'."""
        ),
        description="Analyzes statements for toxicity.",
        output_key="toxicity_analysis"
    )
