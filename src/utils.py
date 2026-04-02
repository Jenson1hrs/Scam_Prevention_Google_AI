 #"""Utility functions for the SEMA Fraud Detection System."""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def format_risk_response(
    risk_score: float,
    status: str,
    explanation: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Format the risk response for API output."""
    response = {
        "risk_score": round(risk_score, 2),
        "status": status,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if explanation:
        response["explanation"] = explanation
    
    return response

def validate_transaction_data(data: Dict[str, Any]) -> bool:
    """Validate incoming transaction data."""
    required_fields = ["amount", "transaction_type", "merchant"]
    
    for field in required_fields:
        if field not in data:
            logger.error(f"Missing required field: {field}")
            return False
    
    # Validate amount
    try:
        amount = float(data["amount"])
        if amount <= 0:
            logger.error(f"Invalid amount: {amount}")
            return False
    except (ValueError, TypeError):
        logger.error(f"Amount must be a number: {data.get('amount')}")
        return False
    
    return True

def log_api_call(endpoint: str, request_data: Dict, response_data: Dict):
    """Log API calls for monitoring."""
    logger.info(
        f"API Call: {endpoint} | "
        f"Request: {json.dumps(request_data, default=str)} | "
        f"Response: {json.dumps(response_data, default=str)}"
    )
 
