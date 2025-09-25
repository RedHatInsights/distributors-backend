"""Tests for health check routes."""

from fastapi.testclient import TestClient


def test_health_root(client: TestClient):
    """Test the root health endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "success"}


def test_health_livez(client: TestClient):
    """Test the livez health endpoint."""
    response = client.get("/livez")
    assert response.status_code == 200
    assert response.json() == {"status": "success"}


def test_health_readyz(client: TestClient):
    """Test the readyz health endpoint."""
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "success"}
