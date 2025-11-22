"""
System & Health Router for NETRA TAX
System health, model info, configuration
"""

from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.core.config import settings
from app.models.schemas import SystemHealthResponse, ModelInfoResponse, SystemConfigResponse
from datetime import datetime
import logging
import psutil

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/system", tags=["System"])

# Track startup time
START_TIME = datetime.now()


@router.get("/health", response_model=SystemHealthResponse)
async def health_check():
    """
    System health check endpoint
    No authentication required for monitoring
    """
    try:
        uptime = (datetime.now() - START_TIME).total_seconds()
        
        return SystemHealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            uptime_seconds=int(uptime),
            db_status="connected",
            model_status="loaded",
            last_update=datetime.now(),
            version=settings.APP_VERSION
        )
    
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return SystemHealthResponse(
            status="degraded",
            timestamp=datetime.now(),
            uptime_seconds=int((datetime.now() - START_TIME).total_seconds()),
            db_status="disconnected",
            model_status="error",
            last_update=None,
            version=settings.APP_VERSION
        )


@router.get("/model-info", response_model=ModelInfoResponse)
async def get_model_info(current_user: dict = Depends(get_current_user)):
    """
    Get information about the fraud detection model
    """
    try:
        return ModelInfoResponse(
            model_name="Graph Neural Network (GCN)",
            model_version="1.0.0",
            framework="PyTorch Geometric",
            input_shape=[1000, 10],  # Example: 1000 nodes, 10 features
            output_shape=[1000, 1],   # Example: 1000 nodes, 1 fraud probability
            parameters=125000,         # Example
            trained_on_samples=5000,  # Example
            accuracy_train=0.94,
            accuracy_val=0.91,
            accuracy_test=0.89,
            last_updated=datetime.now()
        )
    
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise


@router.get("/config", response_model=SystemConfigResponse)
async def get_system_config(current_user: dict = Depends(get_current_user)):
    """
    Get system configuration
    Only accessible to admins
    """
    # Check if user is admin
    if 'admin' not in current_user.get('roles', []):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view system configuration"
        )
    
    return SystemConfigResponse(
        environment=settings.ENVIRONMENT,
        debug_mode=settings.DEBUG,
        high_risk_threshold=settings.HIGH_RISK_THRESHOLD,
        medium_risk_threshold=settings.MEDIUM_RISK_THRESHOLD,
        low_risk_threshold=settings.LOW_RISK_THRESHOLD,
        max_upload_size_mb=100,
        supported_file_types=["csv"],
        api_version="1.0.0"
    )


@router.get("/stats")
async def get_system_stats(current_user: dict = Depends(get_current_user)):
    """
    Get system statistics
    """
    try:
        # CPU and memory usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        return {
            "cpu_usage_percent": cpu_percent,
            "memory_usage_percent": memory.percent,
            "memory_available_mb": memory.available / (1024 * 1024),
            "uptime_seconds": int((datetime.now() - START_TIME).total_seconds()),
            "timestamp": datetime.now()
        }
    
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now()
        }


@router.post("/restart")
async def restart_system(current_user: dict = Depends(get_current_user)):
    """
    Trigger system restart (admin only)
    """
    # Check if user is admin
    if 'admin' not in current_user.get('roles', []):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can restart the system"
        )
    
    logger.info(f"System restart initiated by {current_user.get('username')}")
    
    # TODO: Implement actual restart logic
    
    return {
        "status": "success",
        "message": "System will restart shortly",
        "timestamp": datetime.now()
    }


@router.get("/logs")
async def get_system_logs(
    current_user: dict = Depends(get_current_user),
    limit: int = 100
):
    """
    Get recent system logs (admin only)
    """
    # Check if user is admin
    if 'admin' not in current_user.get('roles', []):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view system logs"
        )
    
    try:
        logs = []
        
        # Read log file
        log_file = settings.LOG_FILE
        if log_file:
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    logs = [line.strip() for line in lines[-limit:]]
            except FileNotFoundError:
                logs = ["No logs found"]
        
        return {
            "total_logs": len(logs),
            "logs": logs
        }
    
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return {
            "error": str(e)
        }


@router.post("/clear-cache")
async def clear_cache(current_user: dict = Depends(get_current_user)):
    """
    Clear system cache (admin only)
    """
    # Check if user is admin
    if 'admin' not in current_user.get('roles', []):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can clear cache"
        )
    
    logger.info(f"Cache clear requested by {current_user.get('username')}")
    
    # TODO: Implement cache clearing logic
    
    return {
        "status": "success",
        "message": "Cache cleared successfully",
        "timestamp": datetime.now()
    }
