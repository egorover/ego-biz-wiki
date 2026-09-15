"""Integration test for retrieval with a real Chroma collection."""

from pathlib import Path
from typing import Sequence

from app.domain.document import DocumentMetadata
from app.domain.chunk import DocumentChunk
from app.infrastructure.vector_store.chroma import ChromaVectorStore


class FakeEmbeddings:
    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        """Generate deterministic document embeddings."""
        vectors = {
            "Как оформить отпуск?": [1.0, 0.0, 0.0],
            "Как подключиться к VPN?": [0.0, 1.0, 0.0],
        }
        return [vectors[text] for text in texts]

    def embed_query(self, query: str) -> list[float]:
        """Generate a deterministic query embedding."""
        vectors = {
            "Как оформить отпуск?": [1.0, 0.0, 0.0],
            "Как подключиться к VPN?": [0.0, 1.0, 0.0],
        }
        return vectors[query]


def make_metadata(
    document_id: str,
    path: str,
    title: str,
    source: str,
) -> DocumentMetadata:
    """Create test document metadata."""
    return DocumentMetadata(
        document_id=document_id,
        path=path,
        title=title,
        category="it",
        subcategory="policy",
        source=source,
        version="1.0",
        language="ru",
        access_level="internal",
        updated_at="2026-09-01",
    )


def make_chunk(
    document_id: str,
    chunk_index: int,
    content: str,
    metadata: DocumentMetadata,
) -> DocumentChunk:
    """Create a document chunk for Chroma indexing."""
    return DocumentChunk(
        chunk_id=f"{document_id}:{chunk_index}",
        document_id=document_id,
        content=content,
        metadata=metadata,
        chunk_index=chunk_index,
    )


def test_chroma_retrieval_returns_nearest_chunks(tmp_path: Path) -> None:
    """Verify Chroma stores and retrieves chunks with metadata."""
    store = ChromaVectorStore(
        persist_directory=tmp_path / ".chroma",
        collection_name="retrieval_test",
    )

    vacation_metadata = make_metadata(
        document_id="hr-vacation",
        path="hr/vacation.md",
        title="Отпуск",
        source="HR / Отпуск",
    )
    vpn_metadata = make_metadata(
        document_id="it-vpn",
        path="it/vpn.md",
        title="VPN",
        source="IT / VPN",
    )

    chunks = [
        make_chunk(
            document_id="hr-vacation",
            chunk_index=0,
            content="Для оформления отпуска подайте заявление.",
            metadata=vacation_metadata,
        ),
        make_chunk(
            document_id="it-vpn",
            chunk_index=0,
            content="Для подключения к VPN используйте корпоративный клиент.",
            metadata=vpn_metadata,
        ),
    ]

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ]

    store.upsert(chunks, embeddings)

    result = store.query(
        embedding=[1.0, 0.0, 0.0],
        n_results=1,
    )

    assert len(result) == 1
    assert result[0].chunk_id == "hr-vacation:0"
    assert result[0].document_id == "hr-vacation"
    assert result[0].content == "Для оформления отпуска подайте заявление."
    assert result[0].metadata.title == "Отпуск"
    assert result[0].source == "HR / Отпуск"


def test_chroma_retrieval_returns_empty_for_empty_collection(
    tmp_path: Path,
) -> None:
    """Verify retrieval from an empty Chroma collection."""
    store = ChromaVectorStore(
        persist_directory=tmp_path / ".chroma",
        collection_name="empty_retrieval_test",
    )

    result = store.query(
        embedding=[1.0, 0.0, 0.0],
        n_results=5,
    )

    assert result == []