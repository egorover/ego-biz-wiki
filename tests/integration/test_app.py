"""Integration tests for the FastAPI application."""

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_rag_service, get_retrieval_service
from app.domain.document import DocumentMetadata
from app.domain.retrieval import RetrievedChunk
from app.domain.rag import RAGResponse, RAGSource
from app.main import app


class FakeRAGService:
    """Test double for the application RAG service."""

    def answer(self, query: str) -> RAGResponse:
        """Return a deterministic test response."""
        return RAGResponse(
            answer=f"Ответ на: {query}",
            sources=[
                RAGSource(
                    document_id="hr-leave",
                    title="Политика отпусков",
                    source="hr/leave_policy.md",
                )
            ],
        )


class FakeRetrievalService:
    """Test double for the application retrieval service."""

    def retrieve(self, query: str) -> list[RetrievedChunk]:
        """Return a deterministic test result."""
        return [
            RetrievedChunk(
                chunk_id="chunk-001",
                document_id="hr-leave",
                content="Сотрудник может оформить ежегодный отпуск.",
                distance=0.42,
                metadata=DocumentMetadata(
                    document_id="vacation-policy",
                    path="knowledge_base/hr/vacation_policy.md",
                    title="Политика отпусков",
                    category="HR",
                    subcategory="Vacation",
                    source="internal",
                    version="1.0",
                    language="ru",
                    access_level="employee",
                    updated_at="2026-09-15",
                ),
                source="hr/leave_policy.md",
            )
        ]


@pytest.fixture
def test_app():
    """Provide the application with isolated test dependencies."""
    app.dependency_overrides[get_rag_service] = lambda: FakeRAGService()
    app.dependency_overrides[get_retrieval_service] = (
        lambda: FakeRetrievalService()
    )

    yield app

    app.dependency_overrides.clear()


def test_health_endpoint(test_app) -> None:
    """Return application health information."""
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_endpoint(test_app) -> None:
    """Return an answer and its knowledge source."""
    client = TestClient(app)

    response = client.post(
        "/chat",
        json={"query": "Как оформить отпуск?"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Ответ на: Как оформить отпуск?",
        "sources": [
            {
                "document_id": "hr-leave",
                "title": "Политика отпусков",
                "source": "hr/leave_policy.md",
            }
        ],
    }


def test_search_endpoint(test_app) -> None:
    """Return retrieved knowledge base chunks."""
    client = TestClient(app)

    response = client.post(
        "/search",
        json={"query": "Как оформить отпуск?"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "results": [
            {
                "chunk_id": "chunk-001",
                "document_id": "hr-leave",
                "title": "Политика отпусков",
                "source": "hr/leave_policy.md",
                "content": "Сотрудник может оформить ежегодный отпуск.",
                "distance": 0.42,
            }
        ]
    }
