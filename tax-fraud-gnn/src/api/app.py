"""
Flask API for Tax Fraud Detection
REST endpoints for model serving
"""

from flask import Flask, request, jsonify
import torch
import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from gnn_models.train_gnn import GNNFraudDetector

app = Flask(__name__)

# Global variables for model and data
MODEL = None
GRAPH_DATA = None
DEVICE = None
COMPANIES = None
MAPPINGS = None


def load_model_and_data():
    """Load model and data on startup"""
    global MODEL, GRAPH_DATA, DEVICE, COMPANIES, MAPPINGS
    
    data_path = Path(__file__).parent.parent / "data" / "processed"
    models_path = Path(__file__).parent.parent / "models"
    
    logger.info("Loading data...")
    COMPANIES = pd.read_csv(data_path / "companies_processed.csv")
    
    logger.info("Loading graph...")
    GRAPH_DATA = torch.load(data_path / "graphs" / "graph_data.pt")
    
    logger.info("Loading model...")
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    MODEL = GNNFraudDetector(in_channels=3, hidden_channels=64, out_channels=2, model_type="gcn").to(DEVICE)
    
    try:
        MODEL.load_state_dict(torch.load(models_path / "best_model.pt", map_location=DEVICE))
        logger.info("Model weights loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load model weights: {e}")
    
    with open(data_path / "graphs" / "node_mappings.pkl", "rb") as f:
        MAPPINGS = pickle.load(f)
    
    logger.info("Model and data loaded successfully!")


@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Tax Fraud Detection API is running",
        "version": "1.0"
    })


@app.route("/api/predict", methods=["POST"])
def predict():
    """
    Predict fraud probability for a company
    Request body: {"company_id": int}
    """
    try:
        data = request.get_json()
        company_id = data.get("company_id")
        
        if not company_id:
            return jsonify({"error": "company_id is required"}), 400
        
        # Find company in graph
        node_list = MAPPINGS["node_list"]
        if company_id not in node_list:
            return jsonify({"error": f"Company ID {company_id} not found"}), 404
        
        # Get prediction
        MODEL.eval()
        with torch.no_grad():
            out = MODEL(GRAPH_DATA.x.to(DEVICE), GRAPH_DATA.edge_index.to(DEVICE))
            predictions = torch.softmax(out, dim=1)
        
        node_idx = node_list.index(company_id)
        fraud_proba = float(predictions[node_idx, 1].cpu().numpy())
        
        # Get company details
        company_row = COMPANIES[COMPANIES["company_id"] == company_id].iloc[0]
        
        return jsonify({
            "company_id": company_id,
            "fraud_probability": fraud_proba,
            "is_fraud": float(fraud_proba > 0.5),
            "risk_level": "HIGH" if fraud_proba > 0.7 else "MEDIUM" if fraud_proba > 0.3 else "LOW",
            "location": company_row["location"],
            "turnover": float(company_row["turnover"])
        })
    
    except Exception as e:
        logger.error(f"Error in predict: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/batch_predict", methods=["POST"])
def batch_predict():
    """
    Batch predict fraud probabilities
    Request body: {"company_ids": [int, ...]}
    """
    try:
        data = request.get_json()
        company_ids = data.get("company_ids", [])
        
        if not company_ids:
            return jsonify({"error": "company_ids list is required"}), 400
        
        node_list = MAPPINGS["node_list"]
        
        # Get predictions for all nodes
        MODEL.eval()
        with torch.no_grad():
            out = MODEL(GRAPH_DATA.x.to(DEVICE), GRAPH_DATA.edge_index.to(DEVICE))
            predictions = torch.softmax(out, dim=1)
        
        results = []
        for company_id in company_ids:
            if company_id not in node_list:
                results.append({
                    "company_id": company_id,
                    "error": "Company not found"
                })
            else:
                node_idx = node_list.index(company_id)
                fraud_proba = float(predictions[node_idx, 1].cpu().numpy())
                company_row = COMPANIES[COMPANIES["company_id"] == company_id].iloc[0]
                
                results.append({
                    "company_id": company_id,
                    "fraud_probability": fraud_proba,
                    "is_fraud": float(fraud_proba > 0.5),
                    "risk_level": "HIGH" if fraud_proba > 0.7 else "MEDIUM" if fraud_proba > 0.3 else "LOW"
                })
        
        return jsonify({"predictions": results})
    
    except Exception as e:
        logger.error(f"Error in batch_predict: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/company/<int:company_id>", methods=["GET"])
def get_company(company_id):
    """Get company details"""
    try:
        company = COMPANIES[COMPANIES["company_id"] == company_id]
        if len(company) == 0:
            return jsonify({"error": f"Company {company_id} not found"}), 404
        
        row = company.iloc[0]
        return jsonify({
            "company_id": company_id,
            "location": row["location"],
            "turnover": float(row["turnover"]),
            "sent_invoice_count": int(row["sent_invoice_count"]),
            "received_invoice_count": int(row["received_invoice_count"]),
            "total_transaction_volume": float(row["total_transaction_volume"])
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get overall statistics"""
    try:
        # Get predictions
        MODEL.eval()
        with torch.no_grad():
            out = MODEL(GRAPH_DATA.x.to(DEVICE), GRAPH_DATA.edge_index.to(DEVICE))
            predictions = torch.softmax(out, dim=1)
            fraud_probas = predictions[:, 1].cpu().numpy()
        
        return jsonify({
            "total_companies": len(COMPANIES),
            "total_edges": GRAPH_DATA.num_edges,
            "average_fraud_probability": float(np.mean(fraud_probas)),
            "high_risk_count": int((fraud_probas > 0.7).sum()),
            "medium_risk_count": int(((fraud_probas > 0.3) & (fraud_probas <= 0.7)).sum()),
            "low_risk_count": int((fraud_probas <= 0.3).sum())
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    load_model_and_data()
    app.run(debug=True, host="0.0.0.0", port=5000)
