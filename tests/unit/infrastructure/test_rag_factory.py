"""Tests for the RAG infrastructure factory."""

from unittest.mock import MagicMock, patch

from app.application.rag.service import RAGService
from app.infrastructure.config.settings import Settings
from app.infrastructure.rag import build_rag_service


def test_build_rag_service_creates_rag_service() -> None:
    """Build the RAG service from configured infrastructure."""
    settings = Settings(
        openai_api_key="test-key",
        chroma_persist_directory=".test-chroma",
    )

    with (
        patch(
            "app.infrastructure.rag.OpenAIEmbeddingProvider",
        ) as embedding_provider,
        patch(
            "app.infrastructure.rag.ChromaVectorStore",
        ) as vector_store,
        patch(
            "app.infrastructure.rag.OpenAILLMProvider",
        ) as llm_provider,
    ):
        service = build_rag_service(settings)

    assert isinstance(service, RAGService)

    embedding_provider.assert_called_once_with(settings)
    vector_store.assert_called_once_with(
        persist_directory=settings.chroma_persist_directory,
        collection_name=settings.chroma_collection,
    )
    llm_provider.assert_called_once_with(settings)


def test_build_rag_service_wires_retrieval_dependencies() -> None:
    """Wire embedding and vector-store providers into retrieval."""
    settings = Settings(
        openai_api_key="test-key",
        chroma_persist_directory=".test-chroma",
    )

    with (
        patch(
            "app.infrastructure.rag.OpenAIEmbeddingProvider",
        ),
        patch(
            "app.infrastructure.rag.ChromaVectorStore",
        ),
        patch(
            "app.infrastructure.rag.OpenAILLMProvider",
        ),
        patch(
            "app.infrastructure.rag.RetrievalService",
        ) as retrieval_service,
    ):
        build_rag_service(settings)

    retrieval_service.assert_called_once_with(
        embedding_provider=retrieval_service.call_args.kwargs[
            "embedding_provider"
        ],
        vector_store=retrieval_service.call_args.kwargs["vector_store"],
        top_k=settings.retrieval_top_k,
        score_threshold=settings.retrieval_score_threshold,
    )