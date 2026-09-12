"""Tests for the health endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    """Health endpoint should return the expected public contract."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "EgoBiz Wiki",
        "version": "0.1.0",
    }


def test_health_contract_has_no_extra_fields() -> None:
    """Health response should expose only its documented fields."""
    response = client.get("/health")

    assert set(response.json()) == {"status", "service", "version"}
