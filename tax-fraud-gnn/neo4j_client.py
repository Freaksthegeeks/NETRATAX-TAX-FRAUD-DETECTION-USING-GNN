from neo4j import GraphDatabase
import os

# Neo4j connection configuration. These are read from environment variables so you
# can point the code at Neo4j Desktop (bolt://localhost:7687) or AuraDB as needed.
NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "1234567890")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def close_driver():
    driver.close()
