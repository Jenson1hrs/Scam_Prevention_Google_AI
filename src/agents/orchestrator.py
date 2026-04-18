"""Orchestrator — coordinates ML, Pattern, and Context agents to produce
a unified fraud verdict.

Flow:
  1. ML Agent runs first (fast, synchronous).
  2. Pattern Agent and Context Agent run in parallel (both use Gemini).
  3. Scores are aggregated with configurable weights.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import List, Optional

from config.settings import ML_WEIGHT, GEMINI_WEIGHT
from src.agents.ml_agent import MLAgent
from src.agents.pattern_agent import PatternAgent
from src.agents.context_agent import ContextAgent

logger = logging.getLogger(__name__)

# Within the Gemini portion, pattern gets 60 % and context 40 %
_PATTERN_SHARE = 0.6
_CONTEXT_SHARE = 0.4


@dataclass
class OrchestrationResult:
    """Unified output from the multi-agent pipeline."""
    final_score: float = 0.0
    ml_score: float = 0.0
    gemini_score: Optional[float] = None
    pattern_score: Optional[float] = None
    context_score: Optional[float] = None
    risk_level: str = "LOW"
    scam_type: Optional[str] = None
    matched_patterns: List[str] = field(default_factory=list)
    suspicious_signals: List[str] = field(default_factory=list)
    pattern_reasoning: Optional[str] = None
    context_summary: Optional[str] = None
    recommended_action: str = "allow"
    analysis_mode: str = "ml_only"
    shap_explanation: List[dict] = field(default_factory=list)


async def run_fraud_analysis(
    amount: float,
    transaction_type: str,
    is_new_device: int,
    is_night: int,
    is_small_amount: int,
    is_round_amount: int,
    ml_agent: MLAgent,
    pattern_agent: PatternAgent,
    context_agent: ContextAgent,
) -> OrchestrationResult:
    """Execute the full multi-agent pipeline and return a merged result."""

    result = OrchestrationResult()

    # ── Stage 1: ML Agent (synchronous) ─────────────────────────
    ml_out = ml_agent.predict(
        amount=amount,
        is_small_amount=is_small_amount,
        is_round_amount=is_round_amount,
        is_night=is_night,
        is_new_device=is_new_device,
    )
    result.ml_score = ml_out["risk_score"]
    result.shap_explanation = ml_out.get("shap_explanation", [])

    # ── Stage 2: Gemini agents in parallel ──────────────────────
    pattern_task = _safe(pattern_agent.analyze(
        amount=amount,
        transaction_type=transaction_type,
        is_new_device=bool(is_new_device),
        is_night=bool(is_night),
        ml_risk_score=result.ml_score,
    ))

    context_task = _safe(context_agent.analyze(
        amount=amount,
        transaction_type=transaction_type,
        is_new_device=bool(is_new_device),
        is_night=bool(is_night),
        is_small_amount=bool(is_small_amount),
        is_round_amount=bool(is_round_amount),
    ))

    pattern_out, context_out = await asyncio.gather(pattern_task, context_task)

    # ── Stage 3: Aggregate ──────────────────────────────────────
    gemini_parts: list[float] = []

    if pattern_out and "pattern_risk_score" in pattern_out:
        result.pattern_score = float(pattern_out["pattern_risk_score"])
        result.scam_type = pattern_out.get("primary_scam_type")
        result.matched_patterns = pattern_out.get("matched_patterns", [])
        result.pattern_reasoning = pattern_out.get("pattern_reasoning")
        gemini_parts.append((_PATTERN_SHARE, result.pattern_score))

    if context_out and "context_risk_score" in context_out:
        result.context_score = float(context_out["context_risk_score"])
        result.suspicious_signals = context_out.get("suspicious_signals", [])
        result.context_summary = context_out.get("context_summary")
        gemini_parts.append((_CONTEXT_SHARE, result.context_score))

    if gemini_parts:
        total_weight = sum(w for w, _ in gemini_parts)
        result.gemini_score = round(
            sum(w * s for w, s in gemini_parts) / total_weight, 2,
        )
        result.final_score = round(
            ML_WEIGHT * result.ml_score + GEMINI_WEIGHT * result.gemini_score, 2,
        )
        result.analysis_mode = "multi_agent"
    else:
        result.final_score = result.ml_score
        result.analysis_mode = (
            "ml_only" if ml_out["method"] == "xgboost" else "fallback"
        )

    # Risk level & recommended action
    if result.final_score > 70:
        result.risk_level = "HIGH"
        result.recommended_action = "block"
    elif result.final_score > 40:
        result.risk_level = "MEDIUM"
        result.recommended_action = "verify"
    else:
        result.risk_level = "LOW"
        result.recommended_action = "allow"

    return result


async def _safe(coro) -> Optional[dict]:
    """Run a coroutine and swallow exceptions so one agent can't crash the pipeline."""
    try:
        return await coro
    except Exception as e:
        logger.error("Agent failed: %s", e)
        return None
