"""High-level RAG retrieval manager and index orchestrator."""

import logging
from pathlib import Path
from typing import List, Optional

from app.config import settings
from app.rag.chunker import MarkdownChunker
from app.rag.embeddings import BaseEmbeddingProvider, get_embedding_provider
from app.rag.loader import MarkdownLoader
from app.rag.vector_store import InMemoryVectorStore, SearchResult

logger = logging.getLogger("app.rag.retriever")


class RAGRetriever:
    """Orchestrates document loading, chunking, embedding, indexing, and retrieval."""

    def __init__(
        self,
        docs_dir: Optional[Path] = None,
        embedding_provider: Optional[BaseEmbeddingProvider] = None,
        vector_store: Optional[InMemoryVectorStore] = None,
    ):
        self.docs_dir = Path(docs_dir or (Path(settings.DATA_DIR) / "docs"))
        self.embedding_provider = embedding_provider or get_embedding_provider()
        self.vector_store = vector_store or InMemoryVectorStore()
        self.chunker = MarkdownChunker(chunk_size=450, chunk_overlap=50)
        self._is_indexed = False

    def index_documents(self, force_reindex: bool = False):
        """Build vector index from Markdown documentation files."""
        if self._is_indexed and not force_reindex:
            return

        logger.info("Starting documentation indexing from %s", self.docs_dir)
        self.vector_store.clear()

        loader = MarkdownLoader(self.docs_dir)
        documents = loader.load_documents()
        if not documents:
            logger.warning("No documents found in %s", self.docs_dir)
            self._is_indexed = True
            return

        chunks = self.chunker.chunk_documents(documents)
        if not chunks:
            logger.warning("No chunks generated from documents.")
            self._is_indexed = True
            return

        chunk_texts = [chunk.chunk_text for chunk in chunks]
        embeddings = self.embedding_provider.embed_documents(chunk_texts)

        self.vector_store.add_chunks(chunks, embeddings)
        self._is_indexed = True
        logger.info("Successfully indexed %d chunks across %d docs", len(chunks), len(documents))

    def retrieve(self, query: str, top_k: int = 3) -> List[SearchResult]:
        """Perform semantic similarity search for a user question."""
        if not self._is_indexed:
            self.index_documents()

        if not query.strip():
            return []

        query_embedding = self.embedding_provider.embed_text(query)
        results = self.vector_store.similarity_search(query_embedding, top_k=top_k)
        logger.info("Query '%s' returned %d top results", query, len(results))
        return results


# Global RAG Retriever Singleton
rag_retriever = RAGRetriever()
