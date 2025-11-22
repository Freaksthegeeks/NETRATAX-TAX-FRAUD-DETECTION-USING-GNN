"""
Graph Construction Module
Builds NetworkX and PyTorch Geometric graph representations
"""

import pandas as pd
import numpy as np
import networkx as nx
import torch
from torch_geometric.data import Data
from pathlib import Path
import logging
import pickle

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GraphBuilder:
    """Construct and convert transaction graphs to GNN-compatible formats"""
    
    def __init__(self, processed_data_path="../../data/processed"):
        self.data_path = Path(processed_data_path)
        self.graph_path = self.data_path / "graphs"
        self.graph_path.mkdir(exist_ok=True)
        logger.info(f"GraphBuilder initialized. Data path: {self.data_path}")
    
    def load_processed_data(self):
        """Load cleaned data"""
        try:
            companies = pd.read_csv(self.data_path / "companies_processed.csv")
            invoices = pd.read_csv(self.data_path / "invoices_processed.csv")
            logger.info(f"Loaded {len(companies)} companies and {len(invoices)} invoices")
            return companies, invoices
        except FileNotFoundError as e:
            logger.error(f"Processed data files not found: {e}")
            raise
    
    def build_networkx_graph(self, companies, invoices):
        """
        Build NetworkX directed graph:
        - Nodes: Companies with attributes (turnover, location, fraud label, etc.)
        - Edges: Invoices with attributes (amount, ITC claimed)
        """
        G = nx.DiGraph()
        logger.info("Building NetworkX directed graph...")
        
        # Add nodes with attributes
        for _, row in companies.iterrows():
            try:
                G.add_node(
                    int(row["company_id"]),
                    turnover=float(row.get("turnover", 0)),
                    location=str(row.get("location", "Unknown")),
                    is_fraud=int(row.get("is_fraud", 0)),
                    sent_invoices=float(row.get("sent_invoice_count", 0)),
                    received_invoices=float(row.get("received_invoice_count", 0)),
                    total_sent_amount=float(row.get("total_sent_amount", 0)),
                    total_received_amount=float(row.get("total_received_amount", 0))
                )
            except Exception as e:
                logger.warning(f"Error adding node {row.get('company_id')}: {e}")
                continue
        
        logger.info(f"Added {G.number_of_nodes()} nodes")
        
        # Add edges with attributes
        for _, row in invoices.iterrows():
            try:
                seller = int(row["seller_id"])
                buyer = int(row["buyer_id"])
                
                # Only add edge if both nodes exist
                if seller in G and buyer in G:
                    G.add_edge(
                        seller,
                        buyer,
                        amount=float(row.get("amount", 0)),
                        itc_claimed=float(row.get("itc_claimed", 0))
                    )
            except Exception as e:
                logger.warning(f"Error adding edge: {e}")
                continue
        
        logger.info(f"Added {G.number_of_edges()} edges")
        return G
    
    def networkx_to_pytorch_geometric(self, G, companies):
        """
        Convert NetworkX graph to PyTorch Geometric Data object
        - Node features: turnover, sent_invoices, received_invoices
        - Edge indices: directed edges from invoice transactions
        - Edge attributes: invoice amount
        """
        logger.info("Converting to PyTorch Geometric format...")
        
        # Create node list and feature matrix
        node_list = sorted(list(G.nodes()))
        node_to_idx = {node: idx for idx, node in enumerate(node_list)}
        
        x_list = []
        y_list = []
        
        for node in node_list:
            node_data = G.nodes[node]
            features = [
                node_data.get("turnover", 0),
                node_data.get("sent_invoices", 0),
                node_data.get("received_invoices", 0)
            ]
            x_list.append(features)
            y_list.append(node_data.get("is_fraud", 0))
        
        x = torch.tensor(x_list, dtype=torch.float32)
        y = torch.tensor(y_list, dtype=torch.long)
        
        logger.info(f"Node feature matrix shape: {x.shape}")
        
        # Create edge indices and attributes
        edge_index = []
        edge_attr = []
        
        for u, v, data in G.edges(data=True):
            u_idx = node_to_idx[u]
            v_idx = node_to_idx[v]
            edge_index.append([u_idx, v_idx])
            edge_attr.append([data.get("amount", 0)])
        
        if edge_index:
            edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
            edge_attr = torch.tensor(edge_attr, dtype=torch.float32)
        else:
            edge_index = torch.zeros((2, 0), dtype=torch.long)
            edge_attr = torch.zeros((0, 1), dtype=torch.float32)
        
        logger.info(f"Edge index shape: {edge_index.shape}")
        
        # Create PyG Data object
        data = Data(
            x=x,
            edge_index=edge_index,
            edge_attr=edge_attr,
            y=y,
            node_ids=torch.tensor(node_list, dtype=torch.long)
        )
        
        return data, node_list, node_to_idx
    
    def compute_graph_statistics(self, G, data):
        """Compute and log graph statistics"""
        logger.info("=" * 60)
        logger.info("GRAPH STATISTICS")
        logger.info("=" * 60)
        logger.info(f"Number of nodes: {G.number_of_nodes()}")
        logger.info(f"Number of edges: {G.number_of_edges()}")
        logger.info(f"Graph density: {nx.density(G):.4f}")
        
        # Degree statistics
        in_degrees = [d for n, d in G.in_degree()]
        out_degrees = [d for n, d in G.out_degree()]
        logger.info(f"Average in-degree: {np.mean(in_degrees):.2f}")
        logger.info(f"Average out-degree: {np.mean(out_degrees):.2f}")
        
        # Fraud statistics
        fraud_nodes = sum(1 for n in G.nodes() if G.nodes[n].get("is_fraud") == 1)
        logger.info(f"Fraudulent companies: {fraud_nodes} ({100*fraud_nodes/G.number_of_nodes():.2f}%)")
        logger.info("=" * 60)
    
    def build_and_save(self):
        """Execute complete graph building pipeline"""
        try:
            logger.info("=" * 60)
            logger.info("STARTING GRAPH CONSTRUCTION PIPELINE")
            logger.info("=" * 60)
            
            # Load data
            companies, invoices = self.load_processed_data()
            
            # Build NetworkX graph
            G = self.build_networkx_graph(companies, invoices)
            
            # Convert to PyTorch Geometric
            data, node_list, node_to_idx = self.networkx_to_pytorch_geometric(G, companies)
            
            # Compute statistics
            self.compute_graph_statistics(G, data)
            
            # Save graph objects
            logger.info("Saving graph files...")
            torch.save(data, self.graph_path / "graph_data.pt")
            logger.info(f"✓ PyTorch Geometric graph: {self.graph_path / 'graph_data.pt'}")
            
            # Save mappings
            mappings = {
                "node_list": node_list,
                "node_to_idx": node_to_idx
            }
            with open(self.graph_path / "node_mappings.pkl", "wb") as f:
                pickle.dump(mappings, f)
            logger.info(f"✓ Node mappings: {self.graph_path / 'node_mappings.pkl'}")
            
            # Save NetworkX graph
            nx.write_gpickle(G, self.graph_path / "networkx_graph.gpickle")
            logger.info(f"✓ NetworkX graph: {self.graph_path / 'networkx_graph.gpickle'}")
            
            logger.info("=" * 60)
            logger.info("✅ GRAPH CONSTRUCTION COMPLETE")
            logger.info("=" * 60)
            
            return data, G, node_list, node_to_idx
            
        except Exception as e:
            logger.error(f"Error during graph construction: {e}")
            raise


if __name__ == "__main__":
    builder = GraphBuilder()
    data, G, node_list, node_to_idx = builder.build_and_save()
    print(f"\nPyTorch Geometric Data:")
    print(f"  Nodes: {data.num_nodes}")
    print(f"  Edges: {data.num_edges}")
    print(f"  Node features: {data.x.shape}")
    print(f"  Edge features: {data.edge_attr.shape}")
