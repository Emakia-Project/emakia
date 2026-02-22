import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


def get_neo4j_driver():
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USER")
    password = os.environ.get("NEO4J_PASSWORD")
    if not uri or not user or not password:
        raise ValueError(
            "Missing Neo4j config. Set NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD (in env or .env)."
        )
    return GraphDatabase.driver(uri, auth=(user, password))


def test_connection():
    """Test Neo4j connection and run a simple query."""
    driver = get_neo4j_driver()
    try:
        driver.verify_connectivity()
        print("✅ Neo4j connection verified")
        with driver.session() as session:
            result = session.run("RETURN 1 AS num")
            row = result.single()
            print(f"✅ Query OK: RETURN {row['num']}")
    finally:
        driver.close()
        print("✅ Driver closed")


if __name__ == "__main__":
    test_connection()