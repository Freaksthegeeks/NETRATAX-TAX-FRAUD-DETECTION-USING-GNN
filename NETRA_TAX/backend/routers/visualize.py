"""
Visualization Router
Network graph and fraud ring visualization endpoints
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, Dict, Any, List
import networkx as nx
import json

from services.model_loader import get_graph_data, get_companies_df, get_fraud_proba, get_mappings
from routers.auth import get_current_user

router = APIRouter()

@router.get("/network_graph")
async def get_network_graph(
    gstin: Optional[str] = Query(None, description="Focus on network around this GSTIN"),
    depth: int = Query(2, description="Network depth to explore"),
    current_user: dict = Depends(get_current_user)
):
    """Get network graph data for D3.js visualization"""
    try:
        graph_data = get_graph_data()
        companies_df = get_companies_df()
        fraud_proba = get_fraud_proba()
        mappings = get_mappings()
        
        if graph_data is None:
            raise HTTPException(status_code=500, detail="Graph data not loaded")
        
        # Convert to NetworkX for easier manipulation
        G = nx.Graph()
        
        # Add nodes
        node_list = mappings.get("node_list", list(range(graph_data.num_nodes)))
        for i, node_id in enumerate(node_list):
            fraud_score = float(fraud_proba[i]) * 100 if fraud_proba is not None and i < len(fraud_proba) else 0.0
            
            # Get company info if available
            company_info = {}
            if companies_df is not None and len(companies_df) > i:
                row = companies_df.iloc[i]
                company_info = {
                    "gstin": str(node_id),
                    "name": str(row.get("company_id", node_id)),
                    "location": str(row.get("location", "")),
                    "turnover": float(row.get("turnover", 0))
                }
            
            G.add_node(
                str(node_id),
                fraud_score=fraud_score,
                risk_level="HIGH" if fraud_score > 70 else "MEDIUM" if fraud_score > 30 else "LOW",
                **company_info
            )
        
        # Add edges
        edge_index = graph_data.edge_index.cpu().numpy()
        for i in range(edge_index.shape[1]):
            src = str(node_list[edge_index[0, i]])
            dst = str(node_list[edge_index[1, i]])
            G.add_edge(src, dst)
        
        # If GSTIN specified, get subgraph
        if gstin:
            if gstin in G:
                # Get neighbors up to depth
                subgraph_nodes = {gstin}
                current_level = {gstin}
                for _ in range(depth):
                    next_level = set()
                    for node in current_level:
                        next_level.update(G.neighbors(node))
                    subgraph_nodes.update(next_level)
                    current_level = next_level
                G = G.subgraph(subgraph_nodes)
            else:
                raise HTTPException(status_code=404, detail=f"GSTIN {gstin} not found")
        
        # Convert to D3.js format
        nodes = []
        for node_id, data in G.nodes(data=True):
            nodes.append({
                "id": node_id,
                "fraud_score": data.get("fraud_score", 0),
                "risk_level": data.get("risk_level", "LOW"),
                "name": data.get("name", node_id),
                "location": data.get("location", ""),
                "turnover": data.get("turnover", 0)
            })
        
        links = []
        for src, dst in G.edges():
            links.append({
                "source": src,
                "target": dst
            })
        
        return {
            "nodes": nodes,
            "links": links,
            "total_nodes": len(nodes),
            "total_edges": len(links)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph generation error: {str(e)}")

@router.get("/fraud_ring")
async def get_fraud_ring(
    gstin: str = Query(..., description="GSTIN to analyze fraud ring"),
    current_user: dict = Depends(get_current_user)
):
    """Get fraud ring visualization data"""
    try:
        # Get network graph
        graph_data = await get_network_graph(gstin=gstin, depth=3, current_user=current_user)
        
        # Filter to high-risk nodes only
        high_risk_nodes = [n for n in graph_data["nodes"] if n["fraud_score"] > 70]
        high_risk_ids = {n["id"] for n in high_risk_nodes}
        
        # Filter links to only connect high-risk nodes
        fraud_ring_links = [
            link for link in graph_data["links"]
            if link["source"] in high_risk_ids and link["target"] in high_risk_ids
        ]
        
        return {
            "nodes": high_risk_nodes,
            "links": fraud_ring_links,
            "ring_size": len(high_risk_nodes),
            "connections": len(fraud_ring_links)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fraud ring analysis error: {str(e)}")

