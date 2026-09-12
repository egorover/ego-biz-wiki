"""Tests for application configuration."""

from app.infrastructure.config.settings import Settings


def test_settings_defaults() -> None:
    """Default settings should describe the local development application."""
    settings = Settings()

    assert settings.app_name == "EgoBiz Wiki"
    assert settings.app_version == "0.1.0"
    assert settings.app_env == "development"
    assert settings.log_level == "INFO"


def test_settings_accept_environment_overrides(monkeypatch) -> None:
    """Environment variables should override configuration defaults."""
    monkeypatch.setenv("APP_NAME", "Test Wiki")
    monkeypatch.setenv("APP_VERSION", "9.9.9")

    settings = Settings()

    assert settings.app_name == "Test Wiki"
    assert settings.app_version == "9.9.9"
