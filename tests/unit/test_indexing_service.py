"""Tests for the indexing application service."""

from pathlib import Path
from typing import Sequence

import pytest

from app.application.indexing.service import IndexingService
from app.domain.chunk import DocumentChunk
from app.domain.document import Document, DocumentMetadata


class FakeMetadataProvider:
    def __init__(self, items: list[DocumentMetadata]) -> None:
        self.items = items

    def load(self) -> list[DocumentMetadata]:
        return self.items


class FakeLoader:
    def load(self, metadata: DocumentMetadata, knowledge_base: Path) -> Document:
        return Document(
            metadata=metadata,
            content="content",
            source_path=knowledge_base / metadata.path,
        )


class FakeChunker:
    def split(self, document: Document) -> list[DocumentChunk]:
        return [
            DocumentChunk(
                chunk_id=f"{document.metadata.document_id}:0",
                document_id=document.metadata.document_id,
                chunk_index=0,
                content=document.content,
                metadata=document.metadata,
            )
        ]


class FakeEmbeddings:
    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [[1.0, 2.0] for _ in texts]


class FakeStore:
    def __init__(self) -> None:
        self.chunks: list[DocumentChunk] = []
        self.embeddings: list[Sequence[float]] = []

    def upsert(
        self,
        chunks: Sequence[DocumentChunk],
        embeddings: Sequence[Sequence[float]],
    ) -> None:
        self.chunks = list(chunks)
        self.embeddings = list(embeddings)


def make_metadata() -> DocumentMetadata:
    return DocumentMetadata(
        document_id="hr-policy",
        path="hr/policy.md",
        title="Policy",
        category="hr",
        subcategory="policy",
        source="HR / Policy",
        version="1.0",
        language="ru",
        access_level="internal",
        updated_at="2026-09-01",
    )


def test_indexing_service_orchestrates_pipeline(tmp_path: Path) -> None:
    store = FakeStore()
    service = IndexingService(
        metadata_provider=FakeMetadataProvider([make_metadata()]),
        document_loader=FakeLoader(),
        chunker=FakeChunker(),
        embedding_provider=FakeEmbeddings(),
        vector_store=store,
        knowledge_base=tmp_path,
    )

    result = service.run()

    assert result.documents_count == 1
    assert result.chunks_count == 1
    assert store.chunks[0].chunk_id == "hr-policy:0"
    assert store.embeddings == [[1.0, 2.0]]


def test_indexing_service_rejects_embedding_count_mismatch(tmp_path: Path) -> None:
    class BadEmbeddings(FakeEmbeddings):
        def embed(self, texts: Sequence[str]) -> list[list[float]]:
            return []

    service = IndexingService(
        metadata_provider=FakeMetadataProvider([make_metadata()]),
        document_loader=FakeLoader(),
        chunker=FakeChunker(),
        embedding_provider=BadEmbeddings(),
        vector_store=FakeStore(),
        knowledge_base=tmp_path,
    )

    with pytest.raises(RuntimeError, match="different number"):
        service.run()
