"""Search API routes."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_retrieval_service
from app.api.schemas.search import SearchRequest, SearchResponse, SearchResult
from app.application.retrieval.service import RetrievalService

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search(
    request: SearchRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
) -> SearchResponse:
    """Search the corporate knowledge base."""
    chunks = retrieval_service.retrieve(request.query)

    results = [
        SearchResult(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            title=chunk.metadata.title,
            source=chunk.source,
            content=chunk.content,
            distance=chunk.distance,
        )
        for chunk in chunks
    ]

    return SearchResponse(results=results)
