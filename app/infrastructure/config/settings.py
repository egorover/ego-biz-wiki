"""Application configuration."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables or .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="EgoBiz Wiki")
    app_version: str = Field(default="0.1.0")
    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")

    openai_api_key: SecretStr = Field(default=SecretStr(""))
    openai_base_url: str | None = Field(default=None)
    embedding_model: str = Field(default="text-embedding-3-small")
    embedding_batch_size: int = Field(default=100, ge=1)

    knowledge_base_path: Path = Field(default=Path("knowledge_base"))
    manifest_filename: str = Field(default="manifest.yaml")
    chroma_persist_directory: Path = Field(default=Path(".chroma"))
    chroma_collection: str = Field(default="ego_biz_wiki")

    chunk_size: int = Field(default=800, ge=1)
    chunk_overlap: int = Field(default=120, ge=0)

    def model_post_init(self, __context: object) -> None:
        """Validate chunking settings after model initialization."""
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings instance."""
    return Settings()
