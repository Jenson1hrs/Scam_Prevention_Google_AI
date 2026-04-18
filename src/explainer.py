"""SHAP-based explainability for the XGBoost fraud model.

Produces per-feature importance values that explain *why* a specific
transaction was flagged, complementing Gemini's natural-language reasoning.
"""

import logging
from typing import Optional, List, Dict, Any

import numpy as np

logger = logging.getLogger(__name__)

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logger.warning("shap package not installed – explainability disabled")

DEFAULT_FEATURE_NAMES = [
    *(f"V{i}" for i in range(1, 29)),
    "Amount",
    "Time",
    "is_night",
    "is_small_amount",
    "is_round_amount",
]


class SHAPExplainer:
    """Wraps a SHAP TreeExplainer for the fraud detection model."""

    def __init__(self, model, feature_names: Optional[List[str]] = None):
        self.model = model
        self.feature_names = feature_names or DEFAULT_FEATURE_NAMES
        self.explainer: Optional[Any] = None

        if not SHAP_AVAILABLE:
            return

        try:
            self.explainer = shap.TreeExplainer(model)
            logger.info("SHAPExplainer initialised with %d features", len(self.feature_names))
        except Exception as e:
            logger.error("Failed to init SHAP TreeExplainer: %s", e)

    @property
    def available(self) -> bool:
        return self.explainer is not None

    def explain(self, features: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """Return the top-k features driving the fraud prediction.

        Each entry: {"feature": name, "impact": float, "direction": "increases_risk" | "decreases_risk"}
        """
        if not self.available:
            return []

        try:
            shap_values = self.explainer.shap_values(features)

            # For binary classifiers shap_values may be a list [class_0, class_1]
            if isinstance(shap_values, list):
                values = shap_values[1][0]  # class 1 = fraud
            else:
                values = shap_values[0]

            indices = np.argsort(np.abs(values))[::-1][:top_k]

            explanations = []
            for idx in indices:
                name = self.feature_names[idx] if idx < len(self.feature_names) else f"feature_{idx}"
                val = float(values[idx])
                explanations.append({
                    "feature": name,
                    "impact": round(abs(val), 4),
                    "direction": "increases_risk" if val > 0 else "decreases_risk",
                })
            return explanations

        except Exception as e:
            logger.error("SHAP explanation failed: %s", e)
            return []
