"""API router for RAG semantic search and grounded Q&A."""

import logging
from fastapi import APIRouter

from app.models.schemas import (
    AskRequest,
    AskResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    RAGSearchResultItem,
    SourceItem,
)
from app.agent.agent import integration_ops_agent
from app.rag.pipeline import rag_pipeline
from app.rag.retriever import rag_retriever

logger = logging.getLogger("app.api.rag")
router = APIRouter(tags=["RAG Document Retrieval & Q&A"])


@router.post("/rag/query", response_model=RAGQueryResponse)
async def query_rag_documents(payload: RAGQueryRequest) -> RAGQueryResponse:
    """Search synthetic operational documentation using vector similarity search."""
    logger.info("RAG query received: '%s' (top_k=%d)", payload.question, payload.top_k)
    search_hits = rag_retriever.retrieve(query=payload.question, top_k=payload.top_k)

    results = [
        RAGSearchResultItem(
            chunk_text=hit.chunk_text,
            similarity_score=hit.similarity_score,
            metadata=hit.metadata,
        )
        for hit in search_hits
    ]

    return RAGQueryResponse(
        question=payload.question,
        results=results,
    )


@router.post("/ask", response_model=AskResponse)
async def ask_question(payload: AskRequest) -> AskResponse:
    """Grounded Single-Agent copilot endpoint synthesizing tool outputs and document context."""
    logger.info("Agent /ask endpoint queried: '%s'", payload.question)
    response_data = await integration_ops_agent.run(question=payload.question)

    sources = [
        SourceItem(
            document_name=item["document_name"],
            section=item["section"],
            source_path=item.get("source_path"),
        )
        for item in response_data.get("sources", [])
    ]

    return AskResponse(
        answer=response_data["answer"],
        sources=sources,
        tools_used=response_data.get("tools_used", []),
    )
