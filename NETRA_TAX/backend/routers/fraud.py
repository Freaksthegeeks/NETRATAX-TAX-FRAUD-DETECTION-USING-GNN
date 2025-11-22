"""
Fraud Detection Router
Company risk, invoice risk, and pattern analysis endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import numpy as np
import torch

from services.model_loader import (
    get_model, get_graph_data, get_companies_df, 
    get_invoices_df, get_mappings, get_fraud_proba, get_device
)
from services.inference import (
    node_risk, invoice_risk, network_analysis, fraud_explanation
)
from services.pattern_detection import (
    detect_circular_trading, detect_fraud_rings, 
    detect_high_degree_nodes, detect_sudden_spikes
)
from routers.auth import get_current_user

router = APIRouter()

class RiskResponse(BaseModel):
    fraud_score: float
    risk_level: str
    reasons: List[str]
    connected_entities: List[Dict[str, Any]]
    pattern_flags: List[str]

class CompanyRiskResponse(BaseModel):
    gstin: str
    fraud_score: float
    risk_level: str
    reasons: List[str]
    connected_entities: List[Dict[str, Any]]
    pattern_flags: List[str]
    company_name: Optional[str] = None
    location: Optional[str] = None

class InvoiceRiskResponse(BaseModel):
    invoice_id: str
    fraud_score: float
    risk_level: str
    reasons: List[str]
    supplier_gstin: Optional[str] = None
    buyer_gstin: Optional[str] = None
    amount: Optional[float] = None

@router.get("/company_risk", response_model=CompanyRiskResponse)
async def get_company_risk(
    gstin: str = Query(..., description="GSTIN of the company"),
    current_user: dict = Depends(get_current_user)
):
    """Get fraud risk for a company by GSTIN"""
    try:
        result = node_risk(gstin)
        return CompanyRiskResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Company not found or error: {str(e)}")

@router.get("/invoice_risk", response_model=InvoiceRiskResponse)
async def get_invoice_risk(
    invoice_id: str = Query(..., description="Invoice number or ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get fraud risk for an invoice"""
    try:
        result = invoice_risk(invoice_id)
        return InvoiceRiskResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Invoice not found or error: {str(e)}")

@router.get("/graph_pattern_analysis")
async def graph_pattern_analysis(
    gstin: Optional[str] = Query(None, description="Optional GSTIN to analyze specific network"),
    current_user: dict = Depends(get_current_user)
):
    """Analyze graph patterns for fraud detection"""
    try:
        graph_data = get_graph_data()
        companies_df = get_companies_df()
        
        patterns = {
            "circular_trading": detect_circular_trading(graph_data, companies_df),
            "fraud_rings": detect_fraud_rings(graph_data, companies_df),
            "high_degree_nodes": detect_high_degree_nodes(graph_data, companies_df),
            "sudden_spikes": detect_sudden_spikes(companies_df) if companies_df is not None else []
        }
        
        if gstin:
            # Analyze specific network around GSTIN
            network = network_analysis(gstin)
            patterns["network_analysis"] = network
        
        return patterns
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pattern analysis error: {str(e)}")

@router.get("/fraud_summary")
async def get_fraud_summary(current_user: dict = Depends(get_current_user)):
    """Get overall fraud detection summary"""
    try:
        fraud_proba = get_fraud_proba()
        companies_df = get_companies_df()
        graph_data = get_graph_data()
        
        if fraud_proba is None or len(fraud_proba) == 0:
            return {
                "total_entities": 0,
                "high_risk_count": 0,
                "medium_risk_count": 0,
                "low_risk_count": 0,
                "average_fraud_score": 0.0
            }
        
        high_risk = (fraud_proba > 0.7).sum()
        medium_risk = ((fraud_proba > 0.3) & (fraud_proba <= 0.7)).sum()
        low_risk = (fraud_proba <= 0.3).sum()
        
        return {
            "total_entities": len(fraud_proba),
            "high_risk_count": int(high_risk),
            "medium_risk_count": int(medium_risk),
            "low_risk_count": int(low_risk),
            "average_fraud_score": float(np.mean(fraud_proba) * 100),
            "total_edges": int(graph_data.num_edges) if graph_data else 0,
            "total_nodes": int(graph_data.num_nodes) if graph_data else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary error: {str(e)}")

@router.get("/explain/{node_id}")
async def explain_fraud(
    node_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get explanation for fraud prediction"""
    try:
        explanation = fraud_explanation(node_id)
        return explanation
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Explanation error: {str(e)}")

