import pytest

from app.ml.service import MLService


def test_ml_predict_returns_neutral_on_model_error(client, monkeypatch):
    # Register a user via the API and then force MLService._load_or_train to raise
    payload = {"email": "failml@example.com", "name": "Fail ML", "password": "SecurePass123!"}
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 201
    token = resp.json()["tokens"]["access_token"]

    def raise_error(user_id, db):
        raise RuntimeError("simulated model load failure")

    monkeypatch.setattr(MLService, "_load_or_train", staticmethod(raise_error))

    response = client.post("/api/ml/predictions", json={}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert body["model_version"] == "unavailable"
    assert any("Model unavailable" in r for r in body.get("recommendations", []))
