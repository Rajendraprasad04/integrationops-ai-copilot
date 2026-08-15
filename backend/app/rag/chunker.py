"""Document chunking and text splitting module."""

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Any
from app.rag.loader import Document

logger = logging.getLogger("app.rag.chunker")


@dataclass
class DocumentChunk:
    """Class representing a processed text chunk with metadata."""

    chunk_id: str
    chunk_text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class MarkdownChunker:
    """Splits Markdown documents into logical section-aware text chunks."""

    def __init__(self, chunk_size: int = 450, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, document: Document) -> List[DocumentChunk]:
        """Process a single Document into multiple DocumentChunks."""
        chunks: List[DocumentChunk] = []
        doc_name = document.metadata.get("document_name", "unknown.md")

        # Split content into sections based on Markdown headers
        sections = self._split_by_headers(document.content)
        chunk_index = 0

        for section_title, section_text in sections:
            if not section_text.strip():
                continue

            # Split section_text if it exceeds chunk_size
            sub_chunks = self._slice_text(section_text)
            for sub_text in sub_chunks:
                chunk_id = f"{doc_name}#chunk_{chunk_index}"
                chunk_metadata = {
                    "document_name": doc_name,
                    "section": section_title,
                    "chunk_index": chunk_index,
                    "char_count": len(sub_text),
                    "source_path": document.metadata.get("source_path", ""),
                }

                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    chunk_text=sub_text.strip(),
                    metadata=chunk_metadata,
                )
                chunks.append(chunk)
                chunk_index += 1

        logger.info("Chunked document '%s' into %d chunks", doc_name, len(chunks))
        return chunks

    def chunk_documents(self, documents: List[Document]) -> List[DocumentChunk]:
        """Process a collection of Document objects."""
        all_chunks: List[DocumentChunk] = []
        for doc in documents:
            all_chunks.extend(self.chunk_document(doc))
        return all_chunks

    def _split_by_headers(self, content: str) -> List[tuple[str, str]]:
        """Split markdown text into (section_header, section_content) pairs."""
        header_pattern = re.compile(r"^(#{1,4}\s+.+)$", re.MULTILINE)
        lines = content.splitlines()
        
        sections: List[tuple[str, str]] = []
        current_header = "Overview"
        current_lines: List[str] = []

        for line in lines:
            if header_pattern.match(line):
                if current_lines:
                    sections.append((current_header, "\n".join(current_lines)))
                    current_lines = []
                current_header = line.lstrip("#").strip()
            else:
                current_lines.append(line)

        if current_lines:
            sections.append((current_header, "\n".join(current_lines)))

        return sections

    def _slice_text(self, text: str) -> List[str]:
        """Slice long text into overlapping chunks."""
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk_str = text[start:end]
            chunks.append(chunk_str)
            if end >= len(text):
                break
            start += self.chunk_size - self.chunk_overlap

        return chunks
