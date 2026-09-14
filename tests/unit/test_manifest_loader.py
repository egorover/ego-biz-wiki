"""Tests for manifest loading."""

from pathlib import Path

import pytest
import yaml

from app.infrastructure.indexing.manifest import ManifestError, ManifestLoader


def test_manifest_loader_returns_metadata(tmp_path: Path) -> None:
    knowledge_base = tmp_path / "knowledge_base"
    knowledge_base.mkdir()
    (knowledge_base / "hr").mkdir()
    document_path = knowledge_base / "hr" / "policy.md"
    document_path.write_text("# Policy\n\nContent", encoding="utf-8")
    manifest = {
        "version": "1.0",
        "documents": [
            {
                "document_id": "hr-policy",
                "path": "hr/policy.md",
                "title": "Policy",
                "category": "hr",
                "subcategory": "policy",
                "source": "HR / Policy",
                "version": "1.0",
                "language": "ru",
                "access_level": "internal",
                "updated_at": "2026-09-01",
            }
        ],
    }
    (knowledge_base / "manifest.yaml").write_text(
        yaml.safe_dump(manifest, allow_unicode=True), encoding="utf-8"
    )

    items = ManifestLoader(knowledge_base / "manifest.yaml").load()

    assert len(items) == 1
    assert items[0].document_id == "hr-policy"
    assert items[0].path == "hr/policy.md"


def test_manifest_loader_rejects_parent_traversal(tmp_path: Path) -> None:
    knowledge_base = tmp_path / "knowledge_base"
    knowledge_base.mkdir()
    manifest = {
        "documents": [
            {
                "document_id": "bad",
                "path": "../secret.md",
                "title": "Bad",
                "category": "x",
                "subcategory": "x",
                "source": "x",
                "version": "1.0",
                "language": "ru",
                "access_level": "internal",
                "updated_at": "2026-09-01",
            }
        ]
    }
    manifest_path = knowledge_base / "manifest.yaml"
    manifest_path.write_text(yaml.safe_dump(manifest), encoding="utf-8")

    with pytest.raises(ManifestError, match="stay inside"):
        ManifestLoader(manifest_path).load()
