from agents.toxicity_agent import toxicity_agent
from agents.bias_agent import bias_agent
from agents.misinfo_agent import misinfo_agent

def classify_text(text):
    return {
        "toxicity": toxicity_agent.think(text),
        "bias": bias_agent.think(text),
        "misinfo": misinfo_agent.think(text)
    }
