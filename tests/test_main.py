"""Tests for the SEMA FastAPI application."""

import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture(scope="module")
def client():
    """Create a test client with lifespan events (agents initialised)."""
    with TestClient(app) as c:
        yield c


# ── Basic endpoints ───────────────────────────────────────────────────

def test_root_endpoint(client):
    response = client.get("/")
    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "running"
    assert "agents" in data
    assert "endpoints" in data


def test_health_check(client):
    response = client.get("/health")
    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "healthy"
    assert "ml_model_loaded" in data
    assert "gemini_available" in data


# ── /predict endpoint ─────────────────────────────────────────────────

def test_predict_minimal(client):
    """Predict with only required field (amount)."""
    response = client.post("/predict", json={"amount": 250.0})
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "ml_risk_score" in data
    assert data["risk_level"] in ("LOW", "MEDIUM", "HIGH")
    assert data["analysis_mode"] in ("multi_agent", "ml_only", "fallback")


def test_predict_high_risk_indicators(client):
    """Transaction with multiple risk indicators."""
    response = client.post("/predict", json={
        "amount": 9500.0,
        "transaction_type": "transfer",
        "is_new_device": 1,
        "is_night": 1,
        "is_small_amount": 0,
        "is_round_amount": 0,
    })
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["risk_score"] <= 100


def test_predict_low_risk(client):
    """Normal-looking daytime purchase."""
    response = client.post("/predict", json={
        "amount": 45.90,
        "transaction_type": "pos",
        "is_new_device": 0,
        "is_night": 0,
        "is_small_amount": 1,
        "is_round_amount": 0,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] <= 100


def test_predict_invalid_amount(client):
    """Amount must be > 0."""
    response = client.post("/predict", json={"amount": -100})
    assert response.status_code == 422


def test_predict_missing_amount(client):
    """Amount is required."""
    response = client.post("/predict", json={"transaction_type": "online"})
    assert response.status_code == 422


# ── /analyze-message endpoint ─────────────────────────────────────────

def test_analyze_message_no_gemini(client):
    """Without a valid Gemini key expect 503; with one expect 200 or transient 502."""
    response = client.post("/analyze-message", json={
        "message": "You won RM10,000! Send RM500 to claim.",
    })
    assert response.status_code in (200, 502, 503)


def test_analyze_message_empty(client):
    """Empty message should be rejected by validation."""
    response = client.post("/analyze-message", json={"message": ""})
    assert response.status_code == 422


# ── /whatsapp endpoint ────────────────────────────────────────────────

def test_whatsapp_webhook_form_success(client, monkeypatch):
    """Twilio webhook should accept form-encoded payload and return XML."""
    monkeypatch.setattr("src.whatsapp_integration.TWILIO_AUTH_TOKEN", "")
    response = client.post("/whatsapp", data={
        "From": "whatsapp:+60123456789",
        "Body": "Your account is frozen. Click this link now.",
    })
    assert response.status_code == 200
    assert "application/xml" in response.headers["content-type"]
    assert "<Response>" in response.text
    assert "<Message>" in response.text


def test_whatsapp_webhook_missing_body(client):
    """Body is required in Twilio webhook payload."""
    response = client.post("/whatsapp", data={"From": "whatsapp:+60123456789"})
    assert response.status_code == 422
