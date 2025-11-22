"""
Pattern Detection Service
Detect fraud patterns: circular trading, fraud rings, etc.
"""

import torch
import numpy as np
from typing import List, Dict, Any
import logging
from collections import defaultdict, deque

from services.model_loader import get_graph_data, get_companies_df, get_fraud_proba, get_mappings

logger = logging.getLogger(__name__)

def detect_circular_trading(graph_data, companies_df=None) -> List[Dict[str, Any]]:
    """Detect circular trading patterns"""
    try:
        if graph_data is None:
            return []
        
        # Convert to simple graph representation
        edge_index = graph_data.edge_index.cpu().numpy()
        num_nodes = graph_data.num_nodes
        
        # Build adjacency list
        adj_list = defaultdict(set)
        for i in range(edge_index.shape[1]):
            src, dst = int(edge_index[0, i]), int(edge_index[1, i])
            adj_list[src].add(dst)
            adj_list[dst].add(src)
        
        # Detect cycles of length 3-5 (circular trading)
        cycles = []
        visited = set()
        
        def find_cycles(node, path, target_length):
            if len(path) == target_length:
                if path[0] in adj_list[node]:
                    cycles.append(path + [node])
                return
            
            for neighbor in adj_list[node]:
                if neighbor not in path and neighbor not in visited:
                    find_cycles(neighbor, path + [node], target_length)
        
        for node in range(min(100, num_nodes)):  # Limit search for performance
            if node not in visited:
                for length in [3, 4, 5]:
                    find_cycles(node, [], length)
                visited.add(node)
        
        return [{"cycle": cycle, "length": len(cycle)} for cycle in cycles[:10]]
    except Exception as e:
        logger.error(f"Error detecting circular trading: {e}")
        return []

def detect_fraud_rings(graph_data, companies_df=None) -> List[Dict[str, Any]]:
    """Detect fraud rings (clusters of high-risk nodes)"""
    try:
        fraud_proba = get_fraud_proba()
        if fraud_proba is None or graph_data is None:
            return []
        
        # Find high-risk nodes
        high_risk_nodes = np.where(fraud_proba > 0.7)[0]
        
        if len(high_risk_nodes) == 0:
            return []
        
        # Build subgraph of high-risk nodes
        edge_index = graph_data.edge_index.cpu().numpy()
        high_risk_set = set(high_risk_nodes.tolist())
        
        rings = []
        visited = set()
        
        def dfs_ring(node, component):
            visited.add(node)
            component.append(int(node))
            for i in range(edge_index.shape[1]):
                src, dst = int(edge_index[0, i]), int(edge_index[1, i])
                if src == node and dst in high_risk_set and dst not in visited:
                    dfs_ring(dst, component)
                elif dst == node and src in high_risk_set and src not in visited:
                    dfs_ring(src, component)
        
        for node in high_risk_nodes:
            if node not in visited:
                component = []
                dfs_ring(int(node), component)
                if len(component) >= 3:  # Ring must have at least 3 nodes
                    rings.append({
                        "nodes": component,
                        "size": len(component),
                        "average_risk": float(fraud_proba[component].mean() * 100)
                    })
        
        return sorted(rings, key=lambda x: x["size"], reverse=True)[:10]
    except Exception as e:
        logger.error(f"Error detecting fraud rings: {e}")
        return []

def detect_high_degree_nodes(graph_data, companies_df=None) -> List[Dict[str, Any]]:
    """Detect nodes with unusually high degree (potential shell companies)"""
    try:
        if graph_data is None:
            return []
        
        edge_index = graph_data.edge_index.cpu().numpy()
        num_nodes = graph_data.num_nodes
        
        # Calculate degrees
        degrees = defaultdict(int)
        for i in range(edge_index.shape[1]):
            src, dst = int(edge_index[0, i]), int(edge_index[1, i])
            degrees[src] += 1
            degrees[dst] += 1
        
        # Find nodes with degree > 2 standard deviations above mean
        if len(degrees) == 0:
            return []
        
        degree_values = list(degrees.values())
        mean_degree = np.mean(degree_values)
        std_degree = np.std(degree_values)
        threshold = mean_degree + 2 * std_degree
        
        high_degree_nodes = [
            {"node_id": node, "degree": degree}
            for node, degree in degrees.items()
            if degree > threshold
        ]
        
        return sorted(high_degree_nodes, key=lambda x: x["degree"], reverse=True)[:20]
    except Exception as e:
        logger.error(f"Error detecting high degree nodes: {e}")
        return []

def detect_sudden_spikes(companies_df) -> List[Dict[str, Any]]:
    """Detect sudden transaction spikes (if time series data available)"""
    try:
        if companies_df is None or len(companies_df) == 0:
            return []
        
        # This would require time series data
        # For now, return empty list
        return []
    except Exception as e:
        logger.error(f"Error detecting sudden spikes: {e}")
        return []

