"""About page — architecture, tech stack, and project information."""

import streamlit as st


def render():
    st.title("ℹ️ About SEMA")

    st.markdown("""
**SEMA** (Scam Explainer & Mitigation Agent) is an AI-powered fraud
prevention system designed to protect Malaysian citizens from financial
scams. It combines traditional machine learning with Google Gemini
reasoning to provide *explainable*, *actionable* risk assessments.

---

### The Problem

Digital fraud costs Malaysian citizens **millions of ringgit** annually.
Common scam types include:
- **Macau Scam** — impersonation of police or court officials
- **Love/Romance Scam** — emotional manipulation for money transfers
- **LHDN Tax Scam** — fake tax authority with arrest threats
- **Parcel Scam** — fake customs fees for non-existent packages
- **E-wallet Phishing** — fake Touch 'n Go / GrabPay alerts

---

### Multi-Agent Architecture

SEMA uses a **three-agent pipeline** orchestrated together:

| Agent | Role | Technology |
|-------|------|------------|
| **ML Agent** | Base risk probability from transaction features | XGBoost (trained on credit card fraud data) |
| **Pattern Agent** | Classifies against Malaysian scam typologies | Google Gemini |
| **Context Agent** | Evaluates behavioural signals (timing, device, amount) | Google Gemini |
| **Orchestrator** | Blends scores with configurable weights | Python (70% ML + 30% Gemini) |

For **message analysis**, a dedicated Gemini agent scans SMS/WhatsApp
text for phishing links, urgency tactics, impersonation, and other
red flags specific to Malaysian scams.

---

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI / Intelligence** | Google Gemini 2.0 Flash via `google-genai` SDK |
| **ML Model** | XGBoost + scikit-learn pipeline |
| **Backend API** | FastAPI (Python) |
| **Frontend** | Streamlit |
| **Deployment** | Docker → Google Cloud Run |
| **Explainability** | SHAP (SHapley Additive exPlanations) |

---

### Track Alignment

**PROJECT 2030 — Track 5: Secure Digital (FinTech & Security)**

> *"Digital fraud and sophisticated scams result in millions of ringgit
> in losses for Malaysian citizens annually. Building a resilient digital
> economy requires advanced, real-time protection layers that can outpace
> increasingly automated threats."*

SEMA directly addresses this challenge by providing an intelligent,
multi-layered fraud detection system that moves beyond simple rule-based
blocking to AI-driven, explainable decisions.

---

### Team

Built for the **MyAI Future Hackathon** by GDG On Campus UTM.

*AI tools (Gemini, GitHub Copilot) were used during development and are
disclosed per hackathon rules Section 4.2.*
""")
