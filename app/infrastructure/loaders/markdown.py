"""Markdown document loader."""

from pathlib import Path

from app.domain.document import Document, DocumentMetadata


class MarkdownLoader:
    """Load UTF-8 Markdown files referenced by the manifest."""

    def load(self, metadata: DocumentMetadata, knowledge_base: Path) -> Document:
        """Read a Markdown document and attach validated metadata."""
        path = knowledge_base / metadata.path
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise RuntimeError(f"Failed to load document: {path}") from exc

        if not content.strip():
            raise ValueError(f"Document is empty: {metadata.path}")

        return Document(metadata=metadata, content=content, source_path=path)
