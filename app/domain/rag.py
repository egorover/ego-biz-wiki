"""Domain models for retrieval-augmented generation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RAGSource:
    """A source used to generate a grounded answer."""

    document_id: str
    source: str
    title: str


@dataclass(frozen=True, slots=True)
class RAGResponse:
    """A grounded answer with its knowledge-base sources."""

    answer: str
    sources: list[RAGSource]
