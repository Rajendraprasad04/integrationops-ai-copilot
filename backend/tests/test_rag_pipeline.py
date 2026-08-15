"""Tests for RAG pipeline, LLM client fallback, and POST /ask endpoint."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.llm.client import MockDevelopmentLLMClient, get_llm_client
from app.rag.pipeline import RAGPipeline

client = TestClient(app)


@pytest.mark.asyncio
async def test_mock_llm_client_fallback():
    """Verify MockDevelopmentLLMClient returns grounded answers from context."""
    llm = MockDevelopmentLLMClient()
    prompt = """DOCUMENT CONTEXT:
[Source: publishing.md | Section: Pre-Publish Schema Validation]
Before executing SQL bulk upserts, Publisher verifies column length constraints.

USER QUESTION:
What happens during publishing?"""

    answer = await llm.generate(prompt=prompt)
    assert "Publisher verifies column length constraints" in answer
    assert "Standard Operating Procedure" in answer


@pytest.mark.asyncio
async def test_rag_pipeline_insufficient_evidence():
    """Verify RAG pipeline handles unanswerable questions gracefully."""
    pipeline = RAGPipeline()
    # Question unrelated to any synthetic doc
    result = await pipeline.ask(question="What is the quantum mechanics formula for gravity?")
    assert "answer" in result
    assert "sources" in result


def test_post_ask_required_questions():
    """Test POST /ask endpoint across the 4 required project evaluation questions."""
    test_questions = [
        "What is the normal integration pipeline?",
        "How does normalization work?",
        "What happens during publishing?",
        "What are common causes of publisher failures?",
    ]

    for question in test_questions:
        response = client.post("/ask", json={"question": question})
        assert response.status_code == 200, f"Failed on question: {question}"
        data = response.json()

        assert "answer" in data
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 0
        assert "sources" in data
        assert isinstance(data["sources"], list)
        assert "tools_used" in data
        assert isinstance(data["tools_used"], list)

        # Check source items structure
        if data["sources"]:
            source = data["sources"][0]
            assert "document_name" in source
            assert "section" in source


def test_post_ask_publishing_question_details():
    """Verify specific source metadata returned for publishing question."""
    response = client.post("/ask", json={"question": "What happens during publishing?"})
    assert response.status_code == 200
    data = response.json()

    doc_names = [s["document_name"] for s in data["sources"]]
    assert "publishing.md" in doc_names or "architecture.md" in doc_names
