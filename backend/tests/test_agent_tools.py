"""Tests for operational tools, router orchestration, and hybrid /ask API endpoint."""

from fastapi.testclient import TestClient
from app.main import app
from app.agent.tools import (
    get_integration_config,
    get_job_logs,
    get_job_status,
    get_pipeline_metrics,
)

client = TestClient(app)


def test_tool_get_job_status_success():
    """Verify get_job_status tool returns structured job details for JOB-1001."""
    res = get_job_status("JOB-1001")
    assert res["found"] is True
    assert res["job_id"] == "JOB-1001"
    assert res["status"] == "FAILED"
    assert res["service"] == "Publisher"
    assert "Destination validation failed" in res["error_message"]


def test_tool_get_job_status_missing_id():
    """Verify get_job_status handles missing job ID gracefully."""
    res = get_job_status("JOB-9999")
    assert res["found"] is False
    assert "error" in res


def test_tool_get_job_logs_success():
    """Verify get_job_logs tool returns log trace entries for JOB-1001."""
    res = get_job_logs("JOB-1001")
    assert res["found"] is True
    assert res["job_id"] == "JOB-1001"
    assert res["log_count"] >= 4
    assert isinstance(res["logs"], list)


def test_tool_get_integration_config():
    """Verify get_integration_config tool returns pipeline configuration."""
    res = get_integration_config("salesforce_postgres")
    assert res["found"] is True
    assert res["integration_id"] == "salesforce_postgres"
    assert res["name"] == "Salesforce CRM to PostgreSQL Sync"
    assert res["status"] == "DEGRADED"


def test_tool_get_pipeline_metrics():
    """Verify get_pipeline_metrics calculates failure rates and record counts."""
    res = get_pipeline_metrics("JOB-1001")
    assert res["found"] is True
    assert res["job_id"] == "JOB-1001"
    assert res["records_processed"] == 1450
    assert res["records_failed"] == 120
    assert res["total_records_handled"] == 1570
    assert res["failure_rate_percent"] > 0.0


def test_ask_query_routing_job_tools():
    """Verify POST /ask executes job tools for 'What happened to JOB-1001?'."""
    response = client.post("/ask", json={"question": "What happened to JOB-1001?"})
    assert response.status_code == 200
    data = response.json()

    assert "tools_used" in data
    assert "get_job_status" in data["tools_used"]
    assert "get_job_logs" in data["tools_used"]
    assert "JOB-1001" in data["answer"] or "Publisher" in data["answer"]


def test_ask_query_routing_rag_only():
    """Verify POST /ask runs RAG only (no tools) for document flow questions."""
    response = client.post("/ask", json={"question": "What is the normal publishing flow?"})
    assert response.status_code == 200
    data = response.json()

    assert data["tools_used"] == []
    assert len(data["sources"]) > 0
    doc_names = [s["document_name"] for s in data["sources"]]
    assert "publishing.md" in doc_names or "architecture.md" in doc_names


def test_ask_query_routing_hybrid_rag_and_tools():
    """Verify POST /ask runs BOTH tools AND RAG for combined questions."""
    response = client.post(
        "/ask",
        json={"question": "Why did JOB-1001 fail and what should normally happen during publishing?"},
    )
    assert response.status_code == 200
    data = response.json()

    # Must contain tool execution
    assert "get_job_status" in data["tools_used"]
    assert "get_job_logs" in data["tools_used"]

    # Must contain RAG document sources
    assert len(data["sources"]) > 0
    doc_names = [s["document_name"] for s in data["sources"]]
    assert "publishing.md" in doc_names or "error-handling.md" in doc_names
