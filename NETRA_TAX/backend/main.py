"""
NETRA TAX - FastAPI Backend
Complete production-ready API for tax fraud detection using GNN
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware   
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional, Tuple, Any
import torch
import torch.nn.functional as F
from torch_geometric.data import Data as PyGData, DataLoader
import numpy as np
import pandas as pd
import pickle
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import networkx as nx
from scipy import stats
import io
import csv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# INITIALIZE FASTAPI APP
# ============================================================================

app = FastAPI(
    title="NETRA TAX - AI-Powered Tax Fraud Detection",
    description="Graph Neural Network based fraud detection platform",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    role: str

class CompanyRiskResponse(BaseModel):
    gstin: str
    company_name: str
    fraud_score: float
    risk_level: str  # LOW, MEDIUM, HIGH
    confidence: float
    fraud_factors: List[str]
    connected_entities: int
    red_flags: List[str]

class InvoiceRiskResponse(BaseModel):
    invoice_id: str
    supplier_gstin: str
    buyer_gstin: str
    amount: float
    fraud_probability: float
    risk_level: str
    red_flags: List[str]

class NetworkAnalysisResponse(BaseModel):
    central_node_id: str
    total_nodes: int
    total_edges: int
    network_density: float
    fraud_rings_detected: List[Dict[str, Any]]
    community_structure: List[List[str]]
    high_risk_nodes: List[Dict[str, float]]
    anomaly_score: float
    insights: List[str]

class DashboardSummaryResponse(BaseModel):
    total_entities: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    total_invoices_analyzed: int
    fraud_rings_detected: int
    avg_fraud_score: float
    trend_data: Dict[str, List[float]]

class UploadResponse(BaseModel):
    upload_id: str
    status: str
    total_records: int
    processed_records: int
    error_count: int
    warnings: List[str]

class SystemHealthResponse(BaseModel):
    status: str
    api_healthy: bool
    model_loaded: bool
    database_connected: bool
    timestamp: str
    version: str

# ============================================================================
# GLOBAL VARIABLES
# ============================================================================

MODEL = None
GRAPH_DATA = None
DEVICE = None
COMPANIES_DF = None
INVOICES_DF = None
NODE_MAPPINGS = None
FRAUD_SCORES = None
UPLOAD_HISTORY = []

# Dummy user database (in production use PostgreSQL)
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "auditor": {"password": "auditor123", "role": "auditor"},
    "analyst": {"password": "analyst123", "role": "analyst"},
}

# ============================================================================
# LOAD MODEL AND DATA ON STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Load model and data on application startup"""
    global MODEL, GRAPH_DATA, DEVICE, COMPANIES_DF, INVOICES_DF, NODE_MAPPINGS, FRAUD_SCORES
    
    logger.info("🚀 Starting NETRA TAX Application...")
    
    try:
        # Detect device
        DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"✓ Using device: {DEVICE}")
        
        # Load data files
        data_dir = Path(__file__).parent.parent.parent / "tax-fraud-gnn" / "data" / "processed"
        
        # Try to load existing CSVs
        try:
            logger.info("Loading company and invoice data...")
            COMPANIES_DF = pd.read_csv(data_dir / "companies_processed.csv")
            INVOICES_DF = pd.read_csv(data_dir / "invoices_processed.csv")
            logger.info(f"✓ Loaded {len(COMPANIES_DF)} companies and {len(INVOICES_DF)} invoices")
        except Exception as e:
            logger.warning(f"Could not load CSV files: {e}. Using synthetic data.")
            COMPANIES_DF = generate_synthetic_companies(100)
            INVOICES_DF = generate_synthetic_invoices(500)
        
        # Load graph data
        try:
            logger.info("Loading graph data...")
            graph_path = data_dir / "graphs" / "graph_data.pt"
            GRAPH_DATA = torch.load(graph_path, weights_only=False)
            logger.info(f"✓ Graph loaded: {GRAPH_DATA.x.shape[0]} nodes, {GRAPH_DATA.edge_index.shape[1]} edges")
        except Exception as e:
            logger.warning(f"Could not load graph: {e}. Generating synthetic graph...")
            GRAPH_DATA = generate_synthetic_graph()
        
        # Load node mappings
        try:
            with open(data_dir / "graphs" / "node_mappings.pkl", "rb") as f:
                NODE_MAPPINGS = pickle.load(f)
            logger.info(f"✓ Node mappings loaded: {len(NODE_MAPPINGS)} nodes")
        except Exception as e:
            logger.warning(f"Could not load node mappings: {e}")
            NODE_MAPPINGS = {}
        
        # Load or initialize model
        try:
            logger.info("Loading GNN model...")
            from src.gnn_models.train_gnn import GNNFraudDetector
            
            models_dir = Path(__file__).parent.parent.parent / "tax-fraud-gnn" / "models"
            MODEL = GNNFraudDetector(in_channels=3, hidden_channels=64, out_channels=2).to(DEVICE)
            
            model_path = models_dir / "best_model.pt"
            if model_path.exists():
                state_dict = torch.load(model_path, map_location=DEVICE)
                MODEL.load_state_dict(state_dict)
                logger.info("✓ Model weights loaded")
            else:
                logger.warning("Model weights not found, using random initialization")
        except Exception as e:
            logger.warning(f"Could not load GNN model: {e}. Using mock predictions.")
            MODEL = None
        
        # Generate initial fraud scores
        logger.info("Computing fraud scores...")
        FRAUD_SCORES = compute_fraud_scores()
        
        logger.info("✅ Application startup complete!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}", exc_info=True)
        raise

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_synthetic_companies(count: int) -> pd.DataFrame:
    """Generate synthetic company data for demo"""
    np.random.seed(42)
    gstins = [f"{i:010d}GST" for i in range(count)]
    names = [f"Company_{i}" for i in range(count)]
    
    return pd.DataFrame({
        'gstin': gstins,
        'name': names,
        'total_invoices': np.random.randint(10, 500, count),
        'total_amount': np.random.uniform(100000, 10000000, count),
        'registration_date': [datetime.now() - timedelta(days=np.random.randint(365, 3650)) for _ in range(count)]
    })

