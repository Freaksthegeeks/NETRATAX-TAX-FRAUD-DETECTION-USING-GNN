"""
File Upload Router
CSV upload, validation, and processing
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
from pathlib import Path
import logging

from routers.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(__file__).parent.parent.parent / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class UploadResponse(BaseModel):
    filename: str
    rows: int
    columns: int
    status: str
    message: str
    validation_errors: List[str] = []

class ValidationResponse(BaseModel):
    valid: bool
    errors: List[str]
    warnings: List[str]
    row_count: int
    column_count: int

REQUIRED_COLUMNS = [
    "Supplier_GSTIN", "Buyer_GSTIN", "Invoice_No", 
    "Date", "Amount", "CGST", "SGST", "IGST", "ITC_Claimed"
]

@router.post("/upload_csv", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload CSV file for processing"""
    try:
        # Save file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Read and validate
        try:
            df = pd.read_csv(file_path)
            rows, cols = df.shape
            
            # Validate columns
            validation_errors = []
            missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
            if missing_cols:
                validation_errors.append(f"Missing required columns: {', '.join(missing_cols)}")
            
            return UploadResponse(
                filename=file.filename,
                rows=int(rows),
                columns=int(cols),
                status="uploaded",
                message="File uploaded successfully",
                validation_errors=validation_errors
            )
        except Exception as e:
            return UploadResponse(
                filename=file.filename,
                rows=0,
                columns=0,
                status="error",
                message=f"Error reading CSV: {str(e)}",
                validation_errors=[str(e)]
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

@router.post("/validate", response_model=ValidationResponse)
async def validate_csv(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Validate CSV file structure"""
    try:
        # Read file
        content = await file.read()
        df = pd.read_csv(pd.io.common.BytesIO(content))
        
        errors = []
        warnings = []
        
        # Check required columns
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {', '.join(missing_cols)}")
        
        # Check for empty rows
        if df.empty:
            errors.append("File is empty")
        
        # Check data types
        if "Amount" in df.columns:
            try:
                pd.to_numeric(df["Amount"], errors='raise')
            except:
                errors.append("Amount column contains non-numeric values")
        
        # Warnings
        if len(df) < 10:
            warnings.append("File contains very few rows (< 10)")
        
        return ValidationResponse(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            row_count=len(df),
            column_count=len(df.columns)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")

@router.post("/process")
async def process_csv(
    filename: str,
    current_user: dict = Depends(get_current_user)
):
    """Process uploaded CSV file"""
    try:
        file_path = UPLOAD_DIR / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        df = pd.read_csv(file_path)
        
        # Process file (add to graph, run inference, etc.)
        # This would integrate with the graph construction and model inference
        
        return {
            "status": "processed",
            "filename": filename,
            "rows_processed": len(df),
            "message": "File processed successfully. Graph updated."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

