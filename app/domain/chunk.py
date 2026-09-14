"""Domain model for indexed document chunks."""

from dataclasses import dataclass

from app.domain.document import DocumentMetadata


@dataclass(frozen=True, slots=True)
class DocumentChunk:
    """A deterministic chunk derived from a knowledge base document."""

    chunk_id: str
    document_id: str
    chunk_index: int
    content: str
    metadata: DocumentMetadata

    @property
    def vector_metadata(self) -> dict[str, str | int]:
        """Return metadata ready for vector-store persistence."""
        return {
            **self.metadata.model_dump(exclude={"document_id", "path"}),
            "document_id": self.document_id,
            "path": self.metadata.path,
            "chunk_index": self.chunk_index,
        }