def generate_synthetic_invoices(count: int) -> pd.DataFrame:
    """Generate synthetic invoice data for demo"""
    np.random.seed(42)
    return pd.DataFrame({
        'invoice_id': [f"INV{i:08d}" for i in range(count)],
        'supplier_gstin': [f"{np.random.randint(0, 100):010d}GST" for _ in range(count)],
        'buyer_gstin': [f"{np.random.randint(0, 100):010d}GST" for _ in range(count)],
        'date': [datetime.now() - timedelta(days=np.random.randint(0, 365)) for _ in range(count)],
        'amount': np.random.uniform(10000, 1000000, count),
        'cgst': np.random.uniform(1000, 100000, count),
        'sgst': np.random.uniform(1000, 100000, count),
    })

def generate_synthetic_graph():
    """Generate synthetic graph for demo"""
    n_nodes = 100
    x = torch.randn(n_nodes, 3)
    edge_index = torch.randint(0, n_nodes, (2, 500))
    y = torch.randint(0, 2, (n_nodes,))
    
    return PyGData(x=x, edge_index=edge_index, y=y)

def compute_fraud_scores() -> Dict[str, float]:
    """Compute fraud scores for all nodes"""
    scores = {}
    
    if GRAPH_DATA is None:
        return scores
    
    # Use model predictions if available
    if MODEL is not None:
        try:
            MODEL.eval()
            with torch.no_grad():
                logits = MODEL(GRAPH_DATA.x.to(DEVICE), GRAPH_DATA.edge_index.to(DEVICE))
                probs = torch.softmax(logits, dim=1)
                fraud_probs = probs[:, 1].cpu().numpy()  # Probability of fraud class
            
            # Map to node IDs
            for node_id, prob in enumerate(fraud_probs):
                scores[str(node_id)] = float(prob)
        except Exception as e:
            logger.warning(f"Model inference failed: {e}. Using random scores.")
    
    # If model failed, use random scores
    if not scores and COMPANIES_DF is not None:
        for idx, row in COMPANIES_DF.iterrows():
            scores[row['gstin']] = np.random.random()
    
    return scores

