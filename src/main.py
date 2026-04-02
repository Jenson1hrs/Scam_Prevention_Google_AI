"""Main FastAPI application for SEMA Fraud Detection System."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import logging
import joblib
import numpy as np
from pathlib import Path
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the request model - MATCHES WHAT YOU SEE IN /docs
class TransactionRequest(BaseModel):
    """Transaction data for fraud prediction"""
    amount: float = Field(..., description="Transaction amount in RM", gt=0)
    transaction_type: str = Field(default="online", description="online, pos, atm, transfer")
    # Add all the fields that your model expects
    is_new_device: int = Field(default=0, description="1 if new device, 0 if known")
    is_night: int = Field(default=0, description="1 if 10PM-5AM, 0 otherwise")
    is_small_amount: int = Field(default=0, description="1 if amount < RM100")
    is_round_amount: int = Field(default=0, description="1 if amount is round number")

class PredictionResponse(BaseModel):
    """Prediction response"""
    risk_score: float
    status: str
    risk_level: str
    explanation: Optional[List[Dict[str, Any]]] = None
    message: str

# Global variables for model
model = None
feature_names = None

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"

def load_model():
    """Load the trained model"""
    global model, feature_names
    
    try:
        model_path = MODELS_DIR / "fraud_pipeline.joblib"
        features_path = MODELS_DIR / "feature_names.joblib"
        
        if not model_path.exists():
            logger.error(f"Model not found at {model_path}")
            logger.info(f"Please train the model first using notebooks/01_data_exploration.ipynb")
            return False
        
        model = joblib.load(model_path)
        
        if features_path.exists():
            feature_names = joblib.load(features_path)
        
        logger.info(f"✅ Model loaded successfully from {model_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return False

# Create FastAPI app
app = FastAPI(
    title="SEMA Fraud Detection API",
    description="Explainable AI system for preventing financial scams",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model on startup
@app.on_event("startup")
async def startup_event():
    """Load model when API starts"""
    success = load_model()
    if not success:
        logger.warning("⚠️ Model not loaded. Using fallback prediction.")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to SEMA Fraud Detection API",
        "status": "running",
        "model_loaded": model is not None,
        "endpoints": ["/health", "/predict", "/docs"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
    }

def prepare_features(amount: float, is_small_amount: int, is_round_amount: int, is_night: int, is_new_device: int) -> np.ndarray:
    """
    Prepare features for model prediction.
    Creates a 32-feature array matching the training data format.
    """
    # V1-V28: use 0 (median of normalized values for a typical transaction)
    v_features = [0.0] * 28
    
    # Scale amount (rough approximation of training scaling)
    # In training, Amount was normalized with mean ~88, std ~250
    amount_scaled = (amount - 88.35) / 250.0
    amount_scaled = max(-3, min(3, amount_scaled))  # Clip to reasonable range
    
    # Time feature (use 0 as default)
    time_scaled = 0.0
    
    # Synthetic features
    is_night_val = float(is_night)
    is_weekend = 0.0  # Default
    is_small_amount_val = float(is_small_amount)
    is_round_amount_val = float(is_round_amount)
    amount_deviation = 0.0  # Default
    
    # Combine all features in the correct order (must match training!)
    features = v_features + [amount_scaled, time_scaled, is_night_val, is_weekend, 
                              is_small_amount_val, is_round_amount_val, amount_deviation]
    
    return np.array(features).reshape(1, -1)

@app.post("/predict", response_model=PredictionResponse)
async def predict(transaction: TransactionRequest):
    """
    Predict fraud risk for a transaction.
    Returns risk score (0-100), risk level, and explanation.
    """
    # If model is not loaded, use fallback
    if model is None:
        # Fallback logic based on amount only
        risk_score = min(100, (transaction.amount / 10000) * 100)
        if transaction.is_night:
            risk_score += 10
        if transaction.is_new_device:
            risk_score += 15
        risk_score = min(100, risk_score)
        
        if risk_score > 70:
            status = "HIGH RISK 🚨"
            risk_level = "HIGH"
            message = "⚠️ Model not loaded. Using fallback rules. Please train the model first."
        elif risk_score > 40:
            status = "MEDIUM RISK ⚠️"
            risk_level = "MEDIUM"
            message = "⚠️ Model not loaded. Using fallback rules. Please train the model first."
        else:
            status = "LOW RISK ✅"
            risk_level = "LOW"
            message = "⚠️ Model not loaded. Using fallback rules. Please train the model first."
        
        return PredictionResponse(
            risk_score=round(risk_score, 2),
            status=status,
            risk_level=risk_level,
            explanation=None,
            message=message
        )
    
    try:
        # Prepare features using the transaction data
        features = prepare_features(
            amount=transaction.amount,
            is_small_amount=transaction.is_small_amount,
            is_round_amount=transaction.is_round_amount,
            is_night=transaction.is_night,
            is_new_device=transaction.is_new_device
        )
        
        # Get prediction probability
        probability = model.predict_proba(features)[0][1]
        risk_score = round(probability * 100, 2)
        
        # Determine risk level
        if risk_score > 70:
            status = "HIGH RISK 🚨"
            risk_level = "HIGH"
            message = "This transaction has high fraud indicators. Please verify carefully."
        elif risk_score > 40:
            status = "MEDIUM RISK ⚠️"
            risk_level = "MEDIUM"
            message = "This transaction shows some risk indicators. Consider additional verification."
        else:
            status = "LOW RISK ✅"
            risk_level = "LOW"
            message = "This transaction appears legitimate based on available data."
        
        return PredictionResponse(
            risk_score=risk_score,
            status=status,
            risk_level=risk_level,
            explanation=None,  # SHAP will be added later
            message=message
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)