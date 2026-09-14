"""Token-aware Markdown chunking."""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.domain.chunk import DocumentChunk
from app.domain.document import Document


class TokenAwareChunker:
    """Split documents into deterministic token-sized chunks."""

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive.")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be >= 0 and smaller than chunk_size.")

        self._splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name="cl100k_base",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def split(self, document: Document) -> list[DocumentChunk]:
        """Return deterministic chunks for a loaded document."""
        parts = self._splitter.split_text(document.content)
        return [
            DocumentChunk(
                chunk_id=f"{document.metadata.document_id}:{index}",
                document_id=document.metadata.document_id,
                chunk_index=index,
                content=part,
                metadata=document.metadata,
            )
            for index, part in enumerate(parts)
            if part.strip()
        ]
