"""Tests for backend system and health endpoints."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_root():
    """Verify GET / returns 200 OK and expected system info payload."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "integrationops-ai"
    assert data["message"] == "Welcome to IntegrationOps AI Copilot API"
    assert "version" in data
    assert "docs_url" in data


def test_get_health():
    """Verify GET /health returns status ok and service name."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "integrationops-ai"
    assert "version" in data
    assert "environment" in data


def test_404_error_handler():
    """Verify non-existent routes return standardized JSON error response."""
    response = client.get("/non-existent-route")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "HTTP_404"
