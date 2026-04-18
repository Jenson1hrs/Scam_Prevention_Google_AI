# SEMA — Scam Explainer & Mitigation Agent

> **Track 5: Secure Digital (FinTech & Security)**  
> PROJECT 2030 — MyAI Future Hackathon by GDG On Campus UTM

SEMA is an AI-powered fraud prevention system that protects Malaysian
citizens from financial scams. It combines a trained **XGBoost ML model**
with **Google Gemini** reasoning through a **multi-agent architecture** to
deliver explainable, actionable risk assessments in real time.

---

## Problem Statement

Digital fraud costs Malaysian citizens **millions of ringgit** annually.
Scam types are increasingly sophisticated — Macau scams, love scams,
LHDN tax impersonation, parcel scams, e-wallet phishing, and job scams
all exploit urgency and trust. Existing rule-based fraud systems cannot
keep up with the pace and creativity of these threats.

SEMA addresses this by moving from simple "block or allow" rules to a
**multi-agent AI pipeline** that *explains* why a transaction is
suspicious and *classifies* it against known Malaysian scam patterns.

---

## Features

- **Transaction Fraud Detection** — submit a financial transaction and
  receive a risk score from a three-agent pipeline (ML + Pattern + Context)
- **Scam Message Analysis** — paste an SMS or WhatsApp message to detect
  phishing, impersonation, and social engineering tactics
- **Explainable AI** — SHAP feature importance explains which factors
  drove the ML prediction; Gemini provides natural-language reasoning
- **Malaysian Context** — prompts and classifications are grounded in
  real Malaysian scam typologies (Macau scam, LHDN, parcel, e-wallet, etc.)
- **Modern Dashboard** — Streamlit-based UI with Transaction Scanner,
  Message Analyser, and architecture overview

---

## Architecture

```
┌──────────────┐
│  Transaction  │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌───────────────────┐     ┌──────────────────┐
│   ML Agent   │     │  Pattern Agent    │     │  Context Agent   │
│  (XGBoost)   │     │  (Gemini — scam   │     │  (Gemini — time, │
│  + SHAP      │     │   typologies)     │     │   device, amount)│
└──────┬───────┘     └────────┬──────────┘     └────────┬─────────┘
       │                      │                         │
       └──────────┬───────────┘─────────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │  Orchestrator  │
         │  70% ML + 30%  │
         │  Gemini blend  │
         └───────┬────────┘
                 │
                 ▼
         ┌────────────────┐
         │  Final Verdict │
         │  + Explanation │
         └────────────────┘
```

### Agents

| Agent | Role | Technology |
|-------|------|------------|
| **ML Agent** | Base fraud probability from transaction features | XGBoost pipeline + SHAP explainability |
| **Pattern Agent** | Classifies against 9 Malaysian scam typologies | Google Gemini 2.0 Flash |
| **Context Agent** | Evaluates behavioural signals (timing, device, amount) | Google Gemini 2.0 Flash |
| **Orchestrator** | Runs agents in parallel, blends scores | Python asyncio |
| **Message Agent** | Scam detection in SMS/WhatsApp text | Google Gemini 2.0 Flash |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI / Intelligence | Google Gemini 2.0 Flash via `google-genai` SDK |
| ML Model | XGBoost + scikit-learn + SMOTE |
| Explainability | SHAP (TreeExplainer) |
| Backend API | FastAPI (Python 3.10+) |
| Frontend | Streamlit |
| Deployment | Docker → Google Cloud Run |

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- A Google AI Studio API key ([get one here](https://aistudio.google.com/apikey))

### 1. Clone & install

```bash
git clone https://github.com/<your-username>/Scam_Prevention_Google_AI.git
cd Scam_Prevention_Google_AI
pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_google_ai_studio_api_key
```

### 3. Train the ML model (optional)

Download the [Kaggle Credit Card Fraud dataset](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
and place `creditcard.csv` in `data/raw/`, then run:

```bash
python scripts/train_model.py
```

This creates `models/fraud_pipeline.joblib`. If skipped, the API uses
rule-based fallback scoring.

### 4. Run the API

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

API docs at: http://localhost:8000/docs

### 5. Run the dashboard

```bash
streamlit run src/frontend/app.py
```

Dashboard at: http://localhost:8501

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service info and agent status |
| GET | `/health` | Health check |
| POST | `/predict` | Multi-agent transaction fraud analysis |
| POST | `/analyze-message` | Scam message detection |

### Example: Transaction prediction

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"amount": 5000, "transaction_type": "transfer", "is_new_device": 1, "is_night": 1}'
```

### Example: Message analysis

```bash
curl -X POST http://localhost:8000/analyze-message \
  -H "Content-Type: application/json" \
  -d '{"message": "Your Maybank account has been locked. Click here: http://fake.com"}'
```

---

## Docker

```bash
docker build -t sema-api .
docker run -p 8080:8080 -e GEMINI_API_KEY=your_key sema-api
```

---

## Cloud Run Deployment

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/sema-api

# Deploy
gcloud run deploy sema-api \
  --image gcr.io/PROJECT_ID/sema-api \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-secrets=GEMINI_API_KEY=gemini-api-key:latest
```

---

## Project Structure

```
├── config/
│   └── settings.py          # Environment config, model paths, thresholds
├── src/
│   ├── main.py              # FastAPI app with /predict and /analyze-message
│   ├── gemini_agent.py      # Gemini API wrapper for fraud analysis
│   ├── explainer.py         # SHAP explainability module
│   ├── utils.py             # Utility functions
│   ├── agents/
│   │   ├── orchestrator.py  # Multi-agent coordination
│   │   ├── ml_agent.py      # XGBoost prediction + SHAP
│   │   ├── pattern_agent.py # Gemini scam pattern classification
│   │   └── context_agent.py # Gemini behavioural context analysis
│   └── frontend/
│       ├── app.py           # Streamlit dashboard entry point
│       └── pages/
│           ├── home.py              # Dashboard overview
│           ├── transaction_scanner.py  # Transaction analysis UI
│           ├── message_analyser.py     # Scam message detection UI
│           └── about.py               # Architecture & info
├── scripts/
│   ├── train_model.py       # Model training script
│   └── generate_synthetic_messages.py
├── notebooks/
│   └── 01_data_exploration.ipynb
├── tests/
│   └── test_main.py
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## AI Tools Disclosure

As required by hackathon rules (Section 4.2), the following AI tools were
used during development:

- **Google Gemini** — core AI integration for fraud analysis and scam detection
- **GitHub Copilot / Cursor AI** — assisted with code generation and debugging

All team members can explain and defend every part of the codebase.

---

## License

MIT
