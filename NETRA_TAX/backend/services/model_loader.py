"""
Model and Data Loader Service
Loads GNN model and graph data for inference
"""

import torch
import pandas as pd
import pickle
from pathlib import Path
import logging
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tax-fraud-gnn" / "src"))

from gnn_models.train_gnn import GNNFraudDetector

logger = logging.getLogger(__name__)

# Global variables
MODEL = None
GRAPH_DATA = None
DEVICE = None
COMPANIES_DF = None
INVOICES_DF = None
MAPPINGS = None
FRAUD_PROBA = None

def load_model_and_data():
    """Load model and data on startup"""
    global MODEL, GRAPH_DATA, DEVICE, COMPANIES_DF, INVOICES_DF, MAPPINGS, FRAUD_PROBA
    
    # Paths - try both locations
    base_path = Path(__file__).parent.parent.parent
    data_paths = [
        base_path / "tax-fraud-gnn" / "data" / "processed",
        base_path / "ai"
    ]
    
    models_paths = [
        base_path / "tax-fraud-gnn" / "models",
        base_path / "ai"
    ]
    
    data_path = None
    models_path = None
    
    for path in data_paths:
        if path.exists():
            data_path = path
            break
    
    for path in models_paths:
        if path.exists():
            models_path = path
            break
    
    if not data_path or not models_path:
        raise FileNotFoundError("Could not find data or models directory")
    
    logger.info(f"Loading data from: {data_path}")
    logger.info(f"Loading models from: {models_path}")
    
    # Load CSV data
    try:
        COMPANIES_DF = pd.read_csv(data_path / "companies_processed.csv")
        INVOICES_DF = pd.read_csv(data_path / "invoices_processed.csv")
        logger.info(f"Loaded {len(COMPANIES_DF)} companies and {len(INVOICES_DF)} invoices")
    except Exception as e:
        logger.warning(f"Could not load CSV files: {e}")
        COMPANIES_DF = pd.DataFrame()
        INVOICES_DF = pd.DataFrame()
    
    # Load graph data
    logger.info("Loading graph data...")
    graph_file = data_path / "graphs" / "graph_data.pt"
    if not graph_file.exists():
        graph_file = base_path / "graph_data.pt"
    
    try:
        GRAPH_DATA = torch.load(graph_file, weights_only=False)
        logger.info(f"Loaded graph: {GRAPH_DATA.num_nodes} nodes, {GRAPH_DATA.num_edges} edges")
    except Exception as e:
        logger.warning(f"Could not load graph with weights_only=False: {e}")
        try:
            from torch_geometric.data import Data as PyGData
            import torch.serialization
            torch.serialization.add_safe_globals([PyGData])
            GRAPH_DATA = torch.load(graph_file, weights_only=False)
        except Exception as e2:
            logger.error(f"Failed to load graph: {e2}")
            try:
                GRAPH_DATA = torch.load(graph_file)
            except Exception as e3:
                logger.error(f"Failed to load graph with all methods: {e3}")
                raise
    
    # Load model
    logger.info("Loading model...")
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {DEVICE}")
    
    model_file = models_path / "best_model.pt"
    if not model_file.exists():
        model_file = models_path / "model.pt"
    
    # Get model dimensions from graph
    in_channels = GRAPH_DATA.x.shape[1] if GRAPH_DATA.x is not None else 3
    MODEL = GNNFraudDetector(
        in_channels=in_channels,
        hidden_channels=64,
        out_channels=2,
        model_type="gcn"
    ).to(DEVICE)
    
    try:
        MODEL.load_state_dict(torch.load(model_file, map_location=DEVICE))
        logger.info("Model weights loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load model weights: {e}. Using untrained model.")
    
    # Load node mappings
    try:
        mappings_file = data_path / "graphs" / "node_mappings.pkl"
        if mappings_file.exists():
            with open(mappings_file, "rb") as f:
                MAPPINGS = pickle.load(f)
        else:
            MAPPINGS = {"node_list": list(range(GRAPH_DATA.num_nodes))}
        logger.info(f"Loaded node mappings: {len(MAPPINGS.get('node_list', []))} nodes")
    except Exception as e:
        logger.warning(f"Could not load mappings: {e}")
        MAPPINGS = {"node_list": list(range(GRAPH_DATA.num_nodes))}
    
    # Get fraud predictions
    MODEL.eval()
    with torch.no_grad():
        out = MODEL(GRAPH_DATA.x.to(DEVICE), GRAPH_DATA.edge_index.to(DEVICE))
        predictions = torch.softmax(out, dim=1)
        FRAUD_PROBA = predictions[:, 1].cpu().numpy()
    
    if COMPANIES_DF is not None and len(COMPANIES_DF) > 0:
        # Add fraud probability to companies dataframe
        if len(FRAUD_PROBA) == len(COMPANIES_DF):
            COMPANIES_DF["fraud_probability"] = FRAUD_PROBA
            COMPANIES_DF["predicted_fraud"] = (FRAUD_PROBA > 0.5).astype(int)
    
    logger.info("✅ Model and data loaded successfully!")
    logger.info(f"   - Nodes: {GRAPH_DATA.num_nodes}")
    logger.info(f"   - Edges: {GRAPH_DATA.num_edges}")
    logger.info(f"   - Companies: {len(COMPANIES_DF) if COMPANIES_DF is not None else 0}")
    logger.info(f"   - Average fraud probability: {FRAUD_PROBA.mean():.4f}")

def get_model():
    """Get loaded model"""
    return MODEL

def get_graph_data():
    """Get loaded graph data"""
    return GRAPH_DATA

def get_companies_df():
    """Get companies dataframe"""
    return COMPANIES_DF

def get_invoices_df():
    """Get invoices dataframe"""
    return INVOICES_DF

def get_mappings():
    """Get node mappings"""
    return MAPPINGS

def get_fraud_proba():
    """Get fraud probabilities"""
    return FRAUD_PROBA

def get_device():
    """Get device"""
    return DEVICE

