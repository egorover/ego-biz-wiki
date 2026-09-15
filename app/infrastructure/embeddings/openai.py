"""OpenAI-compatible embeddings provider."""

from collections.abc import Sequence

from langchain_openai import OpenAIEmbeddings

from app.infrastructure.config.settings import Settings


class OpenAIEmbeddingProvider:
    """Generate embeddings through an OpenAI-compatible endpoint."""

    def __init__(self, settings: Settings) -> None:
        api_key = settings.openai_api_key.get_secret_value().strip()
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for indexing.")

        self._embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=api_key,
            base_url=settings.openai_base_url,
            chunk_size=settings.embedding_batch_size,
        )

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        """Generate embeddings for the supplied texts."""
        return self._embeddings.embed_documents(list(texts))

    def embed_query(self, query: str) -> list[float]:
        """Generate an embedding for a single query."""
        return self._embeddings.embed_query(query)