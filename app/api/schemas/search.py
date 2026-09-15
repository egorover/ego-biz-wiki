"""API schemas for knowledge base search."""

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Request schema for knowledge base search."""

    query: str = Field(min_length=1)


class SearchResult(BaseModel):
    """Single search result."""

    chunk_id: str
    document_id: str
    title: str
    source: str
    content: str
    distance: float


class SearchResponse(BaseModel):
    """Response schema for knowledge base search."""

    results: list[SearchResult]
