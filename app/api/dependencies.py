"""FastAPI dependencies for application services."""

from functools import lru_cache

from app.application.rag.service import RAGService
from app.application.retrieval.service import RetrievalService
from app.infrastructure.config.settings import get_settings
from app.infrastructure.rag import build_rag_service, build_retrieval_service


@lru_cache(maxsize=1)
def get_retrieval_service() -> RetrievalService:
    """Return cached retrieval service."""
    return build_retrieval_service(get_settings())


@lru_cache(maxsize=1)
def get_rag_service() -> RAGService:
    """Return cached RAG service."""
    return build_rag_service(get_settings())
