"""ML Risk Agent — runs the XGBoost pipeline and returns a structured verdict
with optional SHAP explanations.
"""

import logging
from typing import Optional, List, Dict, Any

import joblib
import numpy as np

from config.settings import MODELS_DIR
from src.explainer import SHAPExplainer

logger = logging.getLogger(__name__)


class MLAgent:
    """Wraps the trained XGBoost fraud-detection model."""

    def __init__(self):
        self.model = None
        self.feature_names = None
        self.explainer: Optional[SHAPExplainer] = None
        self._load()

    def _load(self):
        model_path = MODELS_DIR / "fraud_pipeline.joblib"
        features_path = MODELS_DIR / "feature_names.joblib"

        if not model_path.exists():
            logger.warning("ML model not found at %s", model_path)
            return

        try:
            self.model = joblib.load(model_path)
            if features_path.exists():
                self.feature_names = joblib.load(features_path)
            self.explainer = SHAPExplainer(self.model, self.feature_names)
            logger.info("MLAgent: model loaded (SHAP=%s)", self.explainer.available)
        except Exception as e:
            logger.error("MLAgent: failed to load model – %s", e)

    @property
    def available(self) -> bool:
        return self.model is not None

    def predict(
        self,
        amount: float,
        is_small_amount: int,
        is_round_amount: int,
        is_night: int,
        is_new_device: int,
    ) -> dict:
        """Return a risk dict with score, method, and optional SHAP explanations."""
        if self.model is not None:
            features = self._prepare_features(
                amount, is_small_amount, is_round_amount, is_night, is_new_device,
            )
            prob = float(self.model.predict_proba(features)[0][1])

            shap_explanation: List[Dict[str, Any]] = []
            if self.explainer and self.explainer.available:
                shap_explanation = self.explainer.explain(features, top_k=5)

            return {
                "risk_score": round(prob * 100, 2),
                "method": "xgboost",
                "shap_explanation": shap_explanation,
            }

        # Rule-based fallback
        score = min(100.0, (amount / 10000) * 100)
        if is_night:
            score += 10
        if is_new_device:
            score += 15
        return {
            "risk_score": round(min(100.0, score), 2),
            "method": "rule_fallback",
            "shap_explanation": [],
        }

    @staticmethod
    def _prepare_features(
        amount: float,
        is_small_amount: int,
        is_round_amount: int,
        is_night: int,
        is_new_device: int,
    ) -> np.ndarray:
        """Build a 33-feature vector matching the training schema:
        V1–V28 (28) + Amount + Time + is_night + is_small_amount + is_round_amount
        """
        v_features = [0.0] * 28
        amount_scaled = max(-3.0, min(3.0, (amount - 88.35) / 250.0))

        features = v_features + [
            amount_scaled,          # Amount (scaled)
            0.0,                    # Time (scaled)
            float(is_night),
            float(is_small_amount),
            float(is_round_amount),
        ]
        return np.array(features).reshape(1, -1)
