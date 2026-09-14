"""Persistent Chroma vector-store adapter."""

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import chromadb

from app.domain.chunk import DocumentChunk


class ChromaVectorStore:
    """Persist indexed chunks in a local Chroma collection."""

    def __init__(self, persist_directory: Path, collection_name: str) -> None:
        persist_directory.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(persist_directory))
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
        )

    @property
    def count(self) -> int:
        """Return the number of records currently stored."""
        return self._collection.count()

    def upsert(
        self,
        chunks: Sequence[DocumentChunk],
        embeddings: Sequence[Sequence[float]],
    ) -> None:
        """Upsert chunks using deterministic IDs and supplied vectors."""
        if len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings must have equal lengths.")
        if not chunks:
            return

        batch_size = self._client.get_max_batch_size()
        for start in range(0, len(chunks), batch_size):
            chunk_batch = chunks[start : start + batch_size]
            embedding_batch = embeddings[start : start + batch_size]
            self._collection.upsert(
                ids=[chunk.chunk_id for chunk in chunk_batch],
                embeddings=[list(vector) for vector in embedding_batch],
                documents=[chunk.content for chunk in chunk_batch],
                metadatas=[
                    self._sanitize_metadata(chunk.vector_metadata)
                    for chunk in chunk_batch
                ],
            )

    @staticmethod
    def _sanitize_metadata(metadata: dict[str, Any]) -> dict[str, str | int]:
        """Convert metadata to scalar values supported by Chroma."""
        return {
            key: value
            for key, value in metadata.items()
            if isinstance(value, (str, int, float, bool))
        }
