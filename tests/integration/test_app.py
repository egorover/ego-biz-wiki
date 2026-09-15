"""Integration tests for the FastAPI application."""

from fastapi.testclient import TestClient

from app.api.dependencies import get_rag_service
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


app.dependency_overrides[get_rag_service] = lambda: FakeRAGService()


def test_health_endpoint() -> None:
    """Return application health information."""
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_endpoint() -> None:
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