"""Tests for the standardized knowledge base dataset."""

from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_BASE = PROJECT_ROOT / "knowledge_base"
MANIFEST = KNOWLEDGE_BASE / "manifest.yaml"
REQUIRED_FIELDS = {
    "document_id",
    "path",
    "title",
    "category",
    "subcategory",
    "source",
    "version",
    "language",
    "access_level",
    "updated_at",
}


def test_manifest_is_valid() -> None:
    """Validate manifest structure and document references."""
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    documents = data["documents"]

    assert isinstance(documents, list)
    assert documents
    assert len({item["document_id"] for item in documents}) == len(documents)
    assert len({item["path"] for item in documents}) == len(documents)

    for item in documents:
        assert REQUIRED_FIELDS <= item.keys()
        assert (KNOWLEDGE_BASE / item["path"]).is_file()
        assert item["language"] == "ru"
        assert item["access_level"] == "internal"


def test_all_markdown_documents_are_registered() -> None:
    """Ensure every Markdown document is registered in the manifest."""
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    registered = {
        item["path"]
        for item in data["documents"]
        if item["path"].endswith(".md")
    }
    actual = {
        path.relative_to(KNOWLEDGE_BASE).as_posix()
        for path in KNOWLEDGE_BASE.rglob("*.md")
    }

    assert actual == registered


def test_documents_are_non_empty() -> None:
    """Reject empty or obvious placeholder documents."""
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))

    for item in data["documents"]:
        content = (KNOWLEDGE_BASE / item["path"]).read_text(encoding="utf-8")
        assert len(content.strip()) >= 200
        assert "TODO" not in content
        assert "PLACEHOLDER" not in content.upper()
