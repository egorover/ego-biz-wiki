"""Schemas for chat endpoints."""

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)


class ChatSource(BaseModel):
    """Knowledge-base source returned with an answer."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    title: str
    source: str


class ChatResponse(BaseModel):
    """Response returned by the chat endpoint."""

    model_config = ConfigDict(extra="forbid")

    answer: str
    sources: list[ChatSource]