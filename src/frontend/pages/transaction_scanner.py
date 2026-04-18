"""Transaction Scanner page — submit a transaction for multi-agent fraud analysis."""

import streamlit as st
import requests
import json


def render(api_base: str, risk_badge):
    st.title("💳 Transaction Scanner")
    st.caption("Analyse a financial transaction through the SEMA multi-agent pipeline.")

    with st.form("transaction_form"):
        col1, col2 = st.columns(2)

        with col1:
            amount = st.number_input(
                "Amount (RM)", min_value=0.01, value=500.00, step=50.0,
            )
            transaction_type = st.selectbox(
                "Transaction Type",
                ["online", "pos", "atm", "transfer"],
            )

        with col2:
            is_new_device = st.toggle("New / unknown device", value=False)
            is_night = st.toggle("Late-night (10 PM – 5 AM)", value=False)
            is_small_amount = st.toggle("Small amount (< RM 100)", value=False)
            is_round_amount = st.toggle("Round amount", value=False)

        submitted = st.form_submit_button("Analyse Transaction", use_container_width=True)

    if not submitted:
        return

    payload = {
        "amount": amount,
        "transaction_type": transaction_type,
        "is_new_device": int(is_new_device),
        "is_night": int(is_night),
        "is_small_amount": int(is_small_amount),
        "is_round_amount": int(is_round_amount),
    }

    with st.spinner("Running multi-agent analysis..."):
        try:
            resp = requests.post(f"{api_base}/predict", json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the API. Is the backend running?")
            return
        except Exception as e:
            st.error(f"API error: {e}")
            return

    # ── Results ────────────────────────────────────────────────
    st.divider()
    risk_level = data.get("risk_level", "LOW")

    # Top row: score + badge
    r1, r2, r3 = st.columns([1, 1, 1])

    with r1:
        colour = {"HIGH": "#ff4b4b", "MEDIUM": "#ffa726", "LOW": "#66bb6a"}.get(risk_level, "#999")
        st.markdown(
            f'<div class="score-box" style="color:{colour}">{data["risk_score"]}%</div>',
            unsafe_allow_html=True,
        )
        st.markdown(f"<div style='text-align:center'>{risk_badge(risk_level)}</div>", unsafe_allow_html=True)

    with r2:
        st.metric("ML Score", f'{data.get("ml_risk_score", "—")}%')
        st.metric("Gemini Score", f'{data.get("gemini_risk_score", "—")}%')

    with r3:
        st.metric("Analysis Mode", data.get("analysis_mode", "—"))
        st.metric("Action", (data.get("recommended_action") or "—").upper())

    # Explanation
    if data.get("explanation"):
        st.info(data["explanation"])

    # Details expander
    with st.expander("Full agent breakdown", expanded=False):
        detail_cols = st.columns(2)

        with detail_cols[0]:
            st.markdown("**Pattern Agent**")
            st.write(f"Score: {data.get('pattern_risk_score', '—')}")
            st.write(f"Scam type: {data.get('scam_type', '—')}")
            if data.get("matched_patterns"):
                st.write("Matched patterns:")
                for p in data["matched_patterns"]:
                    st.markdown(f"- {p}")

        with detail_cols[1]:
            st.markdown("**Context Agent**")
            st.write(f"Score: {data.get('context_risk_score', '—')}")
            if data.get("suspicious_signals"):
                st.write("Suspicious signals:")
                for s in data["suspicious_signals"]:
                    st.markdown(f"- {s}")

    with st.expander("Raw API response"):
        st.json(data)
