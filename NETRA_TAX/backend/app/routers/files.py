"""
File Upload Router for NETRA TAX
CSV file handling, validation, processing
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from fastapi.responses import FileResponse
from app.core.security import get_current_user
from app.models.schemas import FileUploadResponse, BatchProcessingRequest, BatchProcessingResponse
from app.services.upload_service import CSVUploadService, GraphBuildingService
from app.core.config import settings
import logging
import os
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/files", tags=["File Upload"])

# Initialize services
upload_service = CSVUploadService(settings.UPLOAD_DIR)
graph_builder = GraphBuildingService()

# Track upload jobs
UPLOAD_JOBS = {}


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = "invoice",
    current_user: dict = Depends(get_current_user)
):
    """
    Upload and validate CSV file
    
    file_type: 'invoice' or 'company'
    """
    try:
        # Validate file
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only CSV files are supported"
            )
        
        if file.size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB}MB"
            )
        
        # Save temporary file
        temp_path = Path(settings.TEMP_DIR) / file.filename
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # Process file
        upload_result = upload_service.upload_and_validate(
            str(temp_path),
            file_type
        )
        
        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass
        
        logger.info(f"User {current_user.get('username')} uploaded {file.filename}")
        
        return FileUploadResponse(
            success=upload_result.success,
            file_id=upload_result.file_id,
            filename=upload_result.filename,
            rows_processed=upload_result.rows_processed,
            rows_valid=upload_result.rows_valid,
            rows_errors=upload_result.rows_errors,
            data_hash=upload_result.data_hash,
            message=upload_result.message,
            validation_report=upload_result.validation_report
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing file"
        )


@router.post("/build-graph")
async def build_graph(
    invoices_file_id: str,
    companies_file_id: str = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Build knowledge graph from uploaded files
    """
    try:
        # Load CSV files
        invoices_path = Path(settings.UPLOAD_DIR) / f"{invoices_file_id}_invoice.csv"
        
        if not invoices_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice file not found"
            )
        
        import pandas as pd
        invoices_df = pd.read_csv(invoices_path)
        companies_df = None
        
        if companies_file_id:
            companies_path = Path(settings.UPLOAD_DIR) / f"{companies_file_id}_company.csv"
            if companies_path.exists():
                companies_df = pd.read_csv(companies_path)
        
        # Build graph
        graph_data = graph_builder.build_graph(invoices_df, companies_df)
        
        # Save graph
        graph_path = Path(settings.MODEL_DIR) / f"graph_{invoices_file_id}.pt"
        graph_path.parent.mkdir(parents=True, exist_ok=True)
        
        import torch
        torch.save({
            'x': graph_data.x,
            'edge_index': graph_data.edge_index,
            'edge_attr': graph_data.edge_attr,
            'num_nodes': graph_data.num_nodes,
            'entity_to_id': graph_builder.entity_to_id,
            'id_to_entity': graph_builder.id_to_entity
        }, graph_path)
        
        logger.info(f"Built graph with {graph_data.num_nodes} nodes and {graph_data.edge_index.shape[1]} edges")
        
        return {
            "success": True,
            "graph_id": invoices_file_id,
            "num_nodes": graph_data.num_nodes,
            "num_edges": graph_data.edge_index.shape[1],
            "graph_path": str(graph_path),
            "message": f"Graph built successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error building graph: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error building graph"
        )


@router.post("/batch-process", response_model=BatchProcessingResponse)
async def batch_process(
    request: BatchProcessingRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Process multiple files in batch
    """
    try:
        batch_id = f"batch_{datetime.now().timestamp()}"
        
        UPLOAD_JOBS[batch_id] = {
            "status": "processing",
            "total_files": len(request.file_ids),
            "processed_files": 0,
            "failed_files": 0,
            "started_at": datetime.now()
        }
        
        # TODO: Implement actual batch processing
        # For now, return mock response
        
        return BatchProcessingResponse(
            batch_id=batch_id,
            status="pending",
            total_files=len(request.file_ids),
            processed_files=0,
            failed_files=0,
            results={}
        )
    
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing batch"
        )


@router.get("/batch-status/{batch_id}")
async def get_batch_status(
    batch_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get status of batch processing job
    """
    if batch_id not in UPLOAD_JOBS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch job not found"
        )
    
    return UPLOAD_JOBS[batch_id]


@router.get("/list")
async def list_files(
    current_user: dict = Depends(get_current_user),
    file_type: str = None
):
    """
    List uploaded files
    """
    try:
        upload_dir = Path(settings.UPLOAD_DIR)
        files = []
        
        for file_path in upload_dir.glob("*.csv"):
            file_info = {
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime,
                "type": "invoice" if "_invoice" in file_path.name else "company"
            }
            
            if file_type is None or file_info['type'] == file_type:
                files.append(file_info)
        
        return {
            "total_files": len(files),
            "files": files
        }
    
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error listing files"
        )


@router.delete("/delete/{file_id}")
async def delete_file(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete uploaded file
    """
    try:
        file_path = Path(settings.UPLOAD_DIR) / f"{file_id}*.csv"
        
        # Security: only allow deleting own files or admin
        if current_user.get('roles', []).count('admin') == 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can delete files"
            )
        
        import glob
        files = glob.glob(str(file_path))
        
        if not files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        for f in files:
            os.remove(f)
        
        logger.info(f"User {current_user.get('username')} deleted {file_id}")
        
        return {
            "success": True,
            "message": f"Deleted {len(files)} file(s)"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting file"
        )
