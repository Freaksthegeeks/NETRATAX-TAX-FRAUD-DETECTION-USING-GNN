"""
System Router
Health checks, configuration, and model info
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any
import torch

from services.model_loader import (
    get_model, get_graph_data, get_companies_df,
    get_invoices_df, get_device
)
from routers.auth import get_current_user

router = APIRouter()

class SystemHealth(BaseModel):
    status: str
    model_loaded: bool
    graph_loaded: bool
    data_loaded: bool
    device: str

class ModelInfo(BaseModel):
    model_type: str
    in_channels: int
    hidden_channels: int
    out_channels: int
    device: str
    graph_nodes: int
    graph_edges: int
    companies_count: int
    invoices_count: int

@router.get("/health", response_model=SystemHealth)
async def health_check():
    """System health check"""
    model = get_model()
    graph_data = get_graph_data()
    companies_df = get_companies_df()
    device = get_device()
    
    return SystemHealth(
        status="healthy",
        model_loaded=model is not None,
        graph_loaded=graph_data is not None,
        data_loaded=companies_df is not None and len(companies_df) > 0,
        device=str(device) if device else "unknown"
    )

@router.get("/config")
async def get_config(current_user: dict = Depends(get_current_user)):
    """Get system configuration"""
    return {
        "system_name": "NETRA TAX",
        "version": "1.0.0",
        "features": {
            "authentication": True,
            "file_upload": True,
            "fraud_detection": True,
            "graph_visualization": True,
            "pdf_reports": True,
            "pattern_detection": True
        }
    }

@router.get("/model_info", response_model=ModelInfo)
async def get_model_info(current_user: dict = Depends(get_current_user)):
    """Get model information"""
    model = get_model()
    graph_data = get_graph_data()
    companies_df = get_companies_df()
    invoices_df = get_invoices_df()
    device = get_device()
    
    if model is None or graph_data is None:
        raise HTTPException(status_code=500, detail="Model or graph data not loaded")
    
    return ModelInfo(
        model_type=getattr(model, 'model_type', 'gcn'),
        in_channels=graph_data.x.shape[1] if graph_data.x is not None else 0,
        hidden_channels=64,
        out_channels=2,
        device=str(device),
        graph_nodes=int(graph_data.num_nodes),
        graph_edges=int(graph_data.num_edges),
        companies_count=len(companies_df) if companies_df is not None else 0,
        invoices_count=len(invoices_df) if invoices_df is not None else 0
    )

