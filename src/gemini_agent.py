"""Gemini-powered fraud analysis agent for SEMA.

Uses the google-genai SDK to provide AI reasoning on top of ML predictions,
combining transaction risk scoring with Malaysian scam pattern detection.
"""

import asyncio
import json
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

logger = logging.getLogger(__name__)

TRANSACTION_ANALYSIS_PROMPT = """You are SEMA, an AI fraud analyst protecting Malaysian citizens from financial scams.

Analyze this transaction and provide your independent risk assessment:

Transaction Details:
- Amount: RM {amount}
- Type: {transaction_type}
- New/unknown device: {is_new_device}
- Late-night (10 PM – 5 AM): {is_night}
- Small amount (< RM 100): {is_small_amount}
- Round amount: {is_round_amount}

ML Model Risk Score: {ml_risk_score}%

Consider common Malaysian fraud patterns:
- Macau scam (impersonation of police/court officials demanding payment)
- Love/romance scam (building trust then requesting money transfers)
- Parcel scam (fake customs fees for non-existent packages)
- LHDN tax scam (fake tax authority demanding immediate payment)
- Mule account activity (rapid small transfers to test account, followed by large withdrawal)
- Investment scam (promises of unrealistic returns)

Respond with ONLY valid JSON (no markdown fences):
{{
  "gemini_risk_score": <0-100 integer>,
  "scam_type": "<most likely scam category or 'legitimate'>",
  "confidence": <0-100 how confident you are>,
  "explanation": "<2-3 sentence explanation for the end user>",
  "risk_factors": ["<factor 1>", "<factor 2>"],
  "recommended_action": "<block | verify | allow>"
}}"""

MESSAGE_ANALYSIS_PROMPT = """You are SEMA, a scam message detector built to protect Malaysian citizens.

Analyze this message for scam indicators:

---
{message_text}
---

Sender info: {sender_info}

Check for these Malaysian-specific scam patterns:
- Phishing links impersonating banks (Maybank, CIMB, RHB, Public Bank, Bank Islam)
- Government agency impersonation (LHDN, PDRM, JPJ, SSM, KWSP)
- E-wallet scams (Touch 'n Go, GrabPay, Boost, ShopeePay)
- Prize/lottery scams (fake contest winnings)
- Job offer scams (unrealistic salary, upfront fees)
- Parcel delivery scams (Pos Malaysia, J&T, fake customs)
- Urgency or fear tactics (account frozen, warrant of arrest)
- Requests for TAC/OTP codes
- Suspicious shortened URLs

Respond with ONLY valid JSON (no markdown fences):
{{
  "is_scam": <true or false>,
  "confidence": <0-100>,
  "scam_type": "<specific scam category>",
  "red_flags": ["<indicator 1>", "<indicator 2>"],
  "explanation": "<user-friendly explanation in simple English>",
  "advice": "<what the user should do next>"
}}"""


class GeminiAgent:
    """Wraps the Gemini API for fraud analysis tasks."""

    def __init__(self):
        if not GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set – Gemini features disabled")
            self.client = None
            return

        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self._config = types.GenerateContentConfig(
            temperature=GEMINI_TEMPERATURE,
            max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
            response_mime_type="application/json",
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )
        logger.info("Gemini agent initialised (model=%s)", GEMINI_MODEL)

    @property
    def available(self) -> bool:
        return self.client is not None

    async def analyze_transaction(
        self,
        amount: float,
        transaction_type: str,
        is_new_device: bool,
        is_night: bool,
        is_small_amount: bool,
        is_round_amount: bool,
        ml_risk_score: float,
    ) -> Optional[dict]:
        """Ask Gemini to reason about a transaction's fraud risk.

        Returns parsed JSON dict on success, None on failure.
        """
        if not self.available:
            return None

        prompt = TRANSACTION_ANALYSIS_PROMPT.format(
            amount=amount,
            transaction_type=transaction_type,
            is_new_device=is_new_device,
            is_night=is_night,
            is_small_amount=is_small_amount,
            is_round_amount=is_round_amount,
            ml_risk_score=round(ml_risk_score, 2),
        )

        return await self._call_gemini(prompt)

    async def analyze_message(
        self,
        message_text: str,
        sender: Optional[str] = None,
    ) -> Optional[dict]:
        """Ask Gemini to detect scam patterns in a text message.

        Returns parsed JSON dict on success, None on failure.
        """
        if not self.available:
            return None

        prompt = MESSAGE_ANALYSIS_PROMPT.format(
            message_text=message_text,
            sender_info=sender or "Unknown",
        )

        return await self._call_gemini(prompt)

    async def _call_gemini(self, prompt: str, max_retries: int = 3) -> Optional[dict]:
        """Send a prompt to Gemini with automatic retry on rate limits."""
        for attempt in range(max_retries):
            try:
                response = await self.client.aio.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt,
                    config=self._config,
                )

                if not response.text:
                    logger.error("Gemini returned empty response")
                    return None

                return self._parse_json(response.text)

            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    wait = 2 ** attempt * 5  # 5s, 10s, 20s
                    logger.warning("Rate limited, retrying in %ds (attempt %d/%d)", wait, attempt + 1, max_retries)
                    await asyncio.sleep(wait)
                    continue
                logger.error("Gemini API call failed: %s", e)
                return None

        logger.error("Gemini call failed after %d retries (rate limited)", max_retries)
        return None

    @staticmethod
    def _parse_json(text: str) -> Optional[dict]:
        """Safely extract JSON from Gemini's response text."""
        cleaned = text.strip()

        # Strip markdown code fences if present
        if cleaned.startswith("```"):
            first_newline = cleaned.index("\n")
            cleaned = cleaned[first_newline + 1:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        try:
            return json.loads(cleaned.strip())
        except json.JSONDecodeError as e:
            logger.error("Failed to parse Gemini JSON: %s\nRaw: %s", e, text[:500])
            return None
