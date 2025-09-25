"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock

from src.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def authenticated_client():
    """Create a test client with basic auth credentials."""
    import base64

    client = TestClient(app)
    credentials = base64.b64encode(b"testuser:testpass").decode("ascii")
    client.headers.update({"Authorization": f"Basic {credentials}"})
    return client


@pytest.fixture
def mock_salesforce():
    """Mock salesforce service for testing."""
    return Mock()
