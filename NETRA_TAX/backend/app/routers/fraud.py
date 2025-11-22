"""
Fraud Detection Router for NETRA TAX
Company risk, invoice risk, network analysis, explanations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.core.security import get_current_user
from app.models.schemas import (
    NodeRiskResponse,
    InvoiceRiskRequest,
    InvoiceRiskResponse,
    FraudScoreResponse,
    NetworkAnalysisResponse,
    FraudExplanationResponse,
    CompanySearchRequest,
    CompanySearchResponse,
    InvoiceSearchRequest,
    InvoiceSearchResponse
)
from app.fraud.detection_engine import FraudDetectionEngine
import logging
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/fraud", tags=["Fraud Detection"])

# Global fraud detection engine (will be initialized with loaded model)
FRAUD_ENGINE: Optional[FraudDetectionEngine] = None


def set_fraud_engine(engine: FraudDetectionEngine):
    """Set the fraud detection engine instance"""
    global FRAUD_ENGINE
    FRAUD_ENGINE = engine


def get_fraud_engine() -> FraudDetectionEngine:
    """Get fraud detection engine"""
    if FRAUD_ENGINE is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Fraud detection engine not initialized"
        )
    return FRAUD_ENGINE


# ============================================================================
# Company Risk Endpoints
# ============================================================================

@router.get("/company/risk/{gstin}", response_model=NodeRiskResponse)
async def get_company_risk(
    gstin: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get fraud risk score for a company by GSTIN
    
    Returns:
    - Risk score (0-1)
    - Risk level (LOW, MEDIUM, HIGH)
    - Contributing factors
    """
    try:
        engine = get_fraud_engine()
        
        # For now, use hash of GSTIN to get node ID
        node_id = hash(gstin) % 1000
        
        risk_score = engine.node_risk(node_id)
        
        return NodeRiskResponse(
            entity_id=gstin,
            risk_score=risk_score.risk_score,
            risk_level=risk_score.risk_level.value,
            factors=risk_score.factors
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting company risk: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating company risk"
        )


