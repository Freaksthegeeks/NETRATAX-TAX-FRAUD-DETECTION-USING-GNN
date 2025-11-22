"""
NETRA TAX - AI-Powered Tax Fraud Detection Platform
Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.routers import auth, fraud, files, system
import torch

# Setup logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE) if settings.LOG_FILE else logging.NullHandler(),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# Lifespan Events
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize directories
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.TEMP_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.REPORT_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.MODEL_DIR).mkdir(parents=True, exist_ok=True)
    
    logger.info("Directories initialized")
    
    # Load model and data (if available)
    try:
        if Path(settings.MODEL_PATH).exists():
            logger.info(f"Loading model from {settings.MODEL_PATH}")
            model = torch.load(settings.MODEL_PATH, map_location=settings.DEVICE)
            logger.info("Model loaded successfully")
        else:
            logger.warning(f"Model file not found at {settings.MODEL_PATH}")
        
        if Path(settings.GRAPH_DATA_PATH).exists():
            logger.info(f"Loading graph data from {settings.GRAPH_DATA_PATH}")
            graph_data = torch.load(settings.GRAPH_DATA_PATH, map_location=settings.DEVICE)
            logger.info("Graph data loaded successfully")
        else:
            logger.warning(f"Graph data not found at {settings.GRAPH_DATA_PATH}")
    
    except Exception as e:
        logger.error(f"Error loading model/data: {e}")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")


# ============================================================================
# Create FastAPI Application
# ============================================================================

app = FastAPI(
    title=settings.API_TITLE,
    description="AI-Powered Tax Fraud Detection using Graph Neural Networks",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)


# ============================================================================
# Middleware
# ============================================================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "192.168.*"]
)


# ============================================================================
# Route Registration
# ============================================================================

# Include routers
app.include_router(auth.router)
app.include_router(fraud.router)
app.include_router(files.router)
app.include_router(system.router)


# ============================================================================
# Static Files
# ============================================================================

# Serve static files (if frontend is built)
static_dir = Path(__file__).parent.parent / "frontend" / "dist"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir), html=True), name="static")
    logger.info(f"Static files mounted from {static_dir}")


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/docs",
        "redoc": "/api/redoc"
    }


@app.get("/api/v1")
async def api_root():
    """API v1 root"""
    return {
        "api_version": "1.0.0",
        "endpoints": {
            "auth": "/api/v1/auth",
            "fraud": "/api/v1/fraud",
            "files": "/api/v1/files",
            "system": "/api/v1/system"
        }
    }


# ============================================================================
# Error Handlers
# ============================================================================

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# ============================================================================
# Application Factory
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
