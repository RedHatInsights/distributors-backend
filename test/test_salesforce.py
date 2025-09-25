"""Tests for Salesforce service."""

import pytest
from unittest.mock import patch, Mock
from simple_salesforce import Salesforce

from src.services.salesforce import execute_apex, _get_salesforce, _get_private_key


class TestSalesforceService:
    """Test Salesforce service functions."""

    @patch("src.services.salesforce._get_salesforce")
    def test_execute_apex_success(self, mock_get_salesforce):
        """Test successful Apex execution."""
        # Arrange
        mock_sf = Mock(spec=Salesforce)
        mock_response = {"result": "success", "data": [{"id": "123"}]}
        mock_sf.apexecute.return_value = mock_response
        mock_get_salesforce.return_value = mock_sf

        endpoint = "test/endpoint"
        method = "GET"
        data = {"param": "value"}

        # Act
        result = execute_apex(endpoint, method, data)

        # Assert
        assert result == mock_response
        mock_get_salesforce.assert_called_once()
        mock_sf.apexecute.assert_called_once_with(endpoint, method=method, data=data)

    @patch("src.services.salesforce._get_salesforce")
    def test_execute_apex_with_post_method(self, mock_get_salesforce):
        """Test Apex execution with POST method."""
        # Arrange
        mock_sf = Mock(spec=Salesforce)
        mock_response = {"created": True, "id": "new123"}
        mock_sf.apexecute.return_value = mock_response
        mock_get_salesforce.return_value = mock_sf

        endpoint = "create/record"
        method = "POST"
        data = {"name": "Test Record", "type": "Account"}

        # Act
        result = execute_apex(endpoint, method, data)

        # Assert
        assert result == mock_response
        mock_sf.apexecute.assert_called_once_with(endpoint, method=method, data=data)

    @patch("src.services.salesforce._get_salesforce")
    def test_execute_apex_handles_salesforce_exception(self, mock_get_salesforce):
        """Test that Salesforce exceptions are propagated."""
        # Arrange
        mock_sf = Mock(spec=Salesforce)
        mock_sf.apexecute.side_effect = Exception("Salesforce API Error")
        mock_get_salesforce.return_value = mock_sf

        # Act & Assert
        with pytest.raises(Exception, match="Salesforce API Error"):
            execute_apex("test/endpoint", "GET", {})

    @patch("src.services.salesforce._get_private_key")
    @patch("src.services.salesforce.Salesforce")
    def test_get_salesforce_success(self, mock_salesforce_class, mock_get_private_key):
        """Test successful Salesforce connection creation."""
        # Arrange
        mock_private_key = (
            "-----BEGIN PRIVATE KEY-----\ntest_key\n-----END PRIVATE KEY-----"
        )
        mock_get_private_key.return_value = mock_private_key

        mock_sf_instance = Mock(spec=Salesforce)
        mock_salesforce_class.return_value = mock_sf_instance

        # Act
        result = _get_salesforce()

        # Assert
        assert result == mock_sf_instance
        mock_get_private_key.assert_called_once()
        mock_salesforce_class.assert_called_once_with(
            domain="test-domain",
            username="test@example.com",
            consumer_key="test-consumer-key",
            privatekey=mock_private_key,
        )

    @patch("src.services.salesforce._get_private_key")
    @patch("src.services.salesforce.constants")
    @patch("src.services.salesforce.Salesforce")
    def test_get_salesforce_with_different_domain(
        self, mock_salesforce_class, mock_constants, mock_get_private_key
    ):
        """Test Salesforce connection with different domain."""
        # Arrange
        mock_private_key = (
            "-----BEGIN PRIVATE KEY-----\nother_key\n-----END PRIVATE KEY-----"
        )
        mock_get_private_key.return_value = mock_private_key

        mock_constants.SALESFORCE_DOMAIN = "production"
        mock_constants.SALESFORCE_USERNAME = "prod@company.com"
        mock_constants.SALESFORCE_CONSUMER_KEY.get_secret_value.return_value = (
            "prod_consumer_key"
        )

        mock_sf_instance = Mock(spec=Salesforce)
        mock_salesforce_class.return_value = mock_sf_instance

        # Act
        _get_salesforce()

        # Assert
        mock_salesforce_class.assert_called_once_with(
            domain="production",
            username="prod@company.com",
            consumer_key="prod_consumer_key",
            privatekey=mock_private_key,
        )

    @patch("src.services.salesforce.jks")
    @patch("src.services.salesforce.constants")
    def test_get_private_key_success(self, mock_constants, mock_jks):
        """Test successful private key extraction."""
        # Arrange
        mock_keystore = Mock()
        mock_pk_entry = Mock()
        mock_keystore.private_keys = {"test_alias": mock_pk_entry}

        mock_constants.SALESFORCE_KEYSTORE_PATH = "/path/to/keystore.jks"
        mock_constants.SALESFORCE_KEYSTORE_PASSWORD.get_secret_value.return_value = (
            "keystore_pass"
        )
        mock_constants.SALESFORCE_CERT_ALIAS = "test_alias"
        mock_constants.SALESFORCE_CERT_PASSWORD.get_secret_value.return_value = (
            "cert_pass"
        )

        mock_jks.KeyStore.load.return_value = mock_keystore
        mock_jks.pkey_as_pem.return_value = (
            "-----BEGIN PRIVATE KEY-----\npem_key\n-----END PRIVATE KEY-----"
        )

        # Act
        result = _get_private_key()

        # Assert
        assert (
            result == "-----BEGIN PRIVATE KEY-----\npem_key\n-----END PRIVATE KEY-----"
        )
        mock_jks.KeyStore.load.assert_called_once_with(
            "/path/to/keystore.jks", "keystore_pass"
        )
        mock_pk_entry.decrypt.assert_called_once_with("cert_pass")
        mock_jks.pkey_as_pem.assert_called_once_with(mock_pk_entry)

    @patch("src.services.salesforce.jks")
    @patch("src.services.salesforce.constants")
    def test_get_private_key_keystore_load_error(self, mock_constants, mock_jks):
        """Test handling of keystore loading errors."""
        # Arrange
        mock_constants.SALESFORCE_KEYSTORE_PATH = "/invalid/path.jks"
        mock_constants.SALESFORCE_KEYSTORE_PASSWORD.get_secret_value.return_value = (
            "wrong_pass"
        )

        mock_jks.KeyStore.load.side_effect = Exception("Keystore load failed")

        # Act & Assert
        with pytest.raises(Exception, match="Keystore load failed"):
            _get_private_key()

    @patch("src.services.salesforce.jks")
    @patch("src.services.salesforce.constants")
    def test_get_private_key_missing_alias(self, mock_constants, mock_jks):
        """Test handling of missing certificate alias."""
        # Arrange
        mock_keystore = Mock()
        mock_keystore.private_keys = {}  # Empty dict, no aliases

        mock_constants.SALESFORCE_KEYSTORE_PATH = "/path/to/keystore.jks"
        mock_constants.SALESFORCE_KEYSTORE_PASSWORD.get_secret_value.return_value = (
            "keystore_pass"
        )
        mock_constants.SALESFORCE_CERT_ALIAS = "missing_alias"

        mock_jks.KeyStore.load.return_value = mock_keystore

        # Act & Assert
        with pytest.raises(KeyError):
            _get_private_key()

    @patch("src.services.salesforce.jks")
    @patch("src.services.salesforce.constants")
    def test_get_private_key_decrypt_error(self, mock_constants, mock_jks):
        """Test handling of certificate decryption errors."""
        # Arrange
        mock_keystore = Mock()
        mock_pk_entry = Mock()
        mock_pk_entry.decrypt.side_effect = Exception("Decryption failed")
        mock_keystore.private_keys = {"test_alias": mock_pk_entry}

        mock_constants.SALESFORCE_KEYSTORE_PATH = "/path/to/keystore.jks"
        mock_constants.SALESFORCE_KEYSTORE_PASSWORD.get_secret_value.return_value = (
            "keystore_pass"
        )
        mock_constants.SALESFORCE_CERT_ALIAS = "test_alias"
        mock_constants.SALESFORCE_CERT_PASSWORD.get_secret_value.return_value = (
            "wrong_cert_pass"
        )

        mock_jks.KeyStore.load.return_value = mock_keystore

        # Act & Assert
        with pytest.raises(Exception, match="Decryption failed"):
            _get_private_key()


