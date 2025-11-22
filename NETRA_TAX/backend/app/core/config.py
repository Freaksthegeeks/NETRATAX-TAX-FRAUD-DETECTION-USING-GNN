"""
Core Configuration Module for NETRA TAX
Centralized config for API, security, database, and AI models
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from datetime import timedelta
import os


class Settings(BaseSettings):
    """Application Settings"""
    
    # ============================================================================
    # API Configuration
    # ============================================================================
    APP_NAME: str = "NETRA TAX - AI-Powered Tax Fraud Detection"
    APP_VERSION: str = "1.0.0"
    API_TITLE: str = "NETRA TAX API"
    API_PREFIX: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = DEBUG
    
    # ============================================================================
    # Security & Authentication
    # ============================================================================
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-12345678")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # JWT Configuration
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000",
        "http://192.168.29.114:3000",
        "http://192.168.29.114:5000",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # ============================================================================
    # Database Configuration
    # ============================================================================
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:password@localhost/netra_tax"
    )
    SQLALCHEMY_ECHO: bool = False
    
    # File Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    TEMP_DIR: str = os.getenv("TEMP_DIR", "./temp")
    REPORT_DIR: str = os.getenv("REPORT_DIR", "./reports")
    MODEL_DIR: str = os.getenv("MODEL_DIR", "./models")
    
    # ============================================================================
    # AI/ML Configuration
    # ============================================================================
    GRAPH_DATA_PATH: str = os.getenv("GRAPH_DATA_PATH", "../data/graph_data.pt")
    MODEL_PATH: str = os.getenv("MODEL_PATH", "../models/gnn_model.pt")
    DEVICE: str = "cuda" if os.getenv("USE_CUDA", "true").lower() == "true" else "cpu"
    
    # GNN Model Parameters
    HIDDEN_CHANNELS: int = 64
    NUM_LAYERS: int = 3
    DROPOUT: float = 0.5
    LEARNING_RATE: float = 0.001
    
    # Fraud Detection Thresholds
    HIGH_RISK_THRESHOLD: float = 0.7
    MEDIUM_RISK_THRESHOLD: float = 0.3
    LOW_RISK_THRESHOLD: float = 0.0
    
    # ============================================================================
    # Feature Configuration
    # ============================================================================
    ENABLE_PDF_REPORTS: bool = True
    ENABLE_EMAIL_ALERTS: bool = False
    ENABLE_AUDIT_LOGS: bool = True
    ENABLE_BATCH_PROCESSING: bool = True
    
    # ============================================================================
    # Role-Based Access Control
    # ============================================================================
    USER_ROLES: dict = {
        "admin": ["read", "write", "delete", "approve", "configure"],
        "auditor": ["read", "write", "approve", "export"],
        "gst_officer": ["read", "write", "approve"],
        "analyst": ["read", "write"],
        "viewer": ["read"],
    }
    
    # ============================================================================
    # Fraud Pattern Thresholds
    # ============================================================================
    CIRCULAR_TRADE_MIN_NODES: int = 3
    HIGH_DEGREE_THRESHOLD: int = 10
    SUDDEN_SPIKE_THRESHOLD_PERCENTAGE: float = 0.5  # 50% increase
    CLUSTERING_COEFFICIENT_ANOMALY: float = 0.8
    
    # ============================================================================
    # Logging & Monitoring
    # ============================================================================
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/netra_tax.log"
    ENABLE_SENTRY: bool = os.getenv("ENABLE_SENTRY", "false").lower() == "true"
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN", None)
    
    # ============================================================================
    # Email Configuration (for alerts)
    # ============================================================================
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = 587
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    ALERT_EMAIL_FROM: str = os.getenv("ALERT_EMAIL_FROM", "alerts@netratax.com")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
