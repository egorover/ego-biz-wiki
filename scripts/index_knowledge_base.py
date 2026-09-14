"""Index the EgoBiz Wiki knowledge base."""

import logging
from pathlib import Path

from app.application.indexing.service import IndexingService
from app.infrastructure.config.settings import get_settings
from app.infrastructure.embeddings.openai import OpenAIEmbeddingProvider
from app.infrastructure.indexing.chunker import TokenAwareChunker
from app.infrastructure.indexing.manifest import ManifestLoader
from app.infrastructure.loaders.markdown import MarkdownLoader
from app.infrastructure.vector_store.chroma import ChromaVectorStore

logger = logging.getLogger(__name__)


def build_indexing_service(project_root: Path) -> IndexingService:
    """Build the production indexing pipeline from application settings."""
    settings = get_settings()
    knowledge_base = project_root / settings.knowledge_base_path
    manifest_path = knowledge_base / settings.manifest_filename

    embedding_provider = OpenAIEmbeddingProvider(settings)
    vector_store = ChromaVectorStore(
        persist_directory=project_root / settings.chroma_persist_directory,
        collection_name=settings.chroma_collection,
    )

    return IndexingService(
        metadata_provider=ManifestLoader(manifest_path),
        document_loader=MarkdownLoader(),
        chunker=TokenAwareChunker(settings.chunk_size, settings.chunk_overlap),
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        knowledge_base=knowledge_base,
    )


def main() -> None:
    """Run indexing and print a concise summary."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    project_root = Path(__file__).resolve().parents[1]
    service = build_indexing_service(project_root)
    result = service.run()

    logger.info("Documents loaded: %s", result.documents_count)
    logger.info("Chunks created: %s", result.chunks_count)
    logger.info("Indexing completed successfully")


if __name__ == "__main__":
    main()
