"""Markdown document loader module."""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger("app.rag.loader")


@dataclass
class Document:
    """Class representing a raw ingested document."""

    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class MarkdownLoader:
    """Loader for reading and parsing local Markdown documentation files."""

    def __init__(self, docs_dir: Path):
        self.docs_dir = Path(docs_dir)

    def load_documents(self) -> List[Document]:
        """Load all .md files in the configured documentation directory."""
        if not self.docs_dir.exists():
            logger.warning("Docs directory does not exist: %s", self.docs_dir)
            return []

        documents: List[Document] = []
        for file_path in sorted(self.docs_dir.glob("*.md")):
            try:
                content = file_path.read_text(encoding="utf-8")
                # Extract first heading as document title if present
                first_line = content.splitlines()[0] if content.splitlines() else ""
                title = first_line.lstrip("#").strip() if first_line.startswith("#") else file_path.stem

                doc = Document(
                    content=content,
                    metadata={
                        "document_name": file_path.name,
                        "source_path": str(file_path.resolve()),
                        "title": title,
                    },
                )
                documents.append(doc)
                logger.info("Loaded document: %s (%d chars)", file_path.name, len(content))
            except Exception as e:
                logger.error("Failed to load document %s: %s", file_path, e)

        return documents
