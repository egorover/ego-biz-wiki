"""Integration test for indexing without an external embedding API."""

import pytest

pytest.importorskip("langchain_text_splitters")


from pathlib import Path
from typing import Sequence

import yaml

from app.application.indexing.service import IndexingService
from app.domain.chunk import DocumentChunk
from app.domain.document import Document
from app.infrastructure.indexing.chunker import TokenAwareChunker
from app.infrastructure.indexing.manifest import ManifestLoader
from app.infrastructure.loaders.markdown import MarkdownLoader


class FakeEmbeddings:
    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [[float(index), 1.0, 2.0] for index, _ in enumerate(texts)]


class MemoryVectorStore:
    def __init__(self) -> None:
        self.records: dict[str, tuple[str, Sequence[float], dict[str, str | int]]] = {}

    def upsert(
        self,
        chunks: Sequence[DocumentChunk],
        embeddings: Sequence[Sequence[float]],
    ) -> None:
        for chunk, embedding in zip(chunks, embeddings, strict=True):
            self.records[chunk.chunk_id] = (
                chunk.content,
                embedding,
                chunk.vector_metadata,
            )


def test_indexing_pipeline_loads_chunks_and_metadata(tmp_path: Path) -> None:
    knowledge_base = tmp_path / "knowledge_base"
    (knowledge_base / "hr").mkdir(parents=True)
    (knowledge_base / "hr" / "policy.md").write_text(
        "# Политика\n\n" + "Текст компании. " * 50,
        encoding="utf-8",
    )
    manifest = {
        "version": "1.0",
        "documents": [
            {
                "document_id": "hr-policy",
                "path": "hr/policy.md",
                "title": "Политика",
                "category": "hr",
                "subcategory": "policy",
                "source": "HR / Политика",
                "version": "1.0",
                "language": "ru",
                "access_level": "internal",
                "updated_at": "2026-09-01",
            }
        ],
    }
    (knowledge_base / "manifest.yaml").write_text(
        yaml.safe_dump(manifest, allow_unicode=True), encoding="utf-8"
    )

    store = MemoryVectorStore()
    service = IndexingService(
        metadata_provider=ManifestLoader(knowledge_base / "manifest.yaml"),
        document_loader=MarkdownLoader(),
        chunker=TokenAwareChunker(chunk_size=30, chunk_overlap=5),
        embedding_provider=FakeEmbeddings(),
        vector_store=store,
        knowledge_base=knowledge_base,
    )

    result = service.run()

    assert result.documents_count == 1
    assert result.chunks_count == len(store.records)
    assert store.records
    first = next(iter(store.records.values()))
    assert first[2]["document_id"] == "hr-policy"
    assert first[2]["path"] == "hr/policy.md"
