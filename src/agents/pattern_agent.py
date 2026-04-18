"""Pattern Analysis Agent — uses Gemini to match transactions against
known Malaysian scam typologies.
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
from src.gemini_agent import GeminiAgent  # reuse JSON parsing

logger = logging.getLogger(__name__)

PATTERN_PROMPT = """You are the Pattern Analysis module of SEMA, a Malaysian fraud-prevention system.

Your ONLY job is to classify the transaction against known Malaysian scam typologies and list matching risk patterns.

Transaction:
- Amount: RM {amount}
- Type: {transaction_type}
- New device: {is_new_device}
- Night-time: {is_night}
- ML risk score: {ml_risk_score}%

Known Malaysian scam typologies to check:
1. Macau Scam — impersonation of police, court officials, or bank staff demanding urgent transfers
2. Love/Romance Scam — emotional manipulation leading to repeated money transfers
3. Parcel Scam — fake customs/delivery fees for non-existent packages
4. LHDN Tax Scam — fake tax authority demands with threats of arrest
5. Mule Account — rapid small test deposits followed by large withdrawal
6. Investment Scam — promises of unrealistic returns (e.g. crypto, forex, gold)
7. E-wallet Phishing — fake Touch n Go / GrabPay / Boost alerts
8. Job Scam — upfront payment for non-existent jobs
9. Legitimate — no scam pattern detected

Respond with ONLY valid JSON (no markdown fences):
{{
  "matched_patterns": ["<pattern name>"],
  "primary_scam_type": "<most likely type or 'legitimate'>",
  "pattern_risk_score": <0-100>,
  "pattern_reasoning": "<one sentence explaining why this pattern matched>"
}}"""


class PatternAgent:
    """Classifies transactions against Malaysian scam typologies via Gemini."""

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
        ml_risk_score: float,
    ) -> Optional[dict]:
        if not self.available:
            return None

        prompt = PATTERN_PROMPT.format(
            amount=amount,
            transaction_type=transaction_type,
            is_new_device=is_new_device,
            is_night=is_night,
            ml_risk_score=round(ml_risk_score, 2),
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
            logger.error("PatternAgent failed: %s", e)

        return None
