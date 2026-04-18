"""Context Agent — uses Gemini to evaluate behavioural signals around
the transaction (timing, device, amount patterns).
"""

import logging
from typing import Optional

from google import genai
from google.genai import types

from config.settings import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
    GEMINI_MAX_OUTPUT_TOKENS,
)
from src.gemini_agent import GeminiAgent

logger = logging.getLogger(__name__)

CONTEXT_PROMPT = """You are the Context Analysis module of SEMA, a Malaysian fraud-prevention system.

Your ONLY job is to evaluate the *behavioural context* of a transaction — timing, device trust, and amount anomalies — and flag anything suspicious.

Transaction context:
- Amount: RM {amount}
- Transaction type: {transaction_type}
- New/unknown device: {is_new_device}
- Late-night (10 PM – 5 AM): {is_night}
- Small amount (< RM 100): {is_small_amount}
- Round amount: {is_round_amount}

Consider:
- Mule accounts often start with small test transactions before a large withdrawal.
- Late-night transactions on new devices are higher risk.
- Round amounts (RM 1000, RM 5000) in transfers can indicate social-engineering scams.
- Legitimate purchases tend to have non-round amounts and occur during daytime on known devices.

Respond with ONLY valid JSON (no markdown fences):
{{
  "context_risk_score": <0-100>,
  "suspicious_signals": ["<signal 1>", "<signal 2>"],
  "context_summary": "<one sentence summary of behavioural risk>"
}}"""


class ContextAgent:
    """Evaluates behavioural context of a transaction via Gemini."""

    def __init__(self, client: Optional[genai.Client] = None):
        if client:
            self.client = client
        elif GEMINI_API_KEY:
            self.client = genai.Client(api_key=GEMINI_API_KEY)
        else:
            self.client = None

        self._config = types.GenerateContentConfig(
            temperature=GEMINI_TEMPERATURE,
            max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
            response_mime_type="application/json",
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )

    @property
    def available(self) -> bool:
        return self.client is not None

    async def analyze(
        self,
        amount: float,
        transaction_type: str,
        is_new_device: bool,
        is_night: bool,
        is_small_amount: bool,
        is_round_amount: bool,
    ) -> Optional[dict]:
        if not self.available:
            return None

        prompt = CONTEXT_PROMPT.format(
            amount=amount,
            transaction_type=transaction_type,
            is_new_device=is_new_device,
            is_night=is_night,
            is_small_amount=is_small_amount,
            is_round_amount=is_round_amount,
        )

        try:
            response = await self.client.aio.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=self._config,
            )
            if response.text:
                return GeminiAgent._parse_json(response.text)
        except Exception as e:
            logger.error("ContextAgent failed: %s", e)

        return None
