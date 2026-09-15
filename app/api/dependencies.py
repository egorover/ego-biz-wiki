"""FastAPI dependencies for application services."""

from functools import lru_cache

from app.application.rag.service import RAGService
from app.infrastructure.config.settings import get_settings
from app.infrastructure.rag import build_rag_service


@lru_cache(maxsize=1)
def get_rag_service() -> RAGService:
    """Return the application-wide RAG service."""
    return build_rag_service(get_settings())