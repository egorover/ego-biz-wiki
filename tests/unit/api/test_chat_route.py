"""Tests for the chat API route."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import get_rag_service
from app.api.routes.chat import router
from app.domain.rag import RAGResponse, RAGSource


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


def create_test_app() -> FastAPI:
    """Create a FastAPI application for route testing."""
    application = FastAPI()
    application.dependency_overrides[get_rag_service] = (
        lambda: FakeRAGService()
    )
    application.include_router(router)
    return application


def test_chat_route_returns_answer_and_sources() -> None:
    """Return the generated answer and knowledge sources."""
    client = TestClient(create_test_app())

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


def test_chat_route_rejects_empty_query() -> None:
    """Reject an empty chat query."""
    client = TestClient(create_test_app())

    response = client.post(
        "/chat",
        json={"query": ""},
    )

    assert response.status_code == 422