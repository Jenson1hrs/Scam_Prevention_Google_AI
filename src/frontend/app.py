"""SEMA Fraud Detection Dashboard — main Streamlit entry point."""

import streamlit as st

# ── Page configuration (must be first Streamlit call) ──────────────────
st.set_page_config(
    page_title="SEMA — Scam Prevention",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Global */
    .block-container { padding-top: 1.5rem; }

    /* Risk badges */
    .risk-high   { background: #ff4b4b; color: white; padding: 6px 18px;
                   border-radius: 20px; font-weight: 700; display: inline-block; }
    .risk-medium { background: #ffa726; color: white; padding: 6px 18px;
                   border-radius: 20px; font-weight: 700; display: inline-block; }
    .risk-low    { background: #66bb6a; color: white; padding: 6px 18px;
                   border-radius: 20px; font-weight: 700; display: inline-block; }

    /* Score display */
    .score-box   { font-size: 3rem; font-weight: 800; text-align: center;
                   padding: 0.3em 0; }

    /* Cards */
    .info-card   { background: #f8f9fa; border-radius: 12px; padding: 1.2rem;
                   margin-bottom: 1rem; border-left: 4px solid #1a73e8; }
</style>
""", unsafe_allow_html=True)


def risk_badge(level: str) -> str:
    css_class = f"risk-{level.lower()}"
    return f'<span class="{css_class}">{level} RISK</span>'


# ── Sidebar navigation ────────────────────────────────────────────────
st.sidebar.image(
    "https://fonts.gstatic.com/s/i/productlogos/googleg/v6/24px.svg",
    width=32,
)
st.sidebar.title("SEMA")
st.sidebar.caption("Scam Explainer & Mitigation Agent")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "💳 Transaction Scanner", "💬 Message Analyser", "ℹ️ About"],
    label_visibility="collapsed",
)

API_BASE = st.sidebar.text_input(
    "API URL",
    value="http://localhost:8000",
    help="Base URL of the SEMA FastAPI backend",
)

# ── Page router ────────────────────────────────────────────────────────

if page == "🏠 Home":
    from src.frontend.pages.home import render
    render(API_BASE, risk_badge)

elif page == "💳 Transaction Scanner":
    from src.frontend.pages.transaction_scanner import render
    render(API_BASE, risk_badge)

elif page == "💬 Message Analyser":
    from src.frontend.pages.message_analyser import render
    render(API_BASE, risk_badge)

elif page == "ℹ️ About":
    from src.frontend.pages.about import render
    render()
