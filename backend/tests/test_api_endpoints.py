import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db, drop_db

DB_FILE = Path(__file__).resolve().parents[1] / "quanttrack_test.db"


@pytest.fixture(scope="session", autouse=True)
def test_database():
    if DB_FILE.exists():
        DB_FILE.unlink()
    init_db()
    yield
    drop_db()
    if DB_FILE.exists():
        DB_FILE.unlink()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def register_user(client, email="test@example.com"):
    payload = {
        "email": email,
        "name": "Test Trader",
        "password": "SecurePass123!",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    return response.json()["tokens"]["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_register_login_and_verify(client):
    token = register_user(client, email="verify@example.com")
    response = client.get("/api/auth/verify", headers=auth_headers(token))
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "verify@example.com"
    assert body["is_active"] is True


def test_trade_statistics_empty_defaults(client):
    token = register_user(client, email="stats@example.com")
    response = client.get("/api/trades/statistics/summary", headers=auth_headers(token))
    assert response.status_code == 200
    data = response.json()
    assert data["total_trades"] == 0
    assert data["win_rate"] == 0.0
    assert data["profit_factor"] == 0.0


def test_ml_prediction_returns_model_result(client):
    token = register_user(client, email="ml@example.com")
    response = client.post("/api/ml/predictions", json={}, headers=auth_headers(token))
    assert response.status_code == 200
    data = response.json()
    assert "profitability_probability" in data
    assert "feature_snapshot" in data
    assert data["model_version"]


def test_trade_validation_rejects_bad_timestamp(client):
    token = register_user(client, email="validation@example.com")
    payload = {
        "symbol": "AAPL",
        "direction": "LONG",
        "entry_price": 150.0,
        "exit_price": 145.0,
        "lot_size": 1,
        "entry_timestamp": "2026-10-01T10:00:00",
        "exit_timestamp": "2025-10-01T10:00:00",
    }
    response = client.post("/api/trades", json=payload, headers=auth_headers(token))
    assert response.status_code == 400
    assert "exit_timestamp must be after entry_timestamp" in response.json()["detail"]