class TestSalesforceIntegration:
    """Integration tests for Salesforce service."""

    @patch("src.services.salesforce.jks")
    @patch("src.services.salesforce.constants")
    @patch("src.services.salesforce.Salesforce")
    def test_end_to_end_apex_execution(
        self, mock_salesforce_class, mock_constants, mock_jks
    ):
        """Test complete flow from execute_apex to Salesforce API call."""
        # Arrange
        # Mock keystore and private key extraction
        mock_keystore = Mock()
        mock_pk_entry = Mock()
        mock_keystore.private_keys = {"cert_alias": mock_pk_entry}
        mock_jks.KeyStore.load.return_value = mock_keystore
        mock_jks.pkey_as_pem.return_value = (
            "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----"
        )

        # Mock constants
        mock_constants.SALESFORCE_KEYSTORE_PATH = "/path/to/keystore.jks"
        mock_constants.SALESFORCE_KEYSTORE_PASSWORD.get_secret_value.return_value = (
            "keystore_pass"
        )
        mock_constants.SALESFORCE_CERT_ALIAS = "cert_alias"
        mock_constants.SALESFORCE_CERT_PASSWORD.get_secret_value.return_value = (
            "cert_pass"
        )
        mock_constants.SALESFORCE_DOMAIN = "test"
        mock_constants.SALESFORCE_USERNAME = "test@example.com"
        mock_constants.SALESFORCE_CONSUMER_KEY.get_secret_value.return_value = (
            "consumer_key"
        )

        # Mock Salesforce instance
        mock_sf = Mock(spec=Salesforce)
        mock_sf.apexecute.return_value = {"success": True, "data": "test_data"}
        mock_salesforce_class.return_value = mock_sf

        # Act
        result = execute_apex("test/endpoint", "GET", {"param": "value"})

        # Assert
        assert result == {"success": True, "data": "test_data"}

        # Verify the full chain of calls
        mock_jks.KeyStore.load.assert_called_once()
        mock_pk_entry.decrypt.assert_called_once()
        mock_salesforce_class.assert_called_once()
        mock_sf.apexecute.assert_called_once_with(
            "test/endpoint", method="GET", data={"param": "value"}
        )
