import os
import google.generativeai as genai
from google.adk.agents.llm_agent import LlmAgent

GEMINI_MODEL = "gemini-2.0-flash"

# Ensure the API key is configured (should be done once in your app)
if os.environ.get("GOOGLE_API_KEY"):
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


def get_misinformation_agent():
    """
    Returns an LlmAgent configured for misinformation analysis.
    """
    return LlmAgent(
        name="MisinformationAnalyst",
        model=GEMINI_MODEL,
        instruction=(
            """You are a fake news analyst. Determine if the following fact is fake news.\n\n"
            "Respond with either 'misinformation' or 'accurate' and \n"
            "    Provide your analysis and include:\n"
            "    - Whether the fact is likely true or false.\n"
            "    - References to sources that support or contradict the fact.\n"
            "    - The author or organization responsible for the content.."""
        ),
        description="Detects misinformation in statements.",
        output_key="misinformation_analysis"
    )