@router.post("/company/search", response_model=CompanySearchResponse)
async def search_companies(
    request: CompanySearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Search companies by GSTIN, name, or director
    """
    try:
        # Mock search results for now
        # In production, query database
        results = [
            {
                "gstin": "27AABCT1234H1Z0",
                "name": "ABC Trading Co.",
                "director_name": "John Doe",
                "location": "Mumbai",
                "fraud_score": 45.2,
                "risk_level": "MEDIUM",
                "transaction_count": 28
            }
        ]
        
        return CompanySearchResponse(
            query=request.query,
            total_results=len(results),
            results=results
        )
    
    except Exception as e:
        logger.error(f"Error searching companies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching companies"
        )


# ============================================================================
# Invoice Risk Endpoints
# ============================================================================

@router.post("/invoice/risk", response_model=InvoiceRiskResponse)
async def get_invoice_risk(
    request: InvoiceRiskRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Get fraud risk for a specific invoice
    """
    try:
        engine = get_fraud_engine()
        
        fraud_result = engine.invoice_risk(request.invoice_id)
        
        return InvoiceRiskResponse(
            invoice_id=request.invoice_id,
            fraud_score=fraud_result.fraud_score,
            risk_level=fraud_result.risk_level.value,
            supplier_risk=fraud_result.evidence.get('sender_risk', 0),
            buyer_risk=fraud_result.evidence.get('receiver_risk', 0),
            reasons=fraud_result.reasons,
            pattern_flags=fraud_result.pattern_flags,
            confidence=fraud_result.confidence
        )
    
    except Exception as e:
        logger.error(f"Error getting invoice risk: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating invoice risk"
        )


@router.post("/invoice/search", response_model=InvoiceSearchResponse)
async def search_invoices(
    request: InvoiceSearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Search invoices by criteria
    """
    try:
        # Mock search results for now
        results = [
            {
                "invoice_number": "INV-2024-001",
                "supplier_gstin": "27AABCT1234H1Z0",
                "buyer_gstin": "29ABCDE1234H1Z0",
                "amount": 50000.0,
                "date": __import__('datetime').datetime.now(),
                "fraud_score": 35.5,
                "risk_level": "MEDIUM",
                "status": "Flagged"
            }
        ]
        
        return InvoiceSearchResponse(
            total_results=len(results),
            results=results
        )
    
    except Exception as e:
        logger.error(f"Error searching invoices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching invoices"
        )


# ============================================================================
# Network Analysis Endpoints
# ============================================================================

@router.get("/network/analysis/{node_id}")
async def analyze_network(
    node_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze network patterns around a node
    
    Returns:
    - Node risk information
    - Network metrics
    - Fraud patterns detected
    - Connected entities
    """
    try:
        engine = get_fraud_engine()
        
        analysis = engine.network_analysis(node_id)
        
        return analysis
    
    except Exception as e:
        logger.error(f"Error analyzing network: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error analyzing network"
        )


@router.get("/fraud-rings/{node_id}")
async def detect_fraud_rings(
    node_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Detect potential fraud rings around a node
    """
    try:
        engine = get_fraud_engine()
        
        # Get network analysis
        analysis = engine.network_analysis(node_id)
        fraud_rings = analysis['patterns']['fraud_rings']
        
        return {
            "node_id": node_id,
            "fraud_rings_detected": len(fraud_rings) > 0,
            "rings": fraud_rings,
            "total_nodes_in_rings": sum(len(ring) for ring in fraud_rings)
        }
    
    except Exception as e:
        logger.error(f"Error detecting fraud rings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error detecting fraud rings"
        )


# ============================================================================
# Explanation & Insights Endpoints
# ============================================================================

@router.get("/explain/{node_id}", response_model=FraudExplanationResponse)
async def explain_fraud_prediction(
    node_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Explain why a node was flagged as fraud
    
    Provides:
    - Fraud probability
    - Primary reasons
    - Network context
    - Pattern analysis
    - Confidence score
    - Auditor recommendations
    """
    try:
        engine = get_fraud_engine()
        
        explanation = engine.fraud_explanation(node_id)
        
        return FraudExplanationResponse(**explanation)
    
    except Exception as e:
        logger.error(f"Error generating explanation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating explanation"
        )


@router.get("/summary")
async def get_fraud_summary(
    min_risk_score: float = Query(0.5, ge=0, le=1),
    current_user: dict = Depends(get_current_user)
):
    """
    Get summary of fraud detections
    
    Returns:
    - Total high-risk entities
    - Fraud rings detected
    - Pattern flags
    - Recommendations
    """
    try:
        # Mock summary for now
        return {
            "total_scanned_entities": 1000,
            "high_risk_entities": 45,
            "medium_risk_entities": 120,
            "low_risk_entities": 835,
            "fraud_rings_detected": 8,
            "circular_trades_detected": 12,
            "pattern_alerts": 34,
            "recommendations": [
                "Audit 45 high-risk entities immediately",
                "Investigate 8 detected fraud rings",
                "Monitor 120 medium-risk entities"
            ],
            "confidence_score": 0.87
        }
    
    except Exception as e:
        logger.error(f"Error getting fraud summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating summary"
        )


# ============================================================================
# Bulk Analysis Endpoints
# ============================================================================

@router.post("/bulk-analyze")
async def bulk_analyze(
    entity_ids: list,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze multiple entities in batch
    """
    try:
        engine = get_fraud_engine()
        
        results = []
        for entity_id in entity_ids[:100]:  # Limit to 100
            try:
                risk_score = engine.node_risk(entity_id)
                results.append({
                    "entity_id": entity_id,
                    "risk_score": risk_score.risk_score,
                    "risk_level": risk_score.risk_level.value
                })
            except Exception as e:
                logger.warning(f"Error analyzing entity {entity_id}: {e}")
                results.append({
                    "entity_id": entity_id,
                    "error": str(e)
                })
        
        return {
            "total_analyzed": len(results),
            "successful": len([r for r in results if 'risk_score' in r]),
            "failed": len([r for r in results if 'error' in r]),
            "results": results
        }
    
    except Exception as e:
        logger.error(f"Error in bulk analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error in bulk analysis"
        )
