"""Application service orchestrating the indexing pipeline."""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence

from app.domain.chunk import DocumentChunk
from app.domain.document import Document, DocumentMetadata


class MetadataProvider(Protocol):
    """Provide validated knowledge base metadata."""

    def load(self) -> list[DocumentMetadata]: ...


class DocumentLoader(Protocol):
    """Load a document from its metadata."""

    def load(self, metadata: DocumentMetadata, knowledge_base: Path) -> Document: ...


class Chunker(Protocol):
    """Split a document into deterministic chunks."""

    def split(self, document: Document) -> list[DocumentChunk]: ...


class EmbeddingProvider(Protocol):
    """Create embeddings for indexed text."""

    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


class VectorStore(Protocol):
    """Persist text, embeddings and metadata."""

    def upsert(
        self,
        chunks: Sequence[DocumentChunk],
        embeddings: Sequence[Sequence[float]],
    ) -> None: ...


@dataclass(frozen=True, slots=True)
class IndexingResult:
    """Summary of an indexing run."""

    documents_count: int
    chunks_count: int


class IndexingService:
    """Coordinate document loading, chunking, embedding and persistence."""

    def __init__(
        self,
        metadata_provider: MetadataProvider,
        document_loader: DocumentLoader,
        chunker: Chunker,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        knowledge_base: Path,
    ) -> None:
        self._metadata_provider = metadata_provider
        self._document_loader = document_loader
        self._chunker = chunker
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._knowledge_base = knowledge_base

    def run(self) -> IndexingResult:
        """Execute the full indexing pipeline for the configured knowledge base."""
        metadata_items = self._metadata_provider.load()
        chunks: list[DocumentChunk] = []

        for metadata in metadata_items:
            document = self._document_loader.load(metadata, self._knowledge_base)
            chunks.extend(self._chunker.split(document))

        if not chunks:
            raise RuntimeError("Indexing produced no document chunks.")

        embeddings = self._embedding_provider.embed([chunk.content for chunk in chunks])
        if len(embeddings) != len(chunks):
            raise RuntimeError(
                "Embedding provider returned a different number of vectors "
                "than chunks."
            )

        self._vector_store.upsert(chunks, embeddings)
        return IndexingResult(
            documents_count=len(metadata_items),
            chunks_count=len(chunks),
        )
