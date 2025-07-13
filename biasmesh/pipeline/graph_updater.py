from neo4j import GraphDatabase

def update_tweet_metadata_in_neo4j(uri, auth, tweet_id, labels):
    driver = GraphDatabase.driver(uri, auth=auth)
    with driver.session() as session:
        session.run(
            """
            MATCH (t:Tweet {id: $id})
            SET t.toxicity = $tox,
                t.bias = $bias,
                t.misinfo = $mis
            """,
            {
                "id": tweet_id,
                "tox": labels["toxicity"],
                "bias": labels["bias"],
                "mis": labels["misinfo"]
            }
        )
