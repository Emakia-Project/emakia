from crewai import Agent

bias_agent = Agent(
    role="Bias Analyst",
    goal="Detect political, cultural, or ideological bias in tweet content",
    backstory="Trained to spot loaded language and skewed framing",
    verbose=True
)
