"""Tests for Markdown loading."""

from pathlib import Path

import pytest

from app.domain.document import DocumentMetadata
from app.infrastructure.loaders.markdown import MarkdownLoader


def make_metadata(path: str = "hr/policy.md") -> DocumentMetadata:
    """Build representative document metadata for tests."""
    return DocumentMetadata(
        document_id="hr-policy",
        path=path,
        title="Policy",
        category="hr",
        subcategory="policy",
        source="HR / Policy",
        version="1.0",
        language="ru",
        access_level="internal",
        updated_at="2026-09-01",
    )


def test_markdown_loader_reads_utf8(tmp_path: Path) -> None:
    (tmp_path / "hr").mkdir()
    path = tmp_path / "hr" / "policy.md"
    path.write_text("# Политика\n\nТекст на русском языке.", encoding="utf-8")

    document = MarkdownLoader().load(make_metadata(), tmp_path)

    assert document.content.startswith("# Политика")
    assert document.source_path == path


def test_markdown_loader_rejects_empty_file(tmp_path: Path) -> None:
    (tmp_path / "hr").mkdir()
    (tmp_path / "hr" / "policy.md").write_text("   ", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        MarkdownLoader().load(make_metadata(), tmp_path)
