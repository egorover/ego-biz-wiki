"""Unit tests for the RAG application service."""

from dataclasses import dataclass

from app.application.rag.service import FALLBACK_ANSWER, RAGService
from app.domain.document import DocumentMetadata
from app.domain.retrieval import RetrievedChunk


@dataclass
class FakeRetrievalService:
    """Fake retrieval service for unit tests."""

    chunks: list[RetrievedChunk]

    def retrieve(self, query: str) -> list[RetrievedChunk]:
        """Return predefined chunks."""
        return self.chunks


@dataclass
class FakeLLMProvider:
    """Fake LLM provider for unit tests."""

    response: str = "Тестовый ответ."

    last_query: str = ""
    last_context: str = ""

    def generate(self, query: str, context: str) -> str:
        """Return a predefined response and record the input."""
        self.last_query = query
        self.last_context = context
        return self.response


def create_chunk(
    document_id: str = "doc-001",
    chunk_id: str = "chunk-001",
    title: str = "Политика отпусков",
    source: str = "hr/leave-policy.md",
    content: str = "Сотрудник может оформить отпуск через HR-систему.",
) -> RetrievedChunk:
    """Create a retrieved chunk for testing."""
    metadata =     metadata = DocumentMetadata(
        document_id=document_id,
        title=title,
        category="hr",
        subcategory="leave",
        path=source,
        source=source,
        version="1.0",
        language="ru",
        access_level="internal",
        updated_at="2026-09-15",
    )

    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        content=content,
        distance=0.2,
        metadata=metadata,
        source=source,
    )


def test_returns_fallback_when_no_chunks_are_found() -> None:
    """Return the exact fallback when retrieval returns no chunks."""
    retrieval = FakeRetrievalService(chunks=[])
    llm = FakeLLMProvider()
    service = RAGService(retrieval, llm)

    response = service.answer("Как оформить отпуск?")

    assert response.answer == FALLBACK_ANSWER
    assert response.sources == []
    assert llm.last_query == ""


def test_generates_answer_from_retrieved_context() -> None:
    """Pass the retrieved context to the LLM provider."""
    chunk = create_chunk()
    retrieval = FakeRetrievalService(chunks=[chunk])
    llm = FakeLLMProvider(response="Отпуск оформляется через HR-систему.")
    service = RAGService(retrieval, llm)

    response = service.answer("Как оформить отпуск?")

    assert response.answer == "Отпуск оформляется через HR-систему."
    assert llm.last_query == "Как оформить отпуск?"
    assert "Политика отпусков" in llm.last_context
    assert "Сотрудник может оформить отпуск через HR-систему." in llm.last_context


def test_returns_unique_sources_for_multiple_chunks() -> None:
    """Return one source per document."""
    first = create_chunk(chunk_id="chunk-001")
    second = create_chunk(chunk_id="chunk-002")

    retrieval = FakeRetrievalService(chunks=[first, second])
    llm = FakeLLMProvider()
    service = RAGService(retrieval, llm)

    response = service.answer("Как оформить отпуск?")

    assert len(response.sources) == 1
    assert response.sources[0].document_id == "doc-001"
    assert response.sources[0].title == "Политика отпусков"


def test_rejects_empty_query() -> None:
    """Reject an empty user query."""
    retrieval = FakeRetrievalService(chunks=[])
    llm = FakeLLMProvider()
    service = RAGService(retrieval, llm)

    try:
        service.answer("   ")
    except ValueError as exc:
        assert str(exc) == "query must not be empty."
    else:
        raise AssertionError("Expected ValueError.")
