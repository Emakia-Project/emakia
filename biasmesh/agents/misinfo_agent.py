from crewai import Agent

misinfo_agent = Agent(
    role="Misinformation Analyst",
    goal="Identify false or misleading claims in social posts",
    backstory="Specialist in evaluating sources and factual consistency",
    verbose=True
)
