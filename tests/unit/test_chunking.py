"""Tests for deterministic token-aware chunking."""

from pathlib import Path

import pytest

pytest.importorskip("langchain_text_splitters")

from app.domain.document import Document, DocumentMetadata
from app.infrastructure.indexing.chunker import TokenAwareChunker


def make_document() -> Document:
    """Build a representative document for chunking tests."""
    metadata = DocumentMetadata(
        document_id="it-vpn",
        path="it/vpn.md",
        title="VPN",
        category="it",
        subcategory="remote_access",
        source="IT / VPN",
        version="1.0",
        language="ru",
        access_level="internal",
        updated_at="2026-09-01",
    )
    content = "\n\n".join(
        f"Раздел {index}: корпоративная информация." for index in range(100)
    )
    return Document(
        metadata=metadata,
        content=content,
        source_path=Path("it/vpn.md"),
    )


def test_chunk_ids_are_deterministic() -> None:
    document = make_document()
    chunker = TokenAwareChunker(chunk_size=30, chunk_overlap=5)

    first = chunker.split(document)
    second = chunker.split(document)

    assert [chunk.chunk_id for chunk in first] == [chunk.chunk_id for chunk in second]
    assert [chunk.chunk_index for chunk in first] == list(range(len(first)))
    assert first[0].chunk_id == "it-vpn:0"
    assert all(chunk.metadata.document_id == "it-vpn" for chunk in first)


def test_invalid_overlap_is_rejected() -> None:
    with pytest.raises(ValueError, match="smaller than chunk_size"):
        TokenAwareChunker(chunk_size=10, chunk_overlap=10)
