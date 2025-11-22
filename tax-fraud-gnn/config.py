"""
Configuration file for the project
"""

# Data paths
RAW_DATA_PATH = "data/raw"
PROCESSED_DATA_PATH = "data/processed"
GRAPH_DATA_PATH = "data/processed/graphs"
MODELS_PATH = "models"

# Data generation
SAMPLE_DATA_CONFIG = {
    "num_companies": 500,
    "num_invoices": 2000,
    "fraud_ratio": 0.15,  # 15% fraudulent companies
    "random_seed": 42
}

# Graph construction
GRAPH_CONFIG = {
    "min_company_id": 1,
    "max_company_id": 10000,
    "node_features": ["turnover", "sent_invoices", "received_invoices"],
    "edge_features": ["amount"]
}

# Model training
MODEL_CONFIG = {
    "model_type": "gcn",  # or "graphsage"
    "in_channels": 3,
    "hidden_channels": 64,
    "out_channels": 2,
    "epochs": 100,
    "learning_rate": 0.001,
    "weight_decay": 5e-4,
    "early_stopping_patience": 20,
    "train_ratio": 0.6,
    "val_ratio": 0.2,
    "test_ratio": 0.2,
    "batch_size": None,  # None for full-batch training
    "device": "auto"  # "cuda" or "cpu" or "auto"
}

# Dashboard config
DASHBOARD_CONFIG = {
    "theme": "light",
    "fraud_threshold": 0.5,
    "high_risk_threshold": 0.7,
    "medium_risk_threshold": 0.3
}

# API config
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": False
}

# Logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}
