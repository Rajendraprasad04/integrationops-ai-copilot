"""Pydantic Request and Response Schemas."""

from typing import Any, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check endpoint response model."""

    status: str = Field(default="ok", description="Operational status of the service")
    service: str = Field(..., description="Name of the service")
    version: str = Field(..., description="Service version")
    environment: str = Field(..., description="Running environment")


class SystemInfoResponse(BaseModel):
    """Root endpoint response model."""

    message: str = Field(..., description="Welcome message")
    service: str = Field(..., description="Name of the service")
    version: str = Field(..., description="Service version")
    docs_url: str = Field(default="/docs", description="Interactive API documentation URL")


class ErrorDetail(BaseModel):
    """Standardized error message details."""

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error description")


class ErrorResponse(BaseModel):
    """Standardized API error response format."""

    error: ErrorDetail


class RAGQueryRequest(BaseModel):
    """RAG semantic search request body model."""

    question: str = Field(..., min_length=1, description="Question or query string")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of relevant document chunks to return")


class RAGSearchResultItem(BaseModel):
    """Individual retrieved document chunk search result item."""

    chunk_text: str = Field(..., description="Text content of the retrieved chunk")
    similarity_score: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary (doc name, section, chunk_index)")


class RAGQueryResponse(BaseModel):
    """RAG semantic search response model."""

    question: str = Field(..., description="Original query question")
    results: list[RAGSearchResultItem] = Field(default_factory=list, description="Top relevant document chunks")


class AskRequest(BaseModel):
    """Grounded RAG question request body model."""

    question: str = Field(..., min_length=1, description="Question or ops query string")


class SourceItem(BaseModel):
    """Source reference item for grounded answers."""

    document_name: str = Field(..., description="Document file name")
    section: str = Field(..., description="Section header title")
    source_path: Optional[str] = Field(None, description="Absolute source path")


class AskResponse(BaseModel):
    """Grounded RAG answer response model."""

    answer: str = Field(..., description="Grounded answer text generated from context")
    sources: list[SourceItem] = Field(default_factory=list, description="Source documents used")
    tools_used: list[str] = Field(default_factory=list, description="List of tools invoked during query resolution")