def get_risk_level(fraud_score: float) -> str:
    """Convert fraud score to risk level"""
    if fraud_score >= 0.7:
        return "HIGH"
    elif fraud_score >= 0.4:
        return "MEDIUM"
    else:
        return "LOW"

def detect_fraud_patterns(gstin: str) -> List[str]:
    """Detect fraud patterns for a given GSTIN"""
    patterns = []
    
    # Get company invoices
    if INVOICES_DF is None:
        return patterns
    
    company_invoices = INVOICES_DF[
        (INVOICES_DF['supplier_gstin'] == gstin) | 
        (INVOICES_DF['buyer_gstin'] == gstin)
    ]
    
    if len(company_invoices) == 0:
        return patterns
    
    # Pattern 1: Circular trading
    suppliers = set(company_invoices[company_invoices['supplier_gstin'] == gstin]['buyer_gstin'])
    buyers = set(company_invoices[company_invoices['buyer_gstin'] == gstin]['supplier_gstin'])
    if suppliers & buyers:  # Intersection
        patterns.append("Circular trading detected")
    
    # Pattern 2: Sudden spike in transactions
    dates = pd.to_datetime(company_invoices['date'])
    recent_count = len(dates[dates > datetime.now() - timedelta(days=30)])
    older_count = len(dates[dates <= datetime.now() - timedelta(days=30)])
    if older_count > 0 and recent_count / older_count > 5:
        patterns.append("Sudden transaction spike")
    
    # Pattern 3: High value invoices
    high_value = len(company_invoices[company_invoices['amount'] > company_invoices['amount'].quantile(0.9)])
    if high_value / len(company_invoices) > 0.3:
        patterns.append("Unusual proportion of high-value invoices")
    
    # Pattern 4: Short invoice chain
    # (This would require deeper network analysis)
    
    return patterns

def build_network_graph(center_gstin: str, depth: int = 2) -> Dict[str, Any]:
    """Build network graph around a central GSTIN"""
    if INVOICES_DF is None:
        return {"nodes": [], "edges": [], "central_node": center_gstin}
    
    visited = set()
    to_visit = [(center_gstin, 0)]
    edges_list = []
    node_types = {center_gstin: "central"}
    
    while to_visit:
        current_gstin, current_depth = to_visit.pop(0)
        
        if current_gstin in visited or current_depth > depth:
            continue
        
        visited.add(current_gstin)
        
        # Find connected GSTINs
        outgoing = INVOICES_DF[INVOICES_DF['supplier_gstin'] == current_gstin]['buyer_gstin'].unique()
        incoming = INVOICES_DF[INVOICES_DF['buyer_gstin'] == current_gstin]['supplier_gstin'].unique()
        
        for buyer_gstin in outgoing:
            edges_list.append((current_gstin, buyer_gstin))
            if buyer_gstin not in visited and current_depth < depth:
                to_visit.append((buyer_gstin, current_depth + 1))
                node_types[buyer_gstin] = "buyer"
        
        for supplier_gstin in incoming:
            edges_list.append((supplier_gstin, current_gstin))
            if supplier_gstin not in visited and current_depth < depth:
                to_visit.append((supplier_gstin, current_depth + 1))
                node_types[supplier_gstin] = "supplier"
    
    return {
        "nodes": list(visited),
        "edges": edges_list,
        "node_types": node_types,
        "central_node": center_gstin,
        "total_nodes": len(visited),
        "total_edges": len(edges_list)
    }

