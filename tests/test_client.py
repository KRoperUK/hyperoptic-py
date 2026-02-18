"""Tests for the Hyperoptic API client."""

from unittest.mock import MagicMock, Mock, patch

import pytest
from pydantic import ValidationError

from hyperoptic.client import HyperopticClient
from hyperoptic.exceptions import APIError
from hyperoptic.models import Account, Customer, Package


class TestHyperopticClient:
    """Test the main API client."""

    @patch("hyperoptic.client.HyperopticAuth")
    @patch("httpx.Client")
    def test_client_initialization(self, mock_http_class, mock_auth_class):
        """Test client initialization."""
        mock_http_class.return_value = Mock()
        mock_auth_class.return_value = Mock()

        client = HyperopticClient(email="test@example.com", password="secret")

        assert client._http is not None
        assert client._auth is not None

    @patch("hyperoptic.client.HyperopticAuth")
    @patch("httpx.Client")
    def test_client_context_manager(self, mock_http_class, mock_auth_class):
        """Test using client as a context manager."""
        mock_http = Mock()
        mock_auth = Mock()
        mock_http_class.return_value = mock_http
        mock_auth_class.return_value = mock_auth

        with HyperopticClient(email="test@example.com", password="secret") as client:
            assert client is not None

        mock_http.close.assert_called()
        mock_auth.close.assert_called()


class TestGetCustomers:
    """Test customer retrieval."""

    @patch("hyperoptic.client.HyperopticAuth")
    @patch("httpx.Client")
    def test_get_customers(self, mock_http_class, mock_auth_class, customer_response):
        """Test fetching customers."""
        mock_http = Mock()
        mock_auth = Mock()
        mock_auth.authorization_header = {"Authorization": "Bearer token"}

        mock_http_class.return_value = mock_http
        mock_auth_class.return_value = mock_auth

        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = customer_response
        mock_http.request.return_value = mock_response

        client = HyperopticClient(email="test@example.com", password="secret")
        customers = client.get_customers()

        assert len(customers) == 1
        assert isinstance(customers[0], Customer)
        assert customers[0].email == "kieranroper03@gmail.com"
        assert customers[0].full_name == "Kieran Roper"

    @patch("hyperoptic.client.HyperopticAuth")
    @patch("httpx.Client")
    def test_get_customers_empty(self, mock_http_class, mock_auth_class):
        """Test fetching when no customers exist."""
        mock_http = Mock()
        mock_auth = Mock()
        mock_auth.authorization_header = {"Authorization": "Bearer token"}

        mock_http_class.return_value = mock_http
        mock_auth_class.return_value = mock_auth

        # Mock empty response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"_embedded": {"customers": []}, "page": {}}
        mock_http.request.return_value = mock_response

        client = HyperopticClient(email="test@example.com", password="secret")
        customers = client.get_customers()

        assert customers == []

    @patch("hyperoptic.client.HyperopticAuth")
    @patch("httpx.Client")
    def test_get_customer(self, mock_http_class, mock_auth_class, customer_response):
        """Test getting the primary customer."""
        mock_http = Mock()
        mock_auth = Mock()
        mock_auth.authorization_header = {"Authorization": "Bearer token"}

        mock_http_class.return_value = mock_http
        mock_auth_class.return_value = mock_auth

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = customer_response
        mock_http.request.return_value = mock_response

        client = HyperopticClient(email="test@example.com", password="secret")
        customer = client.get_customer()

        assert isinstance(customer, Customer)
        assert customer.email == "kieranroper03@gmail.com"

    @patch("hyperoptic.client.HyperopticAuth")
    @patch("httpx.Client")
    def test_get_customer_no_customers(self, mock_http_class, mock_auth_class):
        """Test get_customer when no customers exist."""
        mock_http = Mock()
        mock_auth = Mock()
        mock_auth.authorization_header = {"Authorization": "Bearer token"}

        mock_http_class.return_value = mock_http
        mock_auth_class.return_value = mock_auth

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"_embedded": {"customers": []}, "page": {}}
        mock_http.request.return_value = mock_response

        client = HyperopticClient(email="test@example.com", password="secret")

        with pytest.raises(APIError) as exc_info:
            client.get_customer()
        assert "No customers" in str(exc_info.value)


class TestGetPackages:
    """Test package retrieval."""

    @patch("hyperoptic.client.HyperopticAuth")
    @patch("httpx.Client")
    def test_get_packages(self, mock_http_class, mock_auth_class, packages_response):
        """Test fetching packages for a customer."""
        mock_http = Mock()
        mock_auth = Mock()
        mock_auth.authorization_header = {"Authorization": "Bearer token"}

        mock_http_class.return_value = mock_http
        mock_auth_class.return_value = mock_auth

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = packages_response
        mock_http.request.return_value = mock_response

        client = HyperopticClient(email="test@example.com", password="secret")
        packages = client.get_packages("07e3793f-0418-476e-a9c0-98fad1060b3f")

        assert len(packages) == 1
        assert isinstance(packages[0], Package)
        assert packages[0].bundle_name == "1Gb Fibre Connection - Broadband"
        assert packages[0].download_speed == 1000
        assert packages[0].upload_speed == 1000

    @patch("hyperoptic.client.HyperopticAuth")
    @patch("httpx.Client")
    def test_get_packages_with_sort(
        self, mock_http_class, mock_auth_class, packages_response
    ):
        """Test get_packages with custom sort parameter."""
        mock_http = Mock()
        mock_auth = Mock()
        mock_auth.authorization_header = {"Authorization": "Bearer token"}

        mock_http_class.return_value = mock_http
        mock_auth_class.return_value = mock_auth

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = packages_response
        mock_http.request.return_value = mock_response

        client = HyperopticClient(email="test@example.com", password="secret")
        packages = client.get_packages("customer-id", sort="startDate,asc")

        # Verify the sort parameter was passed
        call_args = mock_http.request.call_args
        assert "startDate,asc" in str(call_args)


class TestGetConnections:
    """Test connection retrieval."""

    @patch("hyperoptic.client.HyperopticAuth")
    @patch("httpx.Client")
    def test_get_connection(
        self, mock_http_class, mock_auth_class, connection_response
    ):
        """Test fetching a single connection."""
        mock_http = Mock()
        mock_auth = Mock()
        mock_auth.authorization_header = {"Authorization": "Bearer token"}

        mock_http_class.return_value = mock_http
        mock_auth_class.return_value = mock_auth

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = connection_response
        mock_http.request.return_value = mock_response

        client = HyperopticClient(email="test@example.com", password="secret")
        conn = client.get_connection("b138123e-c047-4878-9960-adf3b5185700")

        assert conn["id"] == "b138123e-c047-4878-9960-adf3b5185700"
        assert conn["isInstalled"] is True

    @patch("hyperoptic.client.HyperopticAuth")
    @patch("httpx.Client")
    def test_get_my_connections(
        self,
        mock_http_class,
        mock_auth_class,
        customer_response,
        connection_response,
    ):
        """Test getting all connections for the primary customer."""
        mock_http = Mock()
        mock_auth = Mock()
        mock_auth.authorization_header = {"Authorization": "Bearer token"}

        mock_http_class.return_value = mock_http
        mock_auth_class.return_value = mock_auth

        # First call: get customer; second call: get connection
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = customer_response

        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = connection_response

        mock_http.request.side_effect = [mock_response1, mock_response2]

        client = HyperopticClient(email="test@example.com", password="secret")
        connections = client.get_my_connections()

        assert len(connections) == 1
        assert connections[0]["id"] == "b138123e-c047-4878-9960-adf3b5185700"


class TestErrorHandling:
    """Test error handling and retries."""

    @patch("hyperoptic.client.HyperopticAuth")
    @patch("httpx.Client")
    def test_api_error_400(self, mock_http_class, mock_auth_class):
        """Test handling of HTTP 400 errors."""
        mock_http = Mock()
        mock_auth = Mock()
        mock_auth.authorization_header = {"Authorization": "Bearer token"}

        mock_http_class.return_value = mock_http
        mock_auth_class.return_value = mock_auth

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_response.url = "https://api.example.com/endpoint"
        mock_http.request.return_value = mock_response

        client = HyperopticClient(email="test@example.com", password="secret")

        with pytest.raises(APIError) as exc_info:
            client.get_customers()
        assert exc_info.value.status_code == 400

    @patch("hyperoptic.client.HyperopticAuth")
    @patch("httpx.Client")
    def test_api_error_404(self, mock_http_class, mock_auth_class):
        """Test handling of HTTP 404 errors."""
        mock_http = Mock()
        mock_auth = Mock()
        mock_auth.authorization_header = {"Authorization": "Bearer token"}

        mock_http_class.return_value = mock_http
        mock_auth_class.return_value = mock_auth

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.url = "https://api.example.com/endpoint"
        mock_http.request.return_value = mock_response

        client = HyperopticClient(email="test@example.com", password="secret")

        with pytest.raises(APIError) as exc_info:
            client.get_customers()
        assert exc_info.value.status_code == 404

    @patch("hyperoptic.client.HyperopticAuth")
    @patch("httpx.Client")
    def test_401_triggers_reauthentication(
        self, mock_http_class, mock_auth_class, customer_response
    ):
        """Test that 401 triggers re-authentication."""
        mock_http = Mock()
        mock_auth = Mock()
        mock_auth.authorization_header = {"Authorization": "Bearer token"}
        mock_auth.login = Mock()

        mock_http_class.return_value = mock_http
        mock_auth_class.return_value = mock_auth

        # First call returns 401, second returns 200
        mock_response1 = Mock()
        mock_response1.status_code = 401
        mock_response1.text = "Unauthorized"

        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = customer_response

        mock_http.request.side_effect = [mock_response1, mock_response2]

        client = HyperopticClient(email="test@example.com", password="secret")
        customers = client.get_customers()

        # Should have called login to get a new token
        mock_auth.login.assert_called_once()
        assert len(customers) == 1

    @patch("hyperoptic.client.HyperopticAuth")
    @patch("httpx.Client")
    def test_api_error_500(self, mock_http_class, mock_auth_class):
        """Test handling of HTTP 500 errors."""
        mock_http = Mock()
        mock_auth = Mock()
        mock_auth.authorization_header = {"Authorization": "Bearer token"}

        mock_http_class.return_value = mock_http
        mock_auth_class.return_value = mock_auth

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_response.url = "https://api.example.com/endpoint"
        mock_http.request.return_value = mock_response

        client = HyperopticClient(email="test@example.com", password="secret")

        with pytest.raises(APIError) as exc_info:
            client.get_customers()
        assert exc_info.value.status_code == 500


class TestRawEndpoint:
    """Test the raw API endpoint."""

    @patch("hyperoptic.client.HyperopticAuth")
    @patch("httpx.Client")
    def test_get_raw(self, mock_http_class, mock_auth_class):
        """Test making raw API calls."""
        mock_http = Mock()
        mock_auth = Mock()
        mock_auth.authorization_header = {"Authorization": "Bearer token"}

        mock_http_class.return_value = mock_http
        mock_auth_class.return_value = mock_auth

        test_data = {"test": "data"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = test_data
        mock_http.request.return_value = mock_response

        client = HyperopticClient(email="test@example.com", password="secret")
        result = client.get_raw("/test-endpoint", param1="value1")

        assert result == test_data
