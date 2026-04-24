"""Home / Dashboard page."""

import streamlit as st
import requests


def render(api_base: str, risk_badge):
    st.title("🛡️ SEMA Dashboard")
    st.markdown(
        "**S**cam **E**xplainer & **M**itigation **A**gent — "
        "Protecting Malaysian citizens from financial fraud using AI."
    )

    # Health check
    col1, col2, col3 = st.columns(3)

    try:
        resp = requests.get(f"{api_base}/health", timeout=5)
        health = resp.json()
        ml_ok = health.get("ml_model_loaded", False)
        gemini_ok = health.get("gemini_available", False)
    except Exception:
        ml_ok = False
        gemini_ok = False

    with col1:
        st.metric("API Status", "Online" if ml_ok or gemini_ok else "Offline")
    with col2:
        st.metric("ML Model", "Loaded" if ml_ok else "Not loaded")
    with col3:
        st.metric("Gemini AI", "Connected" if gemini_ok else "Unavailable")

    st.divider()

    # Quick-start cards
    left, right = st.columns(2)

    with left:
        st.markdown("""
<div class="info-card">
    <h4>💳 Transaction Scanner</h4>
    <p>Submit a financial transaction for real-time fraud analysis.
    Our multi-agent pipeline combines ML prediction with Gemini
    reasoning to provide explainable risk scores.</p>
</div>
""", unsafe_allow_html=True)

    with right:
        st.markdown("""
<div class="info-card">
    <h4>💬 Message Analyser</h4>
    <p>Paste a suspicious SMS or WhatsApp message. SEMA uses Gemini AI
    to detect phishing, impersonation, and social-engineering tactics
    commonly targeting Malaysian citizens.</p>
</div>
""", unsafe_allow_html=True)

    st.divider()

    # Architecture preview
    st.subheader("Multi-Agent Architecture")
    st.markdown("""
```
┌──────────────┐
│  Transaction  │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌───────────────────┐     ┌──────────────────┐
│   ML Agent   │     │  Pattern Agent    │     │  Context Agent   │
│  (XGBoost)   │     │  (Gemini — scam   │     │  (Gemini — time, │
│              │     │   typologies)     │     │   device, amount)│
└──────┬───────┘     └────────┬──────────┘     └────────┬─────────┘
       │                      │                         │
       └──────────┬───────────┘─────────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │  Orchestrator  │
         │  (score blend) │
         └───────┬────────┘
                 │
                 ▼
         ┌────────────────┐
         │  Final Verdict │
         └────────────────┘
```
""")
