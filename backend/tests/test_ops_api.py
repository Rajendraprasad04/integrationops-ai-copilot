"""Tests for Integrations, Jobs, and Logs read-only API endpoints."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_integrations():
    """Verify GET /integrations returns all synthetic integrations."""
    response = client.get("/integrations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5
    integration_ids = [item["integration_id"] for item in data]
    assert "salesforce_postgres" in integration_ids
    assert "github_bigquery" in integration_ids


def test_get_integration_success():
    """Verify GET /integrations/{id} returns integration details."""
    response = client.get("/integrations/salesforce_postgres")
    assert response.status_code == 200
    data = response.json()
    assert data["integration_id"] == "salesforce_postgres"
    assert data["name"] == "Salesforce CRM to PostgreSQL Sync"
    assert data["status"] == "DEGRADED"
    assert data["source_system"] == "Salesforce CRM"
    assert data["destination_system"] == "PostgreSQL Warehouse"


def test_get_integration_not_found():
    """Verify GET /integrations/{id} returns 404 for unknown integration."""
    response = client.get("/integrations/unknown_integration")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "HTTP_404"


def test_get_job_1001_failed_demo():
    """Verify GET /jobs/JOB-1001 returns the failed demo job."""
    response = client.get("/jobs/JOB-1001")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "JOB-1001"
    assert data["integration"] == "salesforce_postgres"
    assert data["status"] == "FAILED"
    assert data["service"] == "Publisher"
    assert "Destination validation failed" in data["error_message"]
    assert data["records_failed"] == 120


def test_get_job_not_found():
    """Verify GET /jobs/{id} returns 404 for unknown job ID."""
    response = client.get("/jobs/JOB-9999")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "HTTP_404"


def test_get_job_logs_success():
    """Verify GET /jobs/JOB-1001/logs returns logs for JOB-1001."""
    response = client.get("/jobs/JOB-1001/logs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 4
    first_log = data[0]
    assert first_log["job_id"] == "JOB-1001"
    assert "log_id" in first_log
    assert "level" in first_log
    assert "message" in first_log

    # Check for ERROR log entry
    levels = [log["level"] for log in data]
    assert "ERROR" in levels


def test_get_job_logs_not_found():
    """Verify GET /jobs/{id}/logs returns 404 for non-existent job ID."""
    response = client.get("/jobs/JOB-9999/logs")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "HTTP_404"
