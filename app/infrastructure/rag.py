"""Infrastructure factory for the RAG service."""

from app.application.rag.service import RAGService
from app.application.retrieval.service import RetrievalService
from app.infrastructure.config.settings import Settings
from app.infrastructure.embeddings.openai import OpenAIEmbeddingProvider
from app.infrastructure.llm.openai import OpenAILLMProvider
from app.infrastructure.vector_store.chroma import ChromaVectorStore


def build_rag_service(settings: Settings) -> RAGService:
    """Build the RAG service from application infrastructure."""
    embedding_provider = OpenAIEmbeddingProvider(settings)
    vector_store = ChromaVectorStore(
        persist_directory=settings.chroma_persist_directory,
        collection_name=settings.chroma_collection,
    )
    retrieval_service = RetrievalService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        top_k=settings.retrieval_top_k,
        score_threshold=settings.retrieval_score_threshold,
    )
    llm_provider = OpenAILLMProvider(settings)

    return RAGService(
        retrieval_service=retrieval_service,
        llm_provider=llm_provider,
    )