"""
GNN Inference Service
Core inference functions for fraud detection
"""

import torch
import numpy as np
from typing import Dict, List, Any, Optional
import logging

from services.model_loader import (
    get_model, get_graph_data, get_companies_df,
    get_invoices_df, get_mappings, get_fraud_proba, get_device
)

logger = logging.getLogger(__name__)

def node_risk(gstin: str) -> Dict[str, Any]:
    """
    Get fraud risk for a node (company) by GSTIN
    
    Returns:
        {
            "fraud_score": 0-100,
            "risk_level": "LOW"|"MEDIUM"|"HIGH",
            "reasons": [],
            "connected_entities": [],
            "pattern_flags": []
        }
    """
    try:
        model = get_model()
        graph_data = get_graph_data()
        companies_df = get_companies_df()
        mappings = get_mappings()
        fraud_proba = get_fraud_proba()
        device = get_device()
        
        if model is None or graph_data is None:
            raise ValueError("Model or graph data not loaded")
        
        # Find node index for GSTIN
        node_list = mappings.get("node_list", [])
        if gstin not in node_list:
            # Try to find in companies dataframe
            if companies_df is not None:
                company_row = companies_df[companies_df["company_id"].astype(str) == str(gstin)]
                if len(company_row) > 0:
                    idx = company_row.index[0]
                    if idx < len(fraud_proba):
                        fraud_score = float(fraud_proba[idx]) * 100
                    else:
                        fraud_score = 0.0
                else:
                    raise ValueError(f"GSTIN {gstin} not found")
            else:
                raise ValueError(f"GSTIN {gstin} not found")
        else:
            node_idx = node_list.index(gstin)
            if node_idx < len(fraud_proba):
                fraud_score = float(fraud_proba[node_idx]) * 100
            else:
                fraud_score = 0.0
        
        # Determine risk level
        if fraud_score > 70:
            risk_level = "HIGH"
        elif fraud_score > 30:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Get reasons
        reasons = []
        if fraud_score > 70:
            reasons.append("High fraud probability detected by GNN model")
        if fraud_score > 50:
            reasons.append("Suspicious transaction patterns identified")
        
        # Get connected entities
        connected_entities = []
        if graph_data is not None:
            edge_index = graph_data.edge_index.cpu().numpy()
            node_idx = node_list.index(gstin) if gstin in node_list else -1
            if node_idx >= 0:
                # Find neighbors
                neighbors = set()
                for i in range(edge_index.shape[1]):
                    if edge_index[0, i] == node_idx:
                        neighbors.add(int(edge_index[1, i]))
                    elif edge_index[1, i] == node_idx:
                        neighbors.add(int(edge_index[0, i]))
                
                for neighbor_idx in list(neighbors)[:10]:  # Limit to 10
                    if neighbor_idx < len(node_list):
                        neighbor_id = node_list[neighbor_idx]
                        neighbor_score = float(fraud_proba[neighbor_idx]) * 100 if neighbor_idx < len(fraud_proba) else 0.0
                        connected_entities.append({
                            "gstin": str(neighbor_id),
                            "fraud_score": neighbor_score
                        })
        
        # Pattern flags
        pattern_flags = []
        if fraud_score > 70:
            pattern_flags.append("HIGH_RISK_NODE")
        if len(connected_entities) > 20:
            pattern_flags.append("HIGH_DEGREE_NODE")
        
        return {
            "gstin": gstin,
            "fraud_score": fraud_score,
            "risk_level": risk_level,
            "reasons": reasons,
            "connected_entities": connected_entities,
            "pattern_flags": pattern_flags
        }
    except Exception as e:
        logger.error(f"Error in node_risk for {gstin}: {e}")
        raise

def invoice_risk(invoice_id: str) -> Dict[str, Any]:
    """
    Get fraud risk for an invoice
    
    Returns:
        {
            "invoice_id": str,
            "fraud_score": 0-100,
            "risk_level": "LOW"|"MEDIUM"|"HIGH",
            "reasons": [],
            "supplier_gstin": str,
            "buyer_gstin": str,
            "amount": float
        }
    """
    try:
        invoices_df = get_invoices_df()
        companies_df = get_companies_df()
        
        if invoices_df is None or len(invoices_df) == 0:
            raise ValueError("Invoice data not available")
        
        # Find invoice
        invoice_row = invoices_df[invoices_df["invoice_id"].astype(str) == str(invoice_id)]
        if len(invoice_row) == 0:
            # Try invoice_no column
            invoice_row = invoices_df[invoices_df.get("invoice_no", invoices_df.columns[0]).astype(str) == str(invoice_id)]
        
        if len(invoice_row) == 0:
            raise ValueError(f"Invoice {invoice_id} not found")
        
        row = invoice_row.iloc[0]
        
        # Get supplier and buyer risk
        supplier_gstin = str(row.get("seller_id", row.get("Supplier_GSTIN", "")))
        buyer_gstin = str(row.get("buyer_id", row.get("Buyer_GSTIN", "")))
        
        supplier_risk = 0.0
        buyer_risk = 0.0
        
        try:
            supplier_result = node_risk(supplier_gstin)
            supplier_risk = supplier_result["fraud_score"]
        except:
            pass
        
        try:
            buyer_result = node_risk(buyer_gstin)
            buyer_risk = buyer_result["fraud_score"]
        except:
            pass
        
        # Calculate invoice risk (average of supplier and buyer, with amount factor)
        amount = float(row.get("amount", 0))
        base_risk = (supplier_risk + buyer_risk) / 2
        
        # Adjust for amount (higher amounts = higher risk)
        if amount > 1000000:
            base_risk += 10
        elif amount > 100000:
            base_risk += 5
        
        fraud_score = min(100, base_risk)
        
        if fraud_score > 70:
            risk_level = "HIGH"
        elif fraud_score > 30:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        reasons = []
        if supplier_risk > 70:
            reasons.append(f"High-risk supplier: {supplier_gstin}")
        if buyer_risk > 70:
            reasons.append(f"High-risk buyer: {buyer_gstin}")
        if amount > 1000000:
            reasons.append("Unusually high transaction amount")
        
        return {
            "invoice_id": invoice_id,
            "fraud_score": fraud_score,
            "risk_level": risk_level,
            "reasons": reasons,
            "supplier_gstin": supplier_gstin,
            "buyer_gstin": buyer_gstin,
            "amount": amount
        }
    except Exception as e:
        logger.error(f"Error in invoice_risk for {invoice_id}: {e}")
        raise

def network_analysis(gstin: str) -> Dict[str, Any]:
    """Analyze network around a GSTIN"""
    try:
        result = node_risk(gstin)
        graph_data = get_graph_data()
        mappings = get_mappings()
        
        node_list = mappings.get("node_list", [])
        if gstin not in node_list:
            raise ValueError(f"GSTIN {gstin} not found")
        
        node_idx = node_list.index(gstin)
        
        # Get network statistics
        edge_index = graph_data.edge_index.cpu().numpy()
        neighbors = set()
        for i in range(edge_index.shape[1]):
            if edge_index[0, i] == node_idx:
                neighbors.add(int(edge_index[1, i]))
            elif edge_index[1, i] == node_idx:
                neighbors.add(int(edge_index[0, i]))
        
        return {
            "gstin": gstin,
            "degree": len(neighbors),
            "connected_entities": result["connected_entities"],
            "network_size": len(neighbors),
            "fraud_score": result["fraud_score"]
        }
    except Exception as e:
        logger.error(f"Error in network_analysis for {gstin}: {e}")
        raise

def fraud_explanation(node_id: str) -> Dict[str, Any]:
    """Get explanation for fraud prediction"""
    try:
        result = node_risk(node_id)
        
        return {
            "node_id": node_id,
            "fraud_score": result["fraud_score"],
            "risk_level": result["risk_level"],
            "explanation": {
                "primary_reasons": result["reasons"],
                "pattern_flags": result["pattern_flags"],
                "network_context": {
                    "connected_entities_count": len(result["connected_entities"]),
                    "high_risk_connections": len([e for e in result["connected_entities"] if e["fraud_score"] > 70])
                }
            }
        }
    except Exception as e:
        logger.error(f"Error in fraud_explanation for {node_id}: {e}")
        raise

