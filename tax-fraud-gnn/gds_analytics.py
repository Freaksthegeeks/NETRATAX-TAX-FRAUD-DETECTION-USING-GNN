"""
Graph Analytics using NetworkX (client-side) + Neo4j
No server-side GDS required — runs locally and writes results back to Neo4j.
"""

from neo4j import GraphDatabase
import networkx as nx
from community import community_louvain
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection configuration from environment variables
NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j+s://c87f29bd.databases.neo4j.io")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "1234567890")

print(f"Using Neo4j URI: {NEO4J_URI} (user: {NEO4J_USER})")
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def export_company_graph():
    """
    Export Company nodes and Company->Company edges from Neo4j.
    Returns: (nodes_dict, edges_list)
    """
    logger.info("Exporting Company nodes and edges from Neo4j...")
    
    nodes = {}
    edges = []
    
    with driver.session() as session:
        # Fetch all companies
        result = session.run(
            """
            MATCH (c:Company)
            RETURN id(c) AS node_id, c.gstin AS gstin, c.name AS name, 
                   c.state AS state, c.is_fraud AS is_fraud
            """
        )
        for record in result:
            node_id = record["node_id"]
            nodes[node_id] = {
                "gstin": record["gstin"],
                "name": record["name"],
                "state": record["state"],
                "is_fraud": record["is_fraud"]
            }
        
        logger.info(f"Loaded {len(nodes)} Company nodes")
        
        # Fetch Company->Company edges (via invoices)
        result = session.run(
            """
            MATCH (s:Company)-[:SUPPLIES_TO]->(:Invoice)-[:BILLED_TO]->(b:Company)
            RETURN DISTINCT id(s) AS source, id(b) AS target
            """
        )
        for record in result:
            edges.append((record["source"], record["target"]))
        
        logger.info(f"Loaded {len(edges)} edges")
    
    return nodes, edges


def build_networkx_graph(nodes, edges):
    """Build a NetworkX directed graph from nodes and edges."""
    logger.info("Building NetworkX graph...")
    G = nx.DiGraph()
    
    # Add nodes with attributes
    for node_id, attrs in nodes.items():
        G.add_node(node_id, **attrs)
    
    # Add edges
    for source, target in edges:
        G.add_edge(source, target)
    
    logger.info(f"NetworkX graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def run_pagerank(graph):
    """Run PageRank on the graph."""
    logger.info("Running PageRank...")
    pagerank = nx.pagerank(graph, alpha=0.85, max_iter=100, tol=1e-06)
    logger.info(f"PageRank computed for {len(pagerank)} nodes")
    return pagerank


def run_louvain(graph):
    """Run Louvain community detection on undirected version of graph."""
    logger.info("Running Louvain community detection...")
    graph_undirected = graph.to_undirected()
    partition = community_louvain.best_partition(graph_undirected)
    logger.info(f"Found {len(set(partition.values()))} communities")
    return partition


def run_wcc(graph):
    """Run Weakly Connected Components."""
    logger.info("Running WCC (Weakly Connected Components)...")
    wcc_map = {}
    for wcc_id, component in enumerate(nx.weakly_connected_components(graph)):
        for node in component:
            wcc_map[node] = wcc_id
    logger.info(f"Found {len(set(wcc_map.values()))} weakly connected components")
    return wcc_map


def write_properties_to_neo4j(nodes, pagerank, community_map, wcc_map):
    """Write PageRank, community_id, and wcc_id back to Neo4j."""
    logger.info("Writing properties back to Neo4j...")
    
    with driver.session() as session:
        # Batch update properties
        for node_id in nodes.keys():
            pr = pagerank.get(node_id, 0.0)
            comm = community_map.get(node_id, -1)
            wcc = wcc_map.get(node_id, -1)
            
            session.run(
                """
                MATCH (c:Company) WHERE id(c) = $node_id
                SET c.pagerank = $pagerank, c.community_id = $community_id, c.wcc_id = $wcc_id
                """,
                node_id=node_id,
                pagerank=float(pr),
                community_id=int(comm),
                wcc_id=int(wcc)
            )
    
    logger.info("Properties written to Neo4j")


def report_top_pagerank(limit=10):
    """Query Neo4j for top companies by pagerank."""
    logger.info(f"\n=== TOP {limit} COMPANIES BY PAGERANK ===")
    
    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:Company)
               WHERE c.pagerank IS NOT NULL
            RETURN c.gstin AS gstin, c.name AS name, c.state AS state, 
                   c.pagerank AS pagerank, c.is_fraud AS is_fraud
            ORDER BY c.pagerank DESC
            LIMIT $limit
            """,
            limit=limit
        )
        
        for i, record in enumerate(result, 1):
            gstin = record["gstin"]
            name = record["name"]
            state = record["state"]
            pr = record["pagerank"]
            fraud = record["is_fraud"]
            print(f"{i}. {gstin} ({name}) - State: {state}, PageRank: {pr:.4f}, Fraud: {fraud}")


def report_large_communities(min_size=4):
    """List communities with size >= min_size."""
    logger.info(f"\n=== COMMUNITIES WITH SIZE >= {min_size} ===")
    
    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:Company)
               WHERE c.community_id IS NOT NULL
            WITH c.community_id AS comm, collect(c.gstin) AS members
            WHERE size(members) >= $min_size
            RETURN comm, size(members) AS size, members[0..5] AS sample_members
            ORDER BY size DESC
            """,
            min_size=min_size
        )
        
        for i, record in enumerate(result, 1):
            comm_id = record["comm"]
            size = record["size"]
            samples = record["sample_members"]
            print(f"{i}. Community {comm_id}: {size} members, Samples: {samples}")


def run_all_analytics():
    """Run complete analytics pipeline: export, analyze, write back, report."""
    try:
        # Export data from Neo4j
        nodes, edges = export_company_graph()
        
        if not nodes or not edges:
            logger.warning("No nodes or edges found in Neo4j. Skipping analytics.")
            return
        
        # Build NetworkX graph
        G = build_networkx_graph(nodes, edges)
        
        # Run algorithms
        pagerank = run_pagerank(G)
        community_map = run_louvain(G)
        wcc_map = run_wcc(G)
        
        # Write results back to Neo4j
        write_properties_to_neo4j(nodes, pagerank, community_map, wcc_map)
        
        # Report
        report_top_pagerank(10)
        report_large_communities(4)
        
        logger.info("\n✓ Analytics complete!")
    
    except Exception as e:
        logger.error(f"Error during analytics: {e}", exc_info=True)
    
    finally:
        driver.close()


if __name__ == "__main__":
    logger.info("Starting client-side graph analytics (NetworkX)...")
    run_all_analytics()
