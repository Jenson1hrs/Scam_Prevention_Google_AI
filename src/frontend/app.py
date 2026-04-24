"""SEMA Fraud Detection Dashboard main Streamlit entry point."""

import os

import streamlit as st

DEFAULT_API_BASE = os.getenv(
    "SEMA_API_BASE_URL",
    "https://sema-api-198988041892.asia-southeast1.run.app",
)

st.set_page_config(
    page_title="SEMA - Scam Prevention",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

    .stApp {
        --sema-accent: #0f766e;
        --sema-accent-soft: #14b8a6;
        --sema-ember: #d97706;
        --sema-danger: #dc2626;
        --sema-ok: #16a34a;
        background:
            radial-gradient(circle at 8% 8%, rgba(20, 184, 166, 0.14), transparent 36%),
            radial-gradient(circle at 92% 12%, rgba(217, 119, 6, 0.12), transparent 28%),
            radial-gradient(circle at 88% 94%, rgba(15, 118, 110, 0.08), transparent 34%);
    }

    .block-container {
        padding-top: 1.35rem;
        padding-bottom: 2rem;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(120, 120, 120, 0.2);
        background: linear-gradient(165deg, rgba(15, 118, 110, 0.08), rgba(217, 119, 6, 0.07));
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        line-height: 1.35;
    }

    .sema-side-brand {
        border: 1px solid rgba(120, 120, 120, 0.25);
        border-radius: 14px;
        padding: 0.82rem 0.82rem 0.86rem;
        background: linear-gradient(145deg, rgba(15, 118, 110, 0.24), rgba(217, 119, 6, 0.18));
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
        margin-bottom: 0.7rem;
    }
    .sema-side-brand h2 {
        margin: 0;
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: -0.01em;
    }
    .sema-side-brand p {
        margin: 0.3rem 0 0 0;
        font-size: 0.78rem;
        opacity: 0.92;
    }

    .sema-side-section {
        margin: 0.8rem 0 0.45rem;
        font-family: "Space Grotesk", sans-serif;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        opacity: 0.62;
    }

    .sema-side-tip {
        margin-top: 0.85rem;
        border: 1px solid rgba(120, 120, 120, 0.24);
        border-radius: 12px;
        padding: 0.66rem 0.68rem;
        background: rgba(255, 255, 255, 0.24);
    }
    .sema-side-tip strong {
        display: block;
        margin-bottom: 0.25rem;
        font-size: 0.72rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-family: "Space Grotesk", sans-serif;
    }
    .sema-side-tip span {
        font-size: 0.78rem;
        line-height: 1.35;
        opacity: 0.92;
        display: block;
    }

    .sema-side-footer {
        margin-top: 0.7rem;
        font-size: 0.68rem;
        opacity: 0.58;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        line-height: 1.35;
    }

    .sema-font,
    .sema-hero,
    .sema-page-header,
    .sema-status-bar,
    .sema-tiles,
    .sema-pipeline,
    .sema-outro,
    .sema-about {
        font-family: "IBM Plex Sans", sans-serif;
    }

    .sema-eyebrow,
    .sema-section-title,
    .sema-outro-eyebrow,
    .sema-panel-label {
        margin: 0 0 0.55rem 0;
        font-size: 0.68rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        font-weight: 700;
        opacity: 0.65;
    }

    .sema-h2,
    .sema-page-title,
    .sema-hero h1,
    .sema-tile h3,
    .sema-about h3 {
        font-family: "Space Grotesk", sans-serif;
        letter-spacing: -0.02em;
    }

    .sema-hero {
        border-radius: 22px;
        padding: 2.05rem 2rem;
        margin-bottom: 1.55rem;
        border: 1px solid rgba(120, 120, 120, 0.25);
        background: linear-gradient(135deg, rgba(15, 118, 110, 0.18), rgba(15, 118, 110, 0.06) 36%, rgba(217, 119, 6, 0.15));
        box-shadow: 0 18px 34px rgba(0, 0, 0, 0.08);
        animation: sema-fade-up 0.55s ease;
    }

    .sema-hero-grid {
        display: grid;
        grid-template-columns: 1.65fr 1fr;
        gap: 1rem;
        align-items: stretch;
    }

    .sema-hero h1 {
        margin: 0 0 0.65rem 0;
        font-size: clamp(1.85rem, 4.2vw, 2.7rem);
        line-height: 1.08;
        font-weight: 700;
    }

    .sema-lead,
    .sema-prose,
    .sema-page-subtitle,
    .sema-tile p,
    .sema-about p,
    .sema-about li {
        font-size: 0.95rem;
        line-height: 1.62;
        opacity: 0.94;
    }

    .sema-hero-panel {
        border-radius: 14px;
        border: 1px solid rgba(120, 120, 120, 0.28);
        background: rgba(255, 255, 255, 0.14);
        padding: 1rem 1.05rem;
        backdrop-filter: blur(3px);
    }
    .sema-hero-panel p {
        margin: 0;
        font-size: 0.72rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        opacity: 0.72;
    }
    .sema-hero-panel h3 {
        margin: 0.35rem 0 0.6rem 0;
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.1rem;
    }
    .sema-hero-panel ul {
        margin: 0;
        padding-left: 1.1rem;
        font-size: 0.87rem;
        line-height: 1.55;
    }

    .sema-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .sema-pill {
        font-size: 0.74rem;
        font-weight: 600;
        border: 1px solid rgba(120, 120, 120, 0.3);
        background: rgba(255, 255, 255, 0.16);
        border-radius: 999px;
        padding: 0.34rem 0.74rem;
    }

    .sema-status-bar {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.75rem;
        margin-bottom: 1.45rem;
    }

    .sema-stat {
        border-radius: 13px;
        padding: 0.95rem 1rem;
        border: 1px solid rgba(120, 120, 120, 0.22);
        background: rgba(255, 255, 255, 0.34);
        text-align: center;
        animation: sema-fade-up 0.5s ease;
    }

    .sema-stat-label {
        font-size: 0.68rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        opacity: 0.67;
        margin-bottom: 0.3rem;
    }

    .sema-stat-value {
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.08rem;
        font-weight: 700;
    }

    .sema-stat-value--ok { color: var(--sema-ok); }
    .sema-stat-value--warn { color: var(--sema-ember); }
    .sema-stat-value--bad { color: var(--sema-danger); }

    .sema-section-title { margin-top: 1.85rem; }
    .sema-h2 {
        margin: 0 0 0.75rem 0;
        font-size: 1.42rem;
        font-weight: 700;
        line-height: 1.2;
    }

    .sema-page-header {
        border-radius: 18px;
        padding: 1.3rem 1.35rem 1.2rem;
        margin-bottom: 1.25rem;
        border: 1px solid rgba(120, 120, 120, 0.24);
        background: linear-gradient(140deg, rgba(15, 118, 110, 0.14), rgba(217, 119, 6, 0.13));
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.06);
        animation: sema-fade-up 0.48s ease;
    }

    .sema-page-title {
        margin: 0 0 0.35rem 0;
        font-size: 1.6rem;
        font-weight: 700;
        line-height: 1.18;
    }

    .sema-page-subtitle {
        margin: 0;
        max-width: 43rem;
    }

    .sema-mini-tags {
        margin-top: 0.7rem;
        display: flex;
        flex-wrap: wrap;
        gap: 0.35rem;
    }
    .sema-mini-tags span {
        border: 1px solid rgba(120, 120, 120, 0.25);
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 0.22rem 0.58rem;
        background: rgba(255, 255, 255, 0.18);
    }

    .sema-tiles {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.95rem;
    }

    .sema-tile {
        border-radius: 15px;
        padding: 1.2rem 1.2rem 1.25rem;
        border: 1px solid rgba(120, 120, 120, 0.22);
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.28), rgba(255, 255, 255, 0.14));
        transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
        animation: sema-fade-up 0.54s ease;
    }
    .sema-tile:hover {
        transform: translateY(-2px);
        border-color: rgba(15, 118, 110, 0.5);
        box-shadow: 0 10px 18px rgba(15, 118, 110, 0.12);
    }
    .sema-tile-icon {
        display: inline-block;
        margin-bottom: 0.55rem;
        border-radius: 999px;
        font-family: "Space Grotesk", sans-serif;
        font-size: 0.7rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-weight: 700;
        padding: 0.35rem 0.62rem;
        color: #ffffff;
        background: linear-gradient(120deg, var(--sema-accent), var(--sema-accent-soft));
    }
    .sema-tile h3 {
        margin: 0 0 0.42rem 0;
        font-size: 1.1rem;
    }
    .sema-tile p { margin: 0; }
    .sema-tile-cta {
        display: inline-block;
        margin-top: 0.82rem;
        font-size: 0.8rem;
        font-weight: 700;
        color: var(--sema-accent);
    }

    .sema-pipeline {
        border-radius: 15px;
        padding: 1.25rem 1.1rem 1.35rem;
        margin-top: 0.55rem;
        border: 1px solid rgba(120, 120, 120, 0.2);
        background: rgba(255, 255, 255, 0.22);
    }

    .sema-pipe-step {
        text-align: center;
        margin: 0 auto;
        max-width: 44rem;
    }

    .sema-pipe-node {
        display: inline-block;
        border-radius: 10px;
        border: 1px solid rgba(120, 120, 120, 0.24);
        padding: 0.56rem 1.02rem;
        font-size: 0.86rem;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.35);
    }
    .sema-pipe-node--in {
        border-color: rgba(15, 118, 110, 0.48);
        background: rgba(15, 118, 110, 0.16);
    }
    .sema-pipe-node--orch {
        border-color: rgba(217, 119, 6, 0.48);
        background: rgba(217, 119, 6, 0.14);
    }
    .sema-pipe-node--out {
        border-color: rgba(22, 163, 74, 0.48);
        background: rgba(22, 163, 74, 0.14);
    }

    .sema-pipe-chevron {
        text-align: center;
        font-family: "Space Grotesk", sans-serif;
        font-size: 0.76rem;
        letter-spacing: 0.22em;
        opacity: 0.6;
        margin: 0.46rem 0;
    }

    .sema-pipe-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.65rem;
    }

    .sema-pipe-agent {
        border-radius: 11px;
        padding: 0.92rem 0.75rem;
        text-align: center;
        border: 1px solid rgba(120, 120, 120, 0.23);
        background: rgba(255, 255, 255, 0.3);
    }
    .sema-pipe-agent--ml { border-top: 4px solid #0ea5e9; }
    .sema-pipe-agent--pat { border-top: 4px solid #f59e0b; }
    .sema-pipe-agent--ctx { border-top: 4px solid #0f766e; }
    .sema-pipe-agent strong {
        display: block;
        margin-bottom: 0.24rem;
        font-family: "Space Grotesk", sans-serif;
        font-size: 0.93rem;
    }
    .sema-pipe-agent span {
        font-size: 0.81rem;
        line-height: 1.4;
        opacity: 0.86;
    }

    .sema-outro {
        border-radius: 13px;
        border: 1px solid rgba(120, 120, 120, 0.23);
        background: rgba(255, 255, 255, 0.3);
        margin-top: 1.7rem;
        padding: 1.05rem 1.1rem;
    }
    .sema-outro--compact {
        margin-top: 1.25rem;
        padding: 0.9rem 1rem;
    }
    .sema-outro-text {
        margin: 0 0 0.4rem 0;
        font-size: 0.9rem;
        line-height: 1.55;
    }
    .sema-outro-text--compact { margin: 0; font-size: 0.86rem; }
    .sema-outro-meta {
        margin: 0;
        font-size: 0.74rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-weight: 700;
        opacity: 0.62;
    }

    .sema-about h3.sema-h2 { margin-top: 1.45rem; }
    .sema-about h3.sema-h2:first-child { margin-top: 0; }
    .sema-about ul {
        margin: 0.28rem 0 0.82rem 0;
        padding-left: 1.12rem;
    }
    .sema-about li { margin-bottom: 0.34rem; }
    .sema-about blockquote {
        margin: 0.75rem 0;
        border-left: 4px solid var(--sema-accent);
        border-radius: 0 8px 8px 0;
        padding: 0.82rem 0.95rem;
        background: rgba(15, 118, 110, 0.08);
        line-height: 1.55;
    }
    .sema-table-wrap {
        overflow-x: auto;
        margin: 0.52rem 0 0.95rem 0;
    }
    .sema-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.87rem;
    }
    .sema-table th,
    .sema-table td {
        border: 1px solid rgba(120, 120, 120, 0.26);
        padding: 0.52rem 0.62rem;
        text-align: left;
        vertical-align: top;
    }
    .sema-table th {
        font-size: 0.66rem;
        letter-spacing: 0.09em;
        text-transform: uppercase;
        font-weight: 700;
        opacity: 0.76;
        background: rgba(15, 118, 110, 0.1);
    }

    .score-box {
        font-family: "Space Grotesk", sans-serif;
        font-size: 2.65rem;
        font-weight: 700;
        text-align: center;
        padding: 0.2rem 0;
    }

    .risk-high,
    .risk-medium,
    .risk-low {
        color: #ffffff;
        border-radius: 999px;
        padding: 0.35rem 0.8rem;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        display: inline-block;
    }
    .risk-high { background: linear-gradient(120deg, #ef4444, #dc2626); }
    .risk-medium { background: linear-gradient(120deg, #f59e0b, #d97706); }
    .risk-low { background: linear-gradient(120deg, #22c55e, #16a34a); }

    @keyframes sema-fade-up {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @media (max-width: 900px) {
        .sema-hero-grid { grid-template-columns: 1fr; }
        .sema-status-bar { grid-template-columns: 1fr; }
        .sema-tiles { grid-template-columns: 1fr; }
        .sema-pipe-grid { grid-template-columns: 1fr; }
    }
</style>
""",
    unsafe_allow_html=True,
)


def risk_badge(level: str) -> str:
    css_class = f"risk-{level.lower()}"
    return f'<span class="{css_class}">{level} RISK</span>'


st.sidebar.image(
    "https://fonts.gstatic.com/s/i/productlogos/googleg/v6/24px.svg",
    width=24,
)
st.sidebar.markdown(
    """
<div class="sema-side-brand">
    <h2>SEMA Console</h2>
    <p>Scam Explainer and Mitigation Agent</p>
</div>
""",
    unsafe_allow_html=True,
)

st.sidebar.markdown('<p class="sema-side-section">Navigation</p>', unsafe_allow_html=True)

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "💳 Transaction Scanner", "💬 Message Analyser", "ℹ️ About"],
    label_visibility="collapsed",
)

st.sidebar.markdown('<p class="sema-side-section">Backend</p>', unsafe_allow_html=True)

api_base = st.sidebar.text_input(
    "API URL",
    value=DEFAULT_API_BASE,
    help="Base URL for the SEMA FastAPI backend",
)

st.sidebar.markdown(
    """
<div class="sema-side-tip">
    <strong>Quick tip</strong>
    <span>Use Transaction Scanner for structured risk and Message Analyser for suspicious chat or SMS text.</span>
</div>
<p class="sema-side-footer">Project 2030 · Track 5 Secure Digital</p>
""",
    unsafe_allow_html=True,
)

if page == "🏠 Home":
    from src.frontend._pages.home import render

    render(api_base, risk_badge)

elif page == "💳 Transaction Scanner":
    from src.frontend._pages.transaction_scanner import render

    render(api_base, risk_badge)

elif page == "💬 Message Analyser":
    from src.frontend._pages.message_analyser import render

    render(api_base, risk_badge)

elif page == "ℹ️ About":
    from src.frontend._pages.about import render

    render()