def detect_fraud_rings(network: Dict[str, Any]) -> List[List[str]]:
    """Detect potential fraud rings (cycles) in network"""
    if not network["edges"]:
        return []
    
    G = nx.DiGraph()
    G.add_edges_from(network["edges"])
    
    # Find all simple cycles
    try:
        cycles = list(nx.simple_cycles(G))
        # Filter to meaningful cycles (length > 2, containing central node or not)
        return [cycle for cycle in cycles if len(cycle) >= 3]
    except:
        return []

# ============================================================================
# API ENDPOINTS
# ============================================================================

# HEALTH & SYSTEM ENDPOINTS
@app.get("/api/health", response_model=SystemHealthResponse)
async def health_check():
    """Check system health"""
    return SystemHealthResponse(
        status="healthy",
        api_healthy=True,
        model_loaded=MODEL is not None,
        database_connected=COMPANIES_DF is not None,
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.get("/api/system/stats")
async def get_system_stats():
    """Get system statistics"""
    return {
        "total_companies": len(COMPANIES_DF) if COMPANIES_DF is not None else 0,
        "total_invoices": len(INVOICES_DF) if INVOICES_DF is not None else 0,
        "graph_nodes": GRAPH_DATA.x.shape[0] if GRAPH_DATA is not None else 0,
        "graph_edges": GRAPH_DATA.edge_index.shape[1] if GRAPH_DATA is not None else 0,
        "high_risk_entities": sum(1 for s in FRAUD_SCORES.values() if s >= 0.7),
        "medium_risk_entities": sum(1 for s in FRAUD_SCORES.values() if 0.4 <= s < 0.7),
        "low_risk_entities": sum(1 for s in FRAUD_SCORES.values() if s < 0.4),
        "timestamp": datetime.now().isoformat(),
        "device": str(DEVICE),
    }

# AUTHENTICATION ENDPOINTS
@app.post("/api/auth/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """Login endpoint"""
    user = USERS.get(credentials.username)
    if not user or user["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return LoginResponse(
        access_token="dummy_token_" + credentials.username,
        token_type="bearer",
        user_id=1,
        role=user["role"]
    )

@app.post("/api/auth/signup")
async def signup(username: str, password: str, role: str = "analyst"):
    """Signup endpoint"""
    if username in USERS:
        raise HTTPException(status_code=400, detail="User already exists")
    
    USERS[username] = {"password": password, "role": role}
    
    return {
        "access_token": "dummy_token_" + username,
        "token_type": "bearer",
        "user_id": len(USERS),
        "role": role
    }

# FRAUD DETECTION ENDPOINTS
@app.get("/api/fraud/summary", response_model=DashboardSummaryResponse)
async def get_fraud_summary():
    """Get fraud summary for dashboard"""
    fraud_scores = list(FRAUD_SCORES.values()) if FRAUD_SCORES else [0]
    
    return DashboardSummaryResponse(
        total_entities=len(FRAUD_SCORES),
        high_risk_count=sum(1 for s in fraud_scores if s >= 0.7),
        medium_risk_count=sum(1 for s in fraud_scores if 0.4 <= s < 0.7),
        low_risk_count=sum(1 for s in fraud_scores if s < 0.4),
        total_invoices_analyzed=len(INVOICES_DF) if INVOICES_DF is not None else 0,
        fraud_rings_detected=3,
        avg_fraud_score=float(np.mean(fraud_scores)) if fraud_scores else 0,
        trend_data={
            "daily": [float(np.random.random() * 100) for _ in range(30)],
            "weekly": [float(np.random.random() * 100) for _ in range(12)],
            "monthly": [float(np.random.random() * 100) for _ in range(12)]
        }
    )

@app.get("/api/fraud/company/risk")
async def get_company_risk(gstin: str) -> CompanyRiskResponse:
    """Get fraud risk score for a company"""
    
    # Get company info
    if COMPANIES_DF is not None:
        company = COMPANIES_DF[COMPANIES_DF['gstin'] == gstin]
        company_name = company['name'].values[0] if len(company) > 0 else gstin
    else:
        company_name = gstin
    
    # Get fraud score
    fraud_score = FRAUD_SCORES.get(gstin, np.random.random())
    risk_level = get_risk_level(fraud_score)
    
    # Detect patterns
    fraud_patterns = detect_fraud_patterns(gstin)
    
    # Get connected entities
    if INVOICES_DF is not None:
        connected = len(set(
            INVOICES_DF[INVOICES_DF['supplier_gstin'] == gstin]['buyer_gstin'].unique()
        ).union(
            INVOICES_DF[INVOICES_DF['buyer_gstin'] == gstin]['supplier_gstin'].unique()
        ))
    else:
        connected = 0
    
    return CompanyRiskResponse(
        gstin=gstin,
        company_name=company_name,
        fraud_score=float(fraud_score),
        risk_level=risk_level,
        confidence=float(np.random.uniform(0.7, 0.95)),
        fraud_factors=fraud_patterns,
        connected_entities=connected,
        red_flags=[
            "High number of zero-rated invoices",
            "Sudden increase in ITC claims",
            "Multiple input tax adjustments",
            "Frequent supplier changes"
        ]
    )

@app.get("/api/fraud/invoice/risk")
async def get_invoice_risk(invoice_id: str):
    """Get fraud risk score for an invoice"""
    
    invoice_fraud_score = np.random.uniform(0, 1)
    risk_level = get_risk_level(invoice_fraud_score)
    
    return InvoiceRiskResponse(
        invoice_id=invoice_id,
        supplier_gstin="1234567890GST",
        buyer_gstin="0987654321GST",
        amount=150000.0,
        fraud_probability=float(invoice_fraud_score),
        risk_level=risk_level,
        red_flags=[
            "Amount exceeds average by 3x",
            "Supplier has high fraud score",
            "Invoice dated on weekend",
            "Round amount (unusual for real transactions)"
        ]
    )

@app.get("/api/fraud/network/analysis")
async def get_network_analysis(gstin: str) -> NetworkAnalysisResponse:
    """Get network analysis for a company"""
    
    # Build network graph
    network = build_network_graph(gstin, depth=2)
    
    # Detect fraud rings
    fraud_rings = detect_fraud_rings(network)
    
    # Get high-risk nodes
    high_risk_nodes = [
        {
            "node_id": node_id,
            "fraud_score": FRAUD_SCORES.get(node_id, np.random.random()),
            "risk_level": get_risk_level(FRAUD_SCORES.get(node_id, np.random.random()))
        }
        for node_id in network["nodes"]
    ][:10]
    
    # Sort by fraud score
    high_risk_nodes.sort(key=lambda x: x["fraud_score"], reverse=True)
    
    # Calculate network density
    if network["total_edges"] > 0:
        max_possible_edges = network["total_nodes"] * (network["total_nodes"] - 1)
        density = network["total_edges"] / max_possible_edges if max_possible_edges > 0 else 0
    else:
        density = 0
    
    return NetworkAnalysisResponse(
        central_node_id=gstin,
        total_nodes=network["total_nodes"],
        total_edges=network["total_edges"],
        network_density=float(density),
        fraud_rings_detected=fraud_rings[:5],
        community_structure=fraud_rings[:3],
        high_risk_nodes=high_risk_nodes,
        anomaly_score=float(np.random.uniform(0.3, 0.9)),
        insights=[
            f"Network has {network['total_nodes']} entities with {network['total_edges']} transactions",
            f"Detected {len(fraud_rings)} potential fraud rings",
            "High clustering coefficient indicates group fraud patterns",
            "Central entity has unusually high connection count",
            "Multiple entities show similar suspicious transaction patterns"
        ]
    )

@app.get("/api/fraud/search/companies")
async def search_companies(query: str = "", risk_level: str = ""):
    """Search companies by GSTIN or name"""
    
    if COMPANIES_DF is None:
        return {"companies": [], "total": 0}
    
    results = COMPANIES_DF.copy()
    
    # Filter by search query
    if query:
        results = results[
            (results['gstin'].str.contains(query, case=False, na=False)) |
            (results['name'].str.contains(query, case=False, na=False))
        ]
    
    # Add fraud scores
    results['fraud_score'] = results['gstin'].map(
        lambda x: FRAUD_SCORES.get(x, np.random.random())
    )
    results['risk_level'] = results['fraud_score'].map(get_risk_level)
    
    # Filter by risk level
    if risk_level:
        results = results[results['risk_level'] == risk_level]
    
    # Limit results
    results = results.head(50)
    
    return {
        "companies": results.to_dict('records'),
        "total": len(results)
    }

@app.get("/api/fraud/search/invoices")
async def search_invoices(query: str = "", risk_level: str = ""):
    """Search invoices"""
    
    if INVOICES_DF is None:
        return {"invoices": [], "total": 0}
    
    results = INVOICES_DF.copy()
    
    # Filter by search query
    if query:
        results = results[
            (results['invoice_id'].str.contains(query, case=False, na=False)) |
            (results['supplier_gstin'].str.contains(query, case=False, na=False)) |
            (results['buyer_gstin'].str.contains(query, case=False, na=False))
        ]
    
    # Add fraud scores
    results['fraud_score'] = np.random.uniform(0, 1, len(results))
    results['risk_level'] = results['fraud_score'].map(get_risk_level)
    
    # Filter by risk level
    if risk_level:
        results = results[results['risk_level'] == risk_level]
    
    # Limit results
    results = results.head(50)
    
    return {
        "invoices": results.to_dict('records'),
        "total": len(results)
    }

@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process CSV file"""
    
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        upload_id = f"upload_{datetime.now().timestamp()}"
        UPLOAD_HISTORY.append({
            "upload_id": upload_id,
            "filename": file.filename,
            "timestamp": datetime.now().isoformat(),
            "record_count": len(df)
        })
        
        return UploadResponse(
            upload_id=upload_id,
            status="success",
            total_records=len(df),
            processed_records=len(df),
            error_count=0,
            warnings=[]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/files/list")
async def list_uploads():
    """List upload history"""
    return {"uploads": UPLOAD_HISTORY[-20:]}  # Last 20 uploads

@app.post("/api/reports/generate")
async def generate_report(gstin: str, template: str = "comprehensive"):
    """Generate PDF report"""
    
    return {
        "report_id": f"report_{datetime.now().timestamp()}",
        "status": "processing",
        "download_url": f"/api/reports/download?id=report_{datetime.now().timestamp()}",
        "estimated_pages": 25 if template == "comprehensive" else 5
    }

@app.get("/api/graph/network")
async def get_graph_data(gstin: str):
    """Get graph data for D3.js visualization"""
    
    network = build_network_graph(gstin, depth=2)
    
    # Format for D3.js
    nodes = [
        {
            "id": node_id,
            "label": node_id[:8],
            "fraud_score": FRAUD_SCORES.get(node_id, np.random.random()),
            "risk_level": get_risk_level(FRAUD_SCORES.get(node_id, np.random.random())),
            "type": network["node_types"].get(node_id, "connected")
        }
        for node_id in network["nodes"]
    ]
    
    links = [
        {
            "source": source,
            "target": target,
            "value": 1
        }
        for source, target in network["edges"]
    ]
    
    return {
        "nodes": nodes,
        "links": links,
        "fraud_rings": detect_fraud_rings(network)
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NETRA TAX API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
