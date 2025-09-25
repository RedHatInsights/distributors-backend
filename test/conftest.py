"""Pytest configuration and fixtures."""

import os
import pytest
from unittest.mock import Mock

# Force test environment variables to override any existing ones
os.environ["SALESFORCE_DOMAIN"] = "test-domain"
os.environ["SALESFORCE_USERNAME"] = "test@example.com"
os.environ["SALESFORCE_CONSUMER_KEY"] = "test-consumer-key"
os.environ["SALESFORCE_KEYSTORE_PATH"] = "/test/path/keystore.jks"
os.environ["SALESFORCE_KEYSTORE_PASSWORD"] = "test-keystore-password"
os.environ["SALESFORCE_CERT_ALIAS"] = "test-alias"
os.environ["SALESFORCE_CERT_PASSWORD"] = "test-cert-password"

from fastapi.testclient import TestClient
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
