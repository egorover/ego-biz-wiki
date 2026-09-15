"""Tests for the retrieval application service."""

from collections.abc import Sequence

import pytest

from app.application.retrieval.service import RetrievalService
from app.domain.document import DocumentMetadata
from app.domain.retrieval import RetrievedChunk


class FakeEmbeddingProvider:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def embed_query(self, query: str) -> list[float]:
        self.queries.append(query)
        return [1.0, 2.0]


class FakeVectorStore:
    def __init__(self, results: list[RetrievedChunk]) -> None:
        self.results = results
        self.embedding: Sequence[float] | None = None
        self.n_results: int | None = None

    def query(
        self,
        embedding: Sequence[float],
        n_results: int,
    ) -> list[RetrievedChunk]:
        self.embedding = embedding
        self.n_results = n_results
        return self.results


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


def make_chunk(
    chunk_id: str,
    distance: float,
    content: str = "content",
) -> RetrievedChunk:
    metadata = make_metadata()
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=metadata.document_id,
        content=content,
        distance=distance,
        metadata=metadata,
        source=metadata.source,
    )


def test_retrieval_service_normalizes_query() -> None:
    embedding_provider = FakeEmbeddingProvider()
    vector_store = FakeVectorStore([make_chunk("chunk-1", 0.2)])
    service = RetrievalService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    result = service.retrieve("  Как оформить отпуск?  ")

    assert result[0].chunk_id == "chunk-1"
    assert embedding_provider.queries == ["Как оформить отпуск?"]


def test_retrieval_service_passes_top_k_to_vector_store() -> None:
    embedding_provider = FakeEmbeddingProvider()
    vector_store = FakeVectorStore([make_chunk("chunk-1", 0.2)])
    service = RetrievalService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        top_k=3,
    )

    service.retrieve("query")

    assert vector_store.n_results == 3


def test_retrieval_service_orders_results_by_distance() -> None:
    embedding_provider = FakeEmbeddingProvider()
    vector_store = FakeVectorStore(
        [
            make_chunk("chunk-3", 0.8),
            make_chunk("chunk-1", 0.2),
            make_chunk("chunk-2", 0.5),
        ]
    )
    service = RetrievalService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    result = service.retrieve("query")

    assert [chunk.chunk_id for chunk in result] == [
        "chunk-1",
        "chunk-2",
        "chunk-3",
    ]


def test_retrieval_service_applies_distance_threshold() -> None:
    embedding_provider = FakeEmbeddingProvider()
    vector_store = FakeVectorStore(
        [
            make_chunk("chunk-1", 0.2),
            make_chunk("chunk-2", 0.6),
            make_chunk("chunk-3", 0.9),
        ]
    )
    service = RetrievalService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        score_threshold=0.6,
    )

    result = service.retrieve("query")

    assert [chunk.chunk_id for chunk in result] == [
        "chunk-1",
        "chunk-2",
    ]


def test_retrieval_service_preserves_metadata_and_source() -> None:
    embedding_provider = FakeEmbeddingProvider()
    vector_store = FakeVectorStore(
        [make_chunk("chunk-1", 0.2, content="vacation policy")]
    )
    service = RetrievalService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    result = service.retrieve("query")

    assert result[0].content == "vacation policy"
    assert result[0].document_id == "hr-policy"
    assert result[0].metadata.title == "Policy"
    assert result[0].source == "HR / Policy"
    assert result[0].distance == 0.2


def test_retrieval_service_returns_empty_result() -> None:
    embedding_provider = FakeEmbeddingProvider()
    vector_store = FakeVectorStore([])
    service = RetrievalService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    result = service.retrieve("query")

    assert result == []


@pytest.mark.parametrize("query", ["", "   "])
def test_retrieval_service_rejects_empty_query(query: str) -> None:
    service = RetrievalService(
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=FakeVectorStore([]),
    )

    with pytest.raises(ValueError, match="query must not be empty"):
        service.retrieve(query)


def test_retrieval_service_rejects_invalid_top_k() -> None:
    with pytest.raises(ValueError, match="top_k"):
        RetrievalService(
            embedding_provider=FakeEmbeddingProvider(),
            vector_store=FakeVectorStore([]),
            top_k=0,
        )


def test_retrieval_service_rejects_negative_threshold() -> None:
    with pytest.raises(ValueError, match="score_threshold"):
        RetrievalService(
            embedding_provider=FakeEmbeddingProvider(),
            vector_store=FakeVectorStore([]),
            score_threshold=-0.1,
        )