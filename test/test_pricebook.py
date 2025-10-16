"""Tests for pricebook routes."""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from test.conftest import get_api_endpoint


class TestPricebookRoutes:
    """Test pricebook API endpoints."""

    @patch("src.routes.pricebook.salesforce.execute_apex")
    def test_get_pricebook_list(
        self, mock_execute_apex, authenticated_client: TestClient
    ):
        """Test the pricebook list endpoint."""
        mock_response = {"pricebooks": [{"id": "123", "name": "Test Pricebook"}]}
        mock_execute_apex.return_value = mock_response

        response = authenticated_client.get(f"{get_api_endpoint()}/PricebookList")

        assert response.status_code == 200
        assert response.json() == mock_response
        mock_execute_apex.assert_called_once_with(
            "partnerpricebook/pricebooklist", "GET", {"mdmId": "MDM-12345"}
        )

    @patch("src.routes.pricebook.salesforce.execute_apex")
    def test_get_pricebook(self, mock_execute_apex, authenticated_client: TestClient):
        """Test the get pricebook by ID endpoint."""
        pricebook_id = "pb123"
        mock_response = {"id": pricebook_id, "name": "Test Pricebook", "items": []}
        mock_execute_apex.return_value = mock_response

        response = authenticated_client.get(
            f"{get_api_endpoint()}/Pricebook?pricebookId={pricebook_id}"
        )

        assert response.status_code == 200
        assert response.json() == mock_response
        mock_execute_apex.assert_called_once_with(
            "partnerpricebook/pricebook",
            "GET",
            {"mdmId": "MDM-12345", "pricebookId": pricebook_id},
        )

    @patch("src.routes.pricebook.salesforce.execute_apex")
    def test_get_pricebook_change_summary(
        self, mock_execute_apex, authenticated_client: TestClient
    ):
        """Test the pricebook change summary endpoint."""
        pricebook_id = "pb123"
        mock_response = {"changes": [{"type": "added", "item": "product1"}]}
        mock_execute_apex.return_value = mock_response

        response = authenticated_client.get(
            f"{get_api_endpoint()}/PricebookChangeSummary?pricebookId={pricebook_id}"
        )

        assert response.status_code == 200
        assert response.json() == mock_response
        mock_execute_apex.assert_called_once_with(
            "partnerpricebook/pricebookchangesummary",
            "GET",
            {"mdmId": "MDM-12345", "pricebookId": pricebook_id},
        )

    @patch("src.routes.pricebook.salesforce.execute_apex")
    def test_get_discount_bands(
        self, mock_execute_apex, authenticated_client: TestClient
    ):
        """Test the discount bands endpoint."""
        mock_response = {"bands": [{"tier": "gold", "discount": 0.15}]}
        mock_execute_apex.return_value = mock_response

        response = authenticated_client.get(f"{get_api_endpoint()}/DiscountBands")

        assert response.status_code == 200
        assert response.json() == mock_response
        mock_execute_apex.assert_called_once_with(
            "partnerpricebook/discountbands", "GET", {"mdmId": "MDM-12345"}
        )

    def test_get_pricebook_missing_id(self, authenticated_client: TestClient):
        """Test that pricebook endpoint requires pricebookId parameter."""
        response = authenticated_client.get(f"{get_api_endpoint()}/Pricebook")

        assert response.status_code == 422  # Validation error

    def test_get_pricebook_change_summary_missing_id(
        self, authenticated_client: TestClient
    ):
        """Test that change summary endpoint requires pricebookId parameter."""
        response = authenticated_client.get(
            f"{get_api_endpoint()}/PricebookChangeSummary"
        )

        assert response.status_code == 422  # Validation error

    @patch("src.routes.pricebook.salesforce.execute_apex")
    def test_salesforce_error_handling(
        self, mock_execute_apex, authenticated_client: TestClient
    ):
        """Test handling of Salesforce service errors."""
        mock_execute_apex.side_effect = Exception("Salesforce connection error")

        with pytest.raises(Exception, match="Salesforce connection error"):
            authenticated_client.get(f"{get_api_endpoint()}/PricebookList")
