"""Embedding provider module for text vectorization."""

import hashlib
import logging
import math
from abc import ABC, abstractmethod
from typing import List
import numpy as np

from app.config import settings

logger = logging.getLogger("app.rag.embeddings")


class BaseEmbeddingProvider(ABC):
    """Abstract Base Class for text embedding generation."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the dimension of the embedding vectors."""
        pass

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string into a float vector."""
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of text strings into a list of float vectors."""
        pass


class LocalHashEmbeddingProvider(BaseEmbeddingProvider):
    """Local, zero-dependency embedding provider using semantic n-gram hash projection.
    
    Generates deterministic unit-normalized vectors suitable for cosine similarity.
    """

    def __init__(self, dimension: int = 384):
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def _text_to_vector(self, text: str) -> np.ndarray:
        """Project text tokens and character n-grams into a normalized dense vector space."""
        vec = np.zeros(self._dimension, dtype=np.float32)
        words = text.lower().split()
        if not words:
            return vec

        # Sub-word & word token hashing
        tokens = list(words)
        # Add word 2-grams
        for i in range(len(words) - 1):
            tokens.append(f"{words[i]}_{words[i+1]}")

        for token in tokens:
            # MD5 hash token to deterministic index and magnitude
            hash_bytes = hashlib.md5(token.encode("utf-8")).digest()
            idx = int.from_bytes(hash_bytes[:4], "little") % self._dimension
            sign = 1.0 if (hash_bytes[4] % 2 == 0) else -1.0
            weight = 1.0 + (hash_bytes[5] / 255.0)
            vec[idx] += sign * weight

        # L2 Normalization to make dot product equal cosine similarity
        norm = np.linalg.norm(vec)
        if norm > 1e-9:
            vec = vec / norm

        return vec

    def embed_text(self, text: str) -> List[float]:
        """Generate unit vector for a single query text."""
        return self._text_to_vector(text).tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate unit vectors for a list of document chunks."""
        return [self.embed_text(t) for t in texts]


def get_embedding_provider() -> BaseEmbeddingProvider:
    """Factory function instantiating configured embedding provider."""
    # Expandable to SentenceTransformers or OpenAI if configured
    return LocalHashEmbeddingProvider(dimension=settings.EMBEDDING_DIMENSION)
