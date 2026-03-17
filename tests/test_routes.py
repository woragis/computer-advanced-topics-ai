import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    resp = client.get("/ai/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_analyze_missing_input():
    resp = client.post("/ai/analyze", json={})
    assert resp.status_code == 400
    assert "Provide 'url' or 'text'" in resp.json()["detail"]
