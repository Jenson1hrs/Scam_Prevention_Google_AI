"""Message analyser page for the redesigned frontend."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st
import requests

from src.frontend._pages._layout import EYEBROW_TOOLS, page_header_compact, tools_outro


_EXAMPLE_MESSAGES = {
    "(select an example)": "",
    "Maybank phishing": "Your Maybank account has been locked due to suspicious activity. Click here to verify: http://maybank-secure-login.xyz",
    "LHDN tax scam": "PERINGATAN: Anda mempunyai tunggakan cukai sebanyak RM12,500. Hubungi 03-8765 4321 segera untuk mengelakkan waran tangkap.",
    "Prize scam": "Tahniah! Anda telah memenangi RM50,000 daripada Shopee Lucky Draw. Hantar RM200 yuran pemprosesan ke 012-3456789.",
    "Parcel scam": "Your parcel from J&T Express is held at customs. Pay RM89 clearance fee here: http://jnt-clearance.co/pay",
    "Job scam": "Hi! We saw your resume on JobStreet. Work from home, earn RM300/day! Just pay RM150 registration fee. WhatsApp 011-2233445.",
    "Legitimate bank SMS": "Your CIMB Clicks transfer of RM150.00 to ALI BIN ABU was successful on 17/04/2026 at 14:32.",
}

_TWILIO_SANDBOX_NUMBER = "+1 415 523 8886"
_TWILIO_SANDBOX_JOIN_CODE = "join rabbit-structure"
_TWILIO_QR_RELATIVE = Path("src/frontend/assets/twilio_sandbox_qr.png")


def _render_twilio_sandbox_qr() -> None:
    """Render Twilio Sandbox onboarding with optional QR image."""
    st.markdown('<p class="sema-panel-label sema-font">Twilio WhatsApp sandbox</p>', unsafe_allow_html=True)
    st.markdown(
        """
To test end-to-end WhatsApp flows, connect your number to your Twilio Sandbox first.
You can either send the join code in WhatsApp or scan the QR code below.
"""
    )
    st.code(f"Send to {_TWILIO_SANDBOX_NUMBER}: {_TWILIO_SANDBOX_JOIN_CODE}")
    st.caption(
        "Note: If Gemini is under high demand, Gemini hits rate limit, or Twilio reaches its daily "
        "message limit, message processing may fail and no WhatsApp reply will be shown."
    )

    project_root = Path(__file__).resolve().parents[3]
    qr_path = project_root / _TWILIO_QR_RELATIVE

    if qr_path.exists():
        try:
            qr_bytes = qr_path.read_bytes()
            if not qr_bytes:
                st.warning("Twilio QR file exists but is empty. Please replace it with a valid PNG image.")
            else:
                qr_b64 = base64.b64encode(qr_bytes).decode("utf-8")
                st.markdown(
                    f"""
<div style="text-align:center; width:100%; margin: 0.35rem 0 0.2rem 0;">
    <img src="data:image/png;base64,{qr_b64}" alt="Twilio Sandbox QR"
         style="width:260px; max-width:100%; display:block; margin:0 auto;" />
    <p style="margin-top:0.45rem; opacity:0.7; font-size:0.9rem;">Twilio Sandbox QR</p>
</div>
""",
                    unsafe_allow_html=True,
                )
        except Exception as exc:
            st.error(f"Unable to load QR image: {exc}")
            st.caption(f"Checked path: {qr_path}")
    else:
        st.caption(
            "QR image not found yet. Add your Twilio QR file at "
            "src/frontend/assets/twilio_sandbox_qr.png to display it here."
        )


def render(api_base: str, _risk_badge):
    st.markdown(
        page_header_compact(
            eyebrow=EYEBROW_TOOLS,
            title="Message Analyser",
            subtitle=(
                "Paste suspicious SMS or WhatsApp text. Gemini evaluates phishing, urgency, "
                "impersonation, and scam patterns common in Malaysia."
            ),
        ),
        unsafe_allow_html=True,
    )

    st.markdown('<p class="sema-panel-label sema-font">Message lab</p>', unsafe_allow_html=True)

    example = st.selectbox("Try an example", list(_EXAMPLE_MESSAGES.keys()))
    prefill = _EXAMPLE_MESSAGES.get(example, "")

    with st.form("message_form"):
        message = st.text_area(
            "Message text",
            value=prefill,
            height=140,
            placeholder="Paste suspicious SMS or WhatsApp content here...",
        )
        sender = st.text_input("Sender (optional)", placeholder="e.g. +6012-3456789")
        submitted = st.form_submit_button("Run Message Scan", use_container_width=True)

    if not submitted:
        _render_twilio_sandbox_qr()
        st.markdown(tools_outro(), unsafe_allow_html=True)
        return

    if not message.strip():
        st.warning("Add message text (or pick an example), then run **Run Message Scan** again.")
        _render_twilio_sandbox_qr()
        st.markdown(tools_outro(), unsafe_allow_html=True)
        return

    payload = {"message": message.strip()}
    if sender.strip():
        payload["sender"] = sender.strip()

    data = None

    with st.spinner("Gemini is profiling the message..."):
        try:
            resp = requests.post(f"{api_base}/analyze-message", json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the API. Is the backend running?")
        except requests.exceptions.Timeout:
            st.warning(
                "System is currently under high demand (or upstream is slow), "
                "so the request timed out. Please retry in a moment."
            )
        except requests.exceptions.HTTPError as e:
            response = e.response
            body = {}
            if response is not None:
                try:
                    body = response.json()
                except Exception:
                    body = {}

            detail = str(body.get("detail", e))
            status_code = response.status_code if response is not None else None
            detail_lower = detail.lower()

            is_high_demand = (
                status_code in {429, 502, 503, 504}
                or "resource exhausted" in detail_lower
                or "rate limit" in detail_lower
                or "quota" in detail_lower
                or "too many requests" in detail_lower
                or "gemini" in detail_lower
            )

            if is_high_demand:
                st.warning(
                    "Gemini is currently experiencing high demand. "
                    "Your system is running, but AI response is temporarily busy. "
                    "Please retry in a moment."
                )
            else:
                st.error(f"API error: {detail}")
        except Exception as e:
            st.error(f"Error: {e}")
    if data is not None:
        st.markdown('<p class="sema-panel-label sema-font">Scan output</p>', unsafe_allow_html=True)

        is_scam = data.get("is_scam", False)
        confidence = data.get("confidence", 0)

        r1, r2, r3 = st.columns([1, 1, 1])

        with r1:
            colour = "#ff4b4b" if is_scam else "#66bb6a"
            label = "SCAM DETECTED" if is_scam else "LIKELY SAFE"
            st.markdown(
                f'<div class="score-box" style="color:{colour}">{label}</div>',
                unsafe_allow_html=True,
            )

        with r2:
            st.metric("Confidence", f"{confidence}%")

        with r3:
            st.metric("Scam Type", data.get("scam_type", "—"))

        st.markdown("</div>", unsafe_allow_html=True)

        st.info(data.get("explanation", "No explanation available."))
        st.success(f"Advice: {data.get('advice', 'Exercise caution.')}")

        if data.get("red_flags"):
            st.markdown('<p class="sema-panel-label sema-font">Red flags</p>', unsafe_allow_html=True)
            for flag in data["red_flags"]:
                st.markdown(f"🚩 {flag}")

        with st.expander("Raw API response"):
            st.json(data)

    _render_twilio_sandbox_qr()

    st.markdown(tools_outro(), unsafe_allow_html=True)
