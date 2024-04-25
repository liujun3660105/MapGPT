from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "your_password"))

with driver.session() as session:
    with session.begin_transaction() as tx:
        result = tx.run("MATCH (n) DETACH DELETE n")
        print(result.consume().counters)