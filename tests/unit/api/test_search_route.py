"""Tests for the search API route."""

from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.api.dependencies import get_retrieval_service
from app.domain.document import DocumentMetadata
from app.domain.retrieval import RetrievedChunk
from app.main import app


def test_search_returns_retrieved_chunks() -> None:
    """Return retrieved chunks as search results."""
    retrieval_service = Mock()
    retrieval_service.retrieve.return_value = [
        RetrievedChunk(
            chunk_id="chunk-001",
            document_id="vacation-policy",
            content="Сотрудник может оформить ежегодный отпуск.",
            distance=0.42,
            metadata=DocumentMetadata(
                document_id="vacation-policy",
                path="knowledge_base/hr/vacation_policy.md",
                title="Vacation Policy",
                category="HR",
                subcategory="Vacation",
                source="internal",
                version="1.0",
                language="ru",
                access_level="employee",
                updated_at="2026-09-15",
            ),
            source="knowledge_base/hr/vacation_policy.md",
        )
    ]

    app.dependency_overrides[get_retrieval_service] = lambda: retrieval_service

    try:
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
                    "document_id": "vacation-policy",
                    "title": "Vacation Policy",
                    "source": "knowledge_base/hr/vacation_policy.md",
                    "content": "Сотрудник может оформить ежегодный отпуск.",
                    "distance": 0.42,
                }
            ]
        }
        retrieval_service.retrieve.assert_called_once_with(
            "Как оформить отпуск?"
        )
    finally:
        app.dependency_overrides.pop(get_retrieval_service, None)


def test_search_returns_empty_results() -> None:
    """Return an empty result list when nothing is retrieved."""
    retrieval_service = Mock()
    retrieval_service.retrieve.return_value = []

    app.dependency_overrides[get_retrieval_service] = lambda: retrieval_service

    try:
        client = TestClient(app)

        response = client.post(
            "/search",
            json={"query": "Как заказать домик на Марсе?"},
        )

        assert response.status_code == 200
        assert response.json() == {"results": []}
        retrieval_service.retrieve.assert_called_once_with(
            "Как заказать домик на Марсе?"
        )
    finally:
        app.dependency_overrides.pop(get_retrieval_service, None)


def test_search_rejects_empty_query() -> None:
    """Reject an empty search query."""
    retrieval_service = Mock()

    app.dependency_overrides[get_retrieval_service] = lambda: retrieval_service

    try:
        client = TestClient(app)

        response = client.post(
            "/search",
            json={"query": ""},
        )

        assert response.status_code == 422
        retrieval_service.retrieve.assert_not_called()
    finally:
        app.dependency_overrides.pop(get_retrieval_service, None)
