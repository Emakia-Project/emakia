from crewai import Agent

toxicity_agent = Agent(
    role="Toxicity Analyst",
    goal="Classify text based on toxic language patterns using GPT-4o",
    backstory="Expert in detecting offensive, violent, or harmful tone in social content",
    verbose=True
)
