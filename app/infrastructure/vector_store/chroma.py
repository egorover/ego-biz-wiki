"""Persistent Chroma vector-store adapter."""

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import chromadb

from app.domain.chunk import DocumentChunk
from app.domain.document import DocumentMetadata
from app.domain.retrieval import RetrievedChunk


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

    def query(
        self,
        embedding: Sequence[float],
        n_results: int,
    ) -> list[RetrievedChunk]:
        """Return nearest indexed chunks for a query embedding."""
        if n_results < 1:
            raise ValueError("n_results must be greater than zero.")

        if self._collection.count() == 0:
            return []

        result = self._collection.query(
            query_embeddings=[list(embedding)],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        ids = result["ids"][0]
        documents = result["documents"][0]
        metadatas = result["metadatas"][0]
        distances = result["distances"][0]

        retrieved: list[RetrievedChunk] = []

        for chunk_id, content, metadata, distance in zip(
            ids,
            documents,
            metadatas,
            distances,
            strict=True,
        ):
            if content is None or metadata is None or distance is None:
                continue

            metadata_values = dict(metadata)
            document_id = str(metadata_values.pop("document_id"))
            metadata_values.pop("chunk_index", None)

            document_metadata = DocumentMetadata.model_validate(
                {"document_id": document_id, **metadata_values}
            )

            retrieved.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    content=content,
                    distance=float(distance),
                    metadata=document_metadata,
                    source=document_metadata.source,
                )
            )

        return retrieved

    @staticmethod
    def _sanitize_metadata(metadata: dict[str, Any]) -> dict[str, str | int]:
        """Convert metadata to scalar values supported by Chroma."""
        return {
            key: value
            for key, value in metadata.items()
            if isinstance(value, (str, int, float, bool))
        }
