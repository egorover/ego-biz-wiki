"""Application service for retrieval-augmented generation."""

from typing import Protocol

from app.domain.rag import RAGResponse, RAGSource
from app.domain.retrieval import RetrievedChunk


FALLBACK_ANSWER = (
    "В базе знаний не найдено достаточно информации "
    "для достоверного ответа на этот вопрос."
)


class RAGLLMProvider(Protocol):
    """Generate grounded answers from retrieved knowledge."""

    def generate(
        self,
        query: str,
        context: str,
    ) -> str:
        """Generate an answer using the supplied knowledge context."""
        ...


class RAGRetrievalService(Protocol):
    """Retrieve knowledge chunks relevant to a user query."""

    def retrieve(self, query: str) -> list[RetrievedChunk]:
        """Return relevant knowledge chunks."""
        ...


class RAGService:
    """Coordinate retrieval and grounded answer generation."""

    def __init__(
        self,
        retrieval_service: RAGRetrievalService,
        llm_provider: RAGLLMProvider,
    ) -> None:
        self._retrieval_service = retrieval_service
        self._llm_provider = llm_provider

    def answer(self, query: str) -> RAGResponse:
        """Generate a grounded answer for a user query."""
        normalized_query = query.strip()

        if not normalized_query:
            raise ValueError("query must not be empty.")

        chunks = self._retrieval_service.retrieve(normalized_query)

        if not chunks:
            return RAGResponse(
                answer=FALLBACK_ANSWER,
                sources=[],
            )

        context = self._build_context(chunks)
        answer = self._llm_provider.generate(
            query=normalized_query,
            context=context,
        ).strip()

        if not answer or answer == FALLBACK_ANSWER:
            return RAGResponse(
                answer=FALLBACK_ANSWER,
                sources=[],
            )

        sources = self._build_sources(chunks)

        return RAGResponse(
            answer=answer,
            sources=sources,
        )

    @staticmethod
    def _build_context(chunks: list[RetrievedChunk]) -> str:
        """Build a grounded context block from retrieved chunks."""
        sections = []

        for index, chunk in enumerate(chunks, start=1):
            sections.append(
                f"[Source {index}]\n"
                f"Title: {chunk.metadata.title}\n"
                f"Source: {chunk.source}\n"
                f"Content:\n{chunk.content}"
            )

        return "\n\n".join(sections)

    @staticmethod
    def _build_sources(
        chunks: list[RetrievedChunk],
    ) -> list[RAGSource]:
        """Convert retrieved chunks into response sources."""
        sources: list[RAGSource] = []
        seen: set[str] = set()

        for chunk in chunks:
            if chunk.document_id in seen:
                continue

            seen.add(chunk.document_id)
            sources.append(
                RAGSource(
                    document_id=chunk.document_id,
                    source=chunk.source,
                    title=chunk.metadata.title,
                )
            )

        return sources