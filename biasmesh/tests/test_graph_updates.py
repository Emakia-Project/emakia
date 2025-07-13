def test_graph_updater():
    from pipeline.graph_updater import update_graph
    update_graph("bolt://localhost:7687", ("neo4j", "password"), "12345", {
        "toxicity": "Not Toxic",
        "bias": "Neutral",
        "misinfo": "Accurate"
    })
