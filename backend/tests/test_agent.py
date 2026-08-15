"""Tests for Single-Agent Orchestrator and POST /ask integration."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.agent.agent import integration_ops_agent, IntegrationOpsAgent

client = TestClient(app)


@pytest.mark.asyncio
async def test_agent_run_direct_execution():
    """Verify IntegrationOpsAgent.run() returns structured answer, sources, and tools_used."""
    agent = IntegrationOpsAgent()
    result = await agent.run("Why did JOB-1001 fail?")
    
    assert "answer" in result
    assert "sources" in result
    assert "tools_used" in result
    assert "get_job_status" in result["tools_used"]
    assert "get_job_logs" in result["tools_used"]


def test_scenario_documentation_only():
    """Scenario 1: Pure documentation question triggers RAG search with 0 tools used."""
    response = client.post("/ask", json={"question": "What is the publishing flow?"})
    assert response.status_code == 200
    data = response.json()

    assert data["tools_used"] == []
    assert len(data["sources"]) > 0
    doc_names = [s["document_name"] for s in data["sources"]]
    assert "publishing.md" in doc_names or "architecture.md" in doc_names


def test_scenario_job_failure_only():
    """Scenario 2: Job failure question triggers operational tools."""
    response = client.post("/ask", json={"question": "Why did JOB-1001 fail?"})
    assert response.status_code == 200
    data = response.json()

    assert "get_job_status" in data["tools_used"]
    assert "get_job_logs" in data["tools_used"]
    assert "JOB-1001" in data["answer"] or "Publisher" in data["answer"] or "FAILED" in data["answer"]


def test_scenario_most_important_combined_query():
    """CRITICAL TEST: Combined question triggers BOTH operational tools AND RAG document search.
    
    Question: "Why did JOB-1001 fail and what should normally happen during publishing?"
    """
    response = client.post(
        "/ask",
        json={"question": "Why did JOB-1001 fail and what should normally happen during publishing?"},
    )
    assert response.status_code == 200
    data = response.json()

    # 1. Verify tools were executed for JOB-1001
    assert "tools_used" in data
    assert "get_job_status" in data["tools_used"]
    assert "get_job_logs" in data["tools_used"]

    # 2. Verify RAG document sources were retrieved for publishing
    assert "sources" in data
    assert len(data["sources"]) > 0
    doc_names = [s["document_name"] for s in data["sources"]]
    assert "publishing.md" in doc_names or "architecture.md" in doc_names or "error-handling.md" in doc_names

    # 3. Verify answer contains grounded synthesis
    answer = data["answer"]
    assert len(answer) > 0
    assert "JOB-1001" in answer or "Publisher" in answer or "customer_email" in answer or "FAILED" in answer
