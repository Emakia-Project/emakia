import os
import google.generativeai as genai
from google.adk.agents.llm_agent import LlmAgent

GEMINI_MODEL = "gemini-2.0-flash"

# Ensure the API key is configured (should be done once in your app)
if os.environ.get("GOOGLE_API_KEY"):
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


def get_bias_agent():
    """
    Returns an LlmAgent configured for bias analysis.
    """
    return LlmAgent(
        name="BiasAnalyst",
        model=GEMINI_MODEL,
        instruction=(
            """You are an AI Bias Analyst. Assess the following statement for bias.\n"
            "Indicate whether the statement contains 'bias' or is 'neutral' and Provide your analysis and include:\n"
            "- Whether the fact is likely true or false.\n"
            "- References to sources that support or contradict the fact.\n"
            "- The author or organization responsible for the content.\n"""
        ),
        description="Analyzes statements for bias.",
        output_key="bias_analysis"
    )
