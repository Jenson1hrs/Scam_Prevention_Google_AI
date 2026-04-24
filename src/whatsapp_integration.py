"""Twilio WhatsApp webhook integration for SEMA."""

from __future__ import annotations

import asyncio
from typing import Optional

from fastapi import APIRouter, Form, HTTPException, Request, Response
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

from config.settings import TWILIO_AUTH_TOKEN
from src.gemini_agent import GeminiAgent
router = APIRouter(tags=["Twilio WhatsApp"])


def _twilio_request_url(request: Request) -> str:
    """Public URL Twilio signed, matching proxy headers on Cloud Run / load balancers."""
    proto = (request.headers.get("x-forwarded-proto") or request.url.scheme or "https").split(",")[0].strip()
    host = (request.headers.get("x-forwarded-host") or request.headers.get("host") or request.url.netloc).split(",")[0].strip()
    path = request.url.path
    query = request.url.query
    base = f"{proto}://{host}{path}"
    return f"{base}?{query}" if query else base


async def _validate_twilio_signature(request: Request) -> None:
    """Validate Twilio signature when auth token is configured."""
    if not TWILIO_AUTH_TOKEN:
        return

    signature = request.headers.get("X-Twilio-Signature")
    if not signature:
        raise HTTPException(status_code=403, detail="Missing Twilio signature header.")

    form = await request.form()
    params = {k: str(v) for k, v in form.multi_items()}
    validator = RequestValidator(TWILIO_AUTH_TOKEN)

    url = _twilio_request_url(request)
    if not validator.validate(url, params, signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature.")


def _build_reply_text(result: dict) -> str:
    """Convert Gemini message analysis output into a WhatsApp-friendly reply."""
    is_scam = bool(result.get("is_scam", False))
    confidence = float(result.get("confidence", 0))
    scam_type = str(result.get("scam_type", "unknown")).strip() or "unknown"
    explanation = str(result.get("explanation", "No explanation available.")).strip()
    advice = str(result.get("advice", "Avoid sharing personal or banking information.")).strip()
    red_flags = result.get("red_flags", []) or []
    red_flags_text = ", ".join(str(flag).strip() for flag in red_flags[:3] if str(flag).strip())

    if is_scam:
        header = f"SCAM ALERT ({confidence:.0f}% confidence)"
        details = f"Type: {scam_type}\nReason: {explanation}"
        if red_flags_text:
            details += f"\nRed flags: {red_flags_text}"
        return f"{header}\n{details}\nAdvice: {advice}"

    return (
        f"Likely safe message ({confidence:.0f}% confidence).\n"
        f"Reason: {explanation}\n"
        f"Advice: {advice}"
    )


@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    From: Optional[str] = Form(default=None),
    Body: str = Form(...),
):
    """Receive incoming Twilio WhatsApp messages and return TwiML response."""
    await _validate_twilio_signature(request)

    reply_text: Optional[str] = None
    gemini = GeminiAgent()
    if gemini.available:
        try:
            # Keep within Twilio's webhook timeout budget.
            result = await asyncio.wait_for(
                gemini.analyze_message(message_text=Body, sender=From, max_retries=1),
                timeout=8.0,
            )
        except asyncio.TimeoutError:
            reply_text = None
        else:
            if result is None:
                reply_text = None
            else:
                reply_text = _build_reply_text(result)

    twiml = MessagingResponse()
    if reply_text:
        twiml.message(reply_text)
    return Response(content=str(twiml), media_type="application/xml")
