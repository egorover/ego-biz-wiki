"""Domain models for knowledge retrieval."""

from dataclasses import dataclass

from app.domain.document import DocumentMetadata


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    """A knowledge-base chunk returned by semantic retrieval."""

    chunk_id: str
    document_id: str
    content: str
    distance: float
    metadata: DocumentMetadata
    source: str
