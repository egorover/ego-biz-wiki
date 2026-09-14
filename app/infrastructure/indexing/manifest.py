"""Knowledge base manifest loading."""

from pathlib import Path
import yaml

from app.domain.document import DocumentMetadata


class ManifestError(ValueError):
    """Raised when the knowledge base manifest is invalid."""


class ManifestLoader:
    """Load and validate document metadata from manifest.yaml."""

    def __init__(self, manifest_path: Path) -> None:
        self._manifest_path = manifest_path
        self._knowledge_base = manifest_path.parent

    def load(self) -> list[DocumentMetadata]:
        """Return validated metadata entries from the manifest."""
        try:
            payload = yaml.safe_load(self._manifest_path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            raise ManifestError(
                f"Failed to read manifest: {self._manifest_path}"
            ) from exc

        if not isinstance(payload, dict) or not isinstance(
            payload.get("documents"), list
        ):
            raise ManifestError("Manifest must contain a 'documents' list.")

        result: list[DocumentMetadata] = []
        seen_ids: set[str] = set()
        seen_paths: set[str] = set()

        for raw_item in payload["documents"]:
            if not isinstance(raw_item, dict):
                raise ManifestError("Each manifest document must be a mapping.")

            try:
                metadata = DocumentMetadata.model_validate(raw_item)
            except Exception as exc:
                raise ManifestError("Invalid document metadata in manifest.") from exc

            relative_path = Path(metadata.path)
            if relative_path.is_absolute() or ".." in relative_path.parts:
                raise ManifestError(
                    f"Manifest path must stay inside knowledge_base: {metadata.path}"
                )

            if metadata.document_id in seen_ids:
                raise ManifestError(
                    f"Duplicate document_id: {metadata.document_id}"
                )
            if metadata.path in seen_paths:
                raise ManifestError(f"Duplicate document path: {metadata.path}")

            document_path = self._knowledge_base / relative_path
            if not document_path.is_file():
                raise ManifestError(
                    f"Document referenced by manifest does not exist: "
                    f"{metadata.path}"
                )

            seen_ids.add(metadata.document_id)
            seen_paths.add(metadata.path)
            result.append(metadata)

        return result
