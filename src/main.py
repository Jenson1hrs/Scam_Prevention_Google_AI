"""Main FastAPI application for SEMA Fraud Detection System.

Multi-agent pipeline:
  1. ML Agent (XGBoost) produces a base risk probability.
  2. Pattern Agent (Gemini) classifies against Malaysian scam typologies.
  3. Context Agent (Gemini) evaluates behavioural signals.
  4. Orchestrator blends all three into a final verdict.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import logging

from src.gemini_agent import GeminiAgent
from src.agents.ml_agent import MLAgent
from src.agents.pattern_agent import PatternAgent
from src.agents.context_agent import ContextAgent
from src.agents.orchestrator import run_fraud_analysis
from src.whatsapp_integration import router as whatsapp_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ── Request / Response schemas ────────────────────────────────────────

class TransactionRequest(BaseModel):
    """Transaction data for fraud prediction."""
    amount: float = Field(..., description="Transaction amount in RM", gt=0)
    transaction_type: str = Field(default="online", description="online, pos, atm, transfer")
    is_new_device: int = Field(default=0, description="1 if new device, 0 if known")
    is_night: int = Field(default=0, description="1 if 10 PM–5 AM, 0 otherwise")
    is_small_amount: int = Field(default=0, description="1 if amount < RM 100")
    is_round_amount: int = Field(default=0, description="1 if amount is a round number")


class SHAPFeature(BaseModel):
    """Single SHAP feature contribution."""
    feature: str
    impact: float
    direction: str


class PredictionResponse(BaseModel):
    """Multi-agent fraud analysis result."""
    risk_score: float
    ml_risk_score: float
    gemini_risk_score: Optional[float] = None
    pattern_risk_score: Optional[float] = None
    context_risk_score: Optional[float] = None
    status: str
    risk_level: str
    scam_type: Optional[str] = None
    matched_patterns: Optional[List[str]] = None
    suspicious_signals: Optional[List[str]] = None
    explanation: Optional[str] = None
    recommended_action: Optional[str] = None
    shap_explanation: Optional[List[SHAPFeature]] = None
    message: str
    analysis_mode: str = Field(description="'multi_agent', 'ml_only', or 'fallback'")


class MessageRequest(BaseModel):
    """SMS / WhatsApp message to analyse for scam patterns."""
    message: str = Field(..., min_length=1, description="Message text to analyse")
    sender: Optional[str] = Field(None, description="Sender number or name")


class MessageAnalysisResponse(BaseModel):
    """Scam detection result for a message."""
    is_scam: bool
    confidence: float
    scam_type: str
    red_flags: List[str]
    explanation: str
    advice: str


# ── Global agent instances ────────────────────────────────────────────

ml_agent: Optional[MLAgent] = None
pattern_agent: Optional[PatternAgent] = None
context_agent: Optional[ContextAgent] = None
gemini_agent: Optional[GeminiAgent] = None


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Initialise agents on startup, clean up on shutdown."""
    global ml_agent, pattern_agent, context_agent, gemini_agent

    ml_agent = MLAgent()
    pattern_agent = PatternAgent()
    context_agent = ContextAgent()
    gemini_agent = GeminiAgent()

    logger.info(
        "Startup complete  ML=%s  Pattern=%s  Context=%s  Gemini=%s",
        ml_agent.available,
        pattern_agent.available,
        context_agent.available,
        gemini_agent.available,
    )
    yield


# ── FastAPI app ───────────────────────────────────────────────────────

app = FastAPI(
    title="SEMA Fraud Detection API",
    description=(
        "Explainable AI system for preventing financial scams in Malaysia. "
        "Uses a multi-agent architecture: XGBoost ML model + Google Gemini "
        "pattern analysis + behavioural context evaluation."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(whatsapp_router)


# ── Endpoints ─────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "service": "SEMA Fraud Detection API",
        "version": "2.0.0",
        "status": "running",
        "agents": {
            "ml": ml_agent.available if ml_agent else False,
            "pattern": pattern_agent.available if pattern_agent else False,
            "context": context_agent.available if context_agent else False,
            "gemini_message": gemini_agent.available if gemini_agent else False,
        },
        "endpoints": {
            "health": "/health",
            "predict": "/predict  [POST]",
            "analyze_message": "/analyze-message  [POST]",
            "whatsapp_webhook": "/whatsapp  [POST]",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ml_model_loaded": ml_agent.available if ml_agent else False,
        "gemini_available": gemini_agent.available if gemini_agent else False,
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(transaction: TransactionRequest):
    """Run the full multi-agent fraud analysis pipeline."""

    result = await run_fraud_analysis(
        amount=transaction.amount,
        transaction_type=transaction.transaction_type,
        is_new_device=transaction.is_new_device,
        is_night=transaction.is_night,
        is_small_amount=transaction.is_small_amount,
        is_round_amount=transaction.is_round_amount,
        ml_agent=ml_agent,
        pattern_agent=pattern_agent,
        context_agent=context_agent,
    )

    # Build human-readable explanation
    parts = []
    if result.pattern_reasoning:
        parts.append(result.pattern_reasoning)
    if result.context_summary:
        parts.append(result.context_summary)
    explanation = " ".join(parts) if parts else None

    if result.analysis_mode == "multi_agent":
        message = "Multi-agent analysis complete (ML + Pattern + Context)."
    elif result.analysis_mode == "ml_only":
        message = "ML prediction only. Gemini agents unavailable."
    else:
        message = "Fallback rule-based scoring. ML model not loaded."

    shap_data = [SHAPFeature(**f) for f in result.shap_explanation] if result.shap_explanation else None

    return PredictionResponse(
        risk_score=result.final_score,
        ml_risk_score=result.ml_score,
        gemini_risk_score=result.gemini_score,
        pattern_risk_score=result.pattern_score,
        context_risk_score=result.context_score,
        status=f"{result.risk_level} RISK",
        risk_level=result.risk_level,
        scam_type=result.scam_type,
        matched_patterns=result.matched_patterns or None,
        suspicious_signals=result.suspicious_signals or None,
        explanation=explanation,
        recommended_action=result.recommended_action,
        shap_explanation=shap_data,
        message=message,
        analysis_mode=result.analysis_mode,
    )


@app.post("/analyze-message", response_model=MessageAnalysisResponse)
async def analyze_message(request: MessageRequest):
    """Detect scam patterns in an SMS or WhatsApp message using Gemini."""

    if not gemini_agent or not gemini_agent.available:
        raise HTTPException(
            status_code=503,
            detail="Gemini is not configured. Set the GEMINI_API_KEY environment variable.",
        )

    result = await gemini_agent.analyze_message(
        message_text=request.message,
        sender=request.sender,
    )

    if result is None:
        raise HTTPException(status_code=502, detail="Gemini analysis failed. Please try again.")

    return MessageAnalysisResponse(
        is_scam=result.get("is_scam", False),
        confidence=float(result.get("confidence", 0)),
        scam_type=result.get("scam_type", "unknown"),
        red_flags=result.get("red_flags", []),
        explanation=result.get("explanation", "Unable to determine."),
        advice=result.get("advice", "Exercise caution with this message."),
    )


# ── Local dev entry point ─────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
