import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Adaptive RAG Workbench API" in response.json()["message"]

def test_index_stats():
    response = client.get("/api/index-stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert "company_breakdown" in data
    assert isinstance(data["total_documents"], int)
