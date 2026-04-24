"""Home page for the redesigned SEMA frontend."""

from __future__ import annotations

import streamlit as st
import requests

from src.frontend._pages._layout import home_outro


def _stat_class(ok: bool, warn: bool = False) -> str:
    if ok:
        return "sema-stat-value--ok"
    if warn:
        return "sema-stat-value--warn"
    return "sema-stat-value--bad"


def render(api_base: str, _risk_badge) -> None:
    try:
        resp = requests.get(f"{api_base}/health", timeout=5)
        health = resp.json()
        ml_ok = bool(health.get("ml_model_loaded", False))
        gemini_ok = bool(health.get("gemini_available", False))
    except Exception:
        ml_ok = False
        gemini_ok = False

    api_online = ml_ok or gemini_ok

    api_label = "Online" if api_online else "Offline"
    ml_label = "Ready" if ml_ok else "Fallback"
    gem_label = "Live" if gemini_ok else "Down"

    api_cls = _stat_class(api_online)
    ml_cls = _stat_class(ml_ok, warn=not ml_ok)
    gem_cls = _stat_class(gemini_ok)

    st.markdown(
        f"""
<section class="sema-hero sema-font" aria-label="SEMA introduction">
    <div class="sema-hero-grid">
        <div>
            <p class="sema-eyebrow">PROJECT 2030 · TRACK 5 · SECURE DIGITAL</p>
            <h1>Designing trust for high-speed scam defence.</h1>
            <p class="sema-lead">
                <strong>SEMA</strong> fuses an ML baseline with Gemini reasoning to produce
                one clear answer: <strong>how risky this event is</strong>, <strong>why</strong>, and
                <strong>what to do next</strong>.
            </p>
            <div class="sema-pills" aria-hidden="true">
                <span class="sema-pill">Fraud Intelligence</span>
                <span class="sema-pill">Explainability First</span>
                <span class="sema-pill">Live Inference</span>
                <span class="sema-pill">Malaysia Scam Patterns</span>
            </div>
        </div>
        <div class="sema-hero-panel" aria-label="System snapshot">
            <p>System Snapshot</p>
            <h3>Realtime Risk Studio</h3>
            <ul>
                <li>Transaction + message workflows</li>
                <li>Score blending with transparent weights</li>
                <li>Actionable mitigations in plain language</li>
            </ul>
        </div>
    </div>
</section>

<div class="sema-status-bar sema-font" role="group" aria-label="Service status">
    <div class="sema-stat">
        <div class="sema-stat-label">API Link</div>
        <div class="sema-stat-value {api_cls}">{api_label}</div>
    </div>
    <div class="sema-stat">
        <div class="sema-stat-label">ML Engine</div>
        <div class="sema-stat-value {ml_cls}">{ml_label}</div>
    </div>
    <div class="sema-stat">
        <div class="sema-stat-label">Gemini Reasoner</div>
        <div class="sema-stat-value {gem_cls}">{gem_label}</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    if not api_online:
        st.warning(
            "Cannot reach the backend at the **API URL** in the sidebar. "
            "Start FastAPI (`uvicorn src.main:app --port 8000`) or paste your Cloud Run URL."
        )

    st.markdown(
        """
<div class="sema-font">
<p class="sema-section-title">Workflows</p>
<h2 class="sema-h2">Choose your threat surface</h2>
<div class="sema-tiles">
    <div class="sema-tile">
        <div class="sema-tile-icon">CARD</div>
        <h3>Transaction Scanner</h3>
        <p>
            Inspect amount, behavior flags, and transaction context through ML + reasoning.
            Receive a risk level with analyst-style explanation.
        </p>
        <span class="sema-tile-cta">Open in sidebar -> Transaction Scanner</span>
    </div>
    <div class="sema-tile">
        <div class="sema-tile-icon">TEXT</div>
        <h3>Message Analyser</h3>
        <p>
            Analyze suspicious SMS or WhatsApp content for urgency, phishing links,
            impersonation, and known local scam signatures.
        </p>
        <span class="sema-tile-cta">Open in sidebar -> Message Analyser</span>
    </div>
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="sema-font">
<p class="sema-section-title">Decision Engine</p>
<h2 class="sema-h2">From input signal to trusted verdict</h2>
<p class="sema-prose">
    SEMA is built as a parallel agent fabric. Every verdict is traceable and explainable.
</p>
<div class="sema-pipeline" aria-label="Architecture pipeline">
    <div class="sema-pipe-step">
        <span class="sema-pipe-node sema-pipe-node--in">Incoming transaction or message</span>
    </div>
    <div class="sema-pipe-chevron">01</div>
    <div class="sema-pipe-grid">
        <div class="sema-pipe-agent sema-pipe-agent--ml">
            <strong>ML Agent</strong>
            <span>Scores numerical behavior with XGBoost and explainability signals.</span>
        </div>
        <div class="sema-pipe-agent sema-pipe-agent--pat">
            <strong>Pattern Agent</strong>
            <span>Recognizes scam archetypes, intent cues, and linguistic pressure.</span>
        </div>
        <div class="sema-pipe-agent sema-pipe-agent--ctx">
            <strong>Context Agent</strong>
            <span>Evaluates timing, novelty, and interaction risk in surrounding context.</span>
        </div>
    </div>
    <div class="sema-pipe-chevron">02</div>
    <div class="sema-pipe-step">
        <span class="sema-pipe-node sema-pipe-node--orch">Orchestrator blends weighted signals into one confidence-calibrated score</span>
    </div>
    <div class="sema-pipe-chevron">03</div>
    <div class="sema-pipe-step">
        <span class="sema-pipe-node sema-pipe-node--out">Risk band + explanation + mitigation plan</span>
    </div>
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.expander("Why SEMA exists — in one glance"):
        st.markdown(
            """
Malaysian users face fast-evolving scams that imitate banks, agencies, couriers, and employers.
Rule-only blockers miss context and language tricks.

SEMA pairs statistical fraud learning with LLM reasoning so analysts and non-technical users
can understand both the score and the rationale behind it.

For message-only checks, Gemini focuses on phishing markers, authority impersonation,
urgency pressure, and payment extraction patterns.
"""
        )

    st.markdown(home_outro(), unsafe_allow_html=True)
