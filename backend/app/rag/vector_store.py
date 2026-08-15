"""In-memory vector store module with NumPy cosine similarity search."""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any
import numpy as np

from app.rag.chunker import DocumentChunk

logger = logging.getLogger("app.rag.vector_store")


def compute_cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Compute cosine similarity score between two 1D floating point vectors."""
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a < 1e-9 or norm_b < 1e-9:
        return 0.0
    similarity = float(np.dot(vec_a, vec_b) / (norm_a * norm_b))
    # Clip numerical float inaccuracies to [-1.0, 1.0] range
    return float(np.clip(similarity, -1.0, 1.0))


@dataclass
class SearchResult:
    """Class representing a retrieved search hit with metadata and similarity score."""

    chunk_id: str
    chunk_text: str
    similarity_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class InMemoryVectorStore:
    """High-performance in-memory vector store powered by NumPy matrix operations."""

    def __init__(self):
        self._chunks: List[DocumentChunk] = []
        self._vectors: List[np.ndarray] = []

    def add_chunks(self, chunks: List[DocumentChunk], embeddings: List[List[float]]):
        """Insert document chunks and their associated vector embeddings into memory."""
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings.")

        for chunk, embedding in zip(chunks, embeddings):
            self._chunks.append(chunk)
            self._vectors.append(np.array(embedding, dtype=np.float32))

        logger.info("Added %d chunks to vector store. Total chunks: %d", len(chunks), len(self._chunks))

    def similarity_search(self, query_embedding: List[float], top_k: int = 3) -> List[SearchResult]:
        """Perform top-K cosine similarity search against stored chunk vectors."""
        if not self._chunks or not self._vectors:
            logger.warning("Vector store is empty. Returning 0 results.")
            return []

        query_vec = np.array(query_embedding, dtype=np.float32)
        scores: List[tuple[float, int]] = []

        for idx, doc_vec in enumerate(self._vectors):
            score = compute_cosine_similarity(query_vec, doc_vec)
            scores.append((score, idx))

        # Sort by similarity score descending
        scores.sort(key=lambda x: x[0], reverse=True)

        results: List[SearchResult] = []
        for score, idx in scores[:top_k]:
            chunk = self._chunks[idx]
            results.append(
                SearchResult(
                    chunk_id=chunk.chunk_id,
                    chunk_text=chunk.chunk_text,
                    similarity_score=round(score, 4),
                    metadata=chunk.metadata,
                )
            )

        return results

    def clear(self):
        """Reset the vector store index."""
        self._chunks.clear()
        self._vectors.clear()

    def count(self) -> int:
        """Return total number of vectors in index."""
        return len(self._chunks)
