"""Application service for semantic knowledge retrieval."""

from collections.abc import Sequence
from typing import Protocol

from app.domain.retrieval import RetrievedChunk


class QueryEmbeddingProvider(Protocol):
    """Generate embeddings for retrieval queries."""

    def embed_query(self, query: str) -> list[float]:
        """Generate an embedding for a single query."""
        ...


class RetrievalVectorStore(Protocol):
    """Retrieve indexed chunks by vector similarity."""

    def query(
        self,
        embedding: Sequence[float],
        n_results: int,
    ) -> list[RetrievedChunk]:
        """Return the nearest indexed chunks."""
        ...


class RetrievalService:
    """Coordinate semantic retrieval without infrastructure dependencies."""

    def __init__(
        self,
        embedding_provider: QueryEmbeddingProvider,
        vector_store: RetrievalVectorStore,
        top_k: int = 5,
        score_threshold: float | None = None,
    ) -> None:
        if top_k < 1:
            raise ValueError("top_k must be greater than zero.")
        if score_threshold is not None and score_threshold < 0:
            raise ValueError("score_threshold must not be negative.")

        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._top_k = top_k
        self._score_threshold = score_threshold

    def retrieve(self, query: str) -> list[RetrievedChunk]:
        """Retrieve the most relevant knowledge chunks for a query."""
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("query must not be empty.")

        embedding = self._embedding_provider.embed_query(normalized_query)
        results = self._vector_store.query(
            embedding=embedding,
            n_results=self._top_k,
        )

        if self._score_threshold is not None:
            results = [
                result
                for result in results
                if result.distance <= self._score_threshold
            ]

        return sorted(results, key=lambda result: result.distance)
