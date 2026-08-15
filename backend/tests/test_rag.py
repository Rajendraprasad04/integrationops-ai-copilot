"""Unit and integration tests for RAG indexing, chunking, vector store, and search API."""

import pytest
import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.rag.chunker import MarkdownChunker
from app.rag.loader import Document
from app.rag.vector_store import (
    InMemoryVectorStore,
    DocumentChunk,
    compute_cosine_similarity,
)

client = TestClient(app)


def test_cosine_similarity_math():
    """Verify mathematical correctness of cosine similarity calculations."""
    vec_a = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    vec_b = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    vec_c = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    vec_d = np.array([-1.0, 0.0, 0.0], dtype=np.float32)

    # Identical vectors -> 1.0
    assert pytest.approx(compute_cosine_similarity(vec_a, vec_b), 0.001) == 1.0
    # Orthogonal vectors -> 0.0
    assert pytest.approx(compute_cosine_similarity(vec_a, vec_c), 0.001) == 0.0
    # Opposite vectors -> -1.0
    assert pytest.approx(compute_cosine_similarity(vec_a, vec_d), 0.001) == -1.0


def test_markdown_chunking_and_metadata_preservation():
    """Verify document chunking and metadata preservation (document_name, section, chunk_index)."""
    doc_content = """# Overview Section
IntegrationOps architecture supports enterprise pipeline publishing.

## Pre-Publish Schema Validation
Publisher validates column schema constraints before executing SQL upserts.
"""
    doc = Document(
        content=doc_content,
        metadata={"document_name": "publishing.md", "source_path": "/docs/publishing.md"},
    )

    chunker = MarkdownChunker(chunk_size=200, chunk_overlap=20)
    chunks = chunker.chunk_document(doc)

    assert len(chunks) >= 2
    first_chunk = chunks[0]
    assert first_chunk.metadata["document_name"] == "publishing.md"
    assert first_chunk.metadata["chunk_index"] == 0
    assert "Overview" in first_chunk.metadata["section"]

    second_chunk = chunks[1]
    assert second_chunk.metadata["document_name"] == "publishing.md"
    assert second_chunk.metadata["chunk_index"] == 1
    assert "Pre-Publish Schema Validation" in second_chunk.metadata["section"]


def test_vector_store_indexing_and_retrieval():
    """Verify in-memory vector store insertion and similarity search ordering."""
    store = InMemoryVectorStore()
    chunk1 = DocumentChunk(
        chunk_id="publishing.md#chunk_0",
        chunk_text="Publisher validates column schema constraints.",
        metadata={"document_name": "publishing.md", "section": "Validation"},
    )
    chunk2 = DocumentChunk(
        chunk_id="scheduler.md#chunk_0",
        chunk_text="Scheduler triggers batch jobs on cron expressions.",
        metadata={"document_name": "scheduler.md", "section": "Schedule"},
    )

    emb1 = [1.0, 0.0, 0.0]
    emb2 = [0.0, 1.0, 0.0]

    store.add_chunks([chunk1, chunk2], [emb1, emb2])
    assert store.count() == 2

    # Query matching emb1
    results = store.similarity_search([0.9, 0.1, 0.0], top_k=2)
    assert len(results) == 2
    assert results[0].chunk_id == "publishing.md#chunk_0"
    assert results[0].similarity_score > results[1].similarity_score


def test_post_rag_query_api():
    """Verify POST /rag/query endpoint returns relevant chunks for question."""
    payload = {
        "question": "What happens during publishing?",
        "top_k": 3,
    }
    response = client.post("/rag/query", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["question"] == "What happens during publishing?"
    assert isinstance(data["results"], list)
    assert len(data["results"]) > 0

    top_hit = data["results"][0]
    assert "chunk_text" in top_hit
    assert "similarity_score" in top_hit
    assert "metadata" in top_hit
    assert "document_name" in top_hit["metadata"]
    assert "section" in top_hit["metadata"]
    assert "chunk_index" in top_hit["metadata"]
