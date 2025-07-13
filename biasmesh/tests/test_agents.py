def test_agents():
    from agents.toxicity_agent import toxicity_agent
    assert toxicity_agent.think("You suck!") in ["Toxic", "⚠️ Unknown"]
