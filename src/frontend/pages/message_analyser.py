"""Message Analyser page — paste SMS / WhatsApp text for scam detection."""

import streamlit as st
import requests


_EXAMPLE_MESSAGES = {
    "(select an example)": "",
    "Maybank phishing": "Your Maybank account has been locked due to suspicious activity. Click here to verify: http://maybank-secure-login.xyz",
    "LHDN tax scam": "PERINGATAN: Anda mempunyai tunggakan cukai sebanyak RM12,500. Hubungi 03-8765 4321 segera untuk mengelakkan waran tangkap.",
    "Prize scam": "Tahniah! Anda telah memenangi RM50,000 daripada Shopee Lucky Draw. Hantar RM200 yuran pemprosesan ke 012-3456789.",
    "Parcel scam": "Your parcel from J&T Express is held at customs. Pay RM89 clearance fee here: http://jnt-clearance.co/pay",
    "Job scam": "Hi! We saw your resume on JobStreet. Work from home, earn RM300/day! Just pay RM150 registration fee. WhatsApp 011-2233445.",
    "Legitimate bank SMS": "Your CIMB Clicks transfer of RM150.00 to ALI BIN ABU was successful on 17/04/2026 at 14:32.",
}


def render(api_base: str, risk_badge):
    st.title("💬 Message Analyser")
    st.caption("Paste a suspicious SMS or WhatsApp message to check for scam patterns.")

    example = st.selectbox("Try an example", list(_EXAMPLE_MESSAGES.keys()))
    prefill = _EXAMPLE_MESSAGES.get(example, "")

    with st.form("message_form"):
        message = st.text_area(
            "Message text",
            value=prefill,
            height=120,
            placeholder="Paste the suspicious message here...",
        )
        sender = st.text_input("Sender (optional)", placeholder="e.g. +6012-3456789")
        submitted = st.form_submit_button("Analyse Message", use_container_width=True)

    if not submitted or not message.strip():
        return

    payload = {"message": message.strip()}
    if sender.strip():
        payload["sender"] = sender.strip()

    with st.spinner("Gemini is analysing the message..."):
        try:
            resp = requests.post(f"{api_base}/analyze-message", json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the API. Is the backend running?")
            return
        except requests.exceptions.HTTPError as e:
            body = e.response.json() if e.response else {}
            st.error(f"API error: {body.get('detail', e)}")
            return
        except Exception as e:
            st.error(f"Error: {e}")
            return

    # ── Results ────────────────────────────────────────────────
    st.divider()
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

    # Explanation
    st.info(data.get("explanation", "No explanation available."))

    # Advice
    st.success(f"**Advice:** {data.get('advice', 'Exercise caution.')}")

    # Red flags
    if data.get("red_flags"):
        st.subheader("Red Flags")
        for flag in data["red_flags"]:
            st.markdown(f"🚩 {flag}")

    with st.expander("Raw API response"):
        st.json(data)
