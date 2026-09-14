"""Domain models for knowledge base documents."""

from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class DocumentMetadata(BaseModel):
    """Validated metadata describing a knowledge base document."""

    model_config = ConfigDict(extra="forbid")

    document_id: str = Field(min_length=1)
    path: str = Field(min_length=1)
    title: str = Field(min_length=1)
    category: str = Field(min_length=1)
    subcategory: str = Field(min_length=1)
    source: str = Field(min_length=1)
    version: str = Field(min_length=1)
    language: str = Field(min_length=1)
    access_level: str = Field(min_length=1)
    updated_at: str = Field(min_length=1)


@dataclass(frozen=True, slots=True)
class Document:
    """Loaded knowledge base document."""

    metadata: DocumentMetadata
    content: str
    source_path: Path
