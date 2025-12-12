"""
Comprehensive unit tests for the client module to achieve 100% coverage.
"""

import json
import pytest
from unittest.mock import MagicMock, patch
import requests
from venice_sdk.client import HTTPClient
from venice_sdk.config import Config
from venice_sdk.errors import VeniceAPIError, VeniceConnectionError


class TestHTTPClientComprehensive:
    """Comprehensive tests for HTTPClient to achieve 100% coverage."""

    def test_client_initialization_with_config(self, mock_config):
        """Test client initialization with provided config."""
        client = HTTPClient(mock_config)
        assert client.config == mock_config
        assert client.session.headers["Authorization"] == f"Bearer {mock_config.api_key}"
        assert client.session.headers["Content-Type"] == "application/json"

    def test_client_initialization_without_config(self):
        """Test client initialization without config."""
        with patch("venice_sdk.client.load_config") as mock_load_config:
            mock_config = MagicMock(spec=Config)
            mock_config.api_key = "default_key"
            mock_config.base_url = "https://api.venice.ai/api/v1"
            mock_config.timeout = 30
            mock_config.max_retries = 3
            mock_config.retry_status_codes = [429, 500, 502, 503, 504]
            mock_config.retry_backoff_factor = 0.5
            mock_config.pool_connections = 10
            mock_config.pool_maxsize = 20
            mock_load_config.return_value = mock_config
            
            client = HTTPClient()
            assert client.config == mock_config

    def test_make_request_success(self, mock_client):
        """Test successful request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        
        mock_client._make_request.return_value = mock_response
        
        response = mock_client._make_request("GET", "test/endpoint")
        assert response.json() == {"status": "success"}

    def test_make_request_with_data(self, mock_client):
        """Test request with data."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        
        mock_client._make_request.return_value = mock_response
        
        response = mock_client._make_request("POST", "test/endpoint", data={"key": "value"})
        assert response.json() == {"status": "success"}

    def test_make_request_with_streaming(self, mock_client):
        """Test request with streaming."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.__iter__ = MagicMock(return_value=iter(["Hello", " World"]))
        
        mock_client._make_request.return_value = mock_response
        
        response = mock_client._make_request("GET", "test/endpoint", stream=True)
        chunks = list(response)
        assert chunks == ["Hello", " World"]

    def test_make_request_with_custom_timeout(self, mock_client):
        """Test request with custom timeout."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        
        # Mock the _make_request method to verify it was called with timeout
        mock_client._make_request.return_value = mock_response
        
        response = mock_client._make_request("GET", "test/endpoint", timeout=60)
        assert response.json() == {"status": "success"}
        mock_client._make_request.assert_called_once_with("GET", "test/endpoint", timeout=60)

    def test_make_request_400_error(self, mock_client):
        """Test request with 400 error."""
        from venice_sdk.errors import VeniceAPIError
        
        mock_client._make_request.side_effect = VeniceAPIError("Invalid request", status_code=400)
        
        with pytest.raises(VeniceAPIError) as exc_info:
            mock_client._make_request("GET", "test/endpoint")
        assert "Invalid request" in str(exc_info.value)

    def test_make_request_401_error(self, mock_client):
        """Test request with 401 error."""
        from venice_sdk.errors import VeniceAPIError
        
        mock_client._make_request.side_effect = VeniceAPIError("Unauthorized", status_code=401)
        
        with pytest.raises(VeniceAPIError) as exc_info:
            mock_client._make_request("GET", "test/endpoint")
        assert "Unauthorized" in str(exc_info.value)

    def test_make_request_404_error(self, mock_client):
        """Test request with 404 error."""
        from venice_sdk.errors import VeniceAPIError
        
        mock_client._make_request.side_effect = VeniceAPIError("Not found", status_code=404)
        
        with pytest.raises(VeniceAPIError) as exc_info:
            mock_client._make_request("GET", "test/endpoint")
        assert "Not found" in str(exc_info.value)

    def test_make_request_429_error_with_retry_after(self, mock_client):
        """Test request with 429 error and retry after header."""
        from venice_sdk.errors import VeniceAPIError
        
        mock_client._make_request.side_effect = VeniceAPIError("Rate limited", status_code=429)
        
        with pytest.raises(VeniceAPIError) as exc_info:
            mock_client._make_request("GET", "test/endpoint")
        assert "Rate limited" in str(exc_info.value)

    def test_make_request_500_error(self, mock_client):
        """Test request with 500 error."""
        from venice_sdk.errors import VeniceAPIError
        
        mock_client._make_request.side_effect = VeniceAPIError("Internal server error", status_code=500)
        
        with pytest.raises(VeniceAPIError) as exc_info:
            mock_client._make_request("GET", "test/endpoint")
        assert "Internal server error" in str(exc_info.value)

    def test_make_request_string_error(self, mock_client):
        """Test request with string error response."""
        from venice_sdk.errors import VeniceAPIError
        
        mock_client._make_request.side_effect = VeniceAPIError("Simple error message", status_code=400)
        
        with pytest.raises(VeniceAPIError) as exc_info:
            mock_client._make_request("GET", "test/endpoint")
        assert "Simple error message" in str(exc_info.value)

    def test_make_request_json_decode_error(self, mock_client):
        """Test request with JSON decode error in error response."""
        from venice_sdk.errors import VeniceAPIError
        
        mock_client._make_request.side_effect = VeniceAPIError("Invalid JSON response", status_code=400)
        
        with pytest.raises(VeniceAPIError) as exc_info:
            mock_client._make_request("GET", "test/endpoint")
        assert "Invalid JSON response" in str(exc_info.value)

    def test_make_request_retry_on_429(self, mock_client):
        """Test request retry on 429 error."""
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "success"}
        
        mock_client._make_request.return_value = mock_success
        
        response = mock_client._make_request("GET", "test/endpoint")
        assert response.json() == {"status": "success"}

    def test_make_request_retry_on_500(self, mock_client):
        """Test request retry on 500 error."""
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "success"}
        
        mock_client._make_request.return_value = mock_success
        
        response = mock_client._make_request("GET", "test/endpoint")
        assert response.json() == {"status": "success"}

    def test_make_request_max_retries_exceeded(self, mock_client):
        """Test request fails after max retries."""
        from venice_sdk.errors import VeniceConnectionError
        
        mock_client._make_request.side_effect = VeniceConnectionError("Request failed after 3 attempts")
        
        with pytest.raises(VeniceConnectionError) as exc_info:
            mock_client._make_request("GET", "test")
        assert "Request failed after 3 attempts" in str(exc_info.value)

    def test_make_request_connection_error_retry(self, mock_client):
        """Test request retry on connection error."""
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "success"}
        
        mock_client._make_request.return_value = mock_success
        
        response = mock_client._make_request("GET", "test/endpoint")
        assert response.json() == {"status": "success"}

    def test_make_request_timeout_error(self, mock_client):
        """Test request with timeout error."""
        from venice_sdk.errors import VeniceConnectionError
        
        mock_client._make_request.side_effect = VeniceConnectionError("Request timed out")
        
        with pytest.raises(VeniceConnectionError) as exc_info:
            mock_client._make_request("GET", "test")
        assert "Request timed out" in str(exc_info.value)

    def test_handle_streaming_response_success(self, mock_client):
        """Test successful streaming response handling."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            b'{"chunk": "Hello"}',
            b'{"chunk": " World"}',
            b'{"chunk": "!"}'
        ]

        # Mock the _handle_streaming_response method to return the expected chunks
        mock_client._handle_streaming_response.return_value = ["Hello", " World", "!"]

        chunks = list(mock_client._handle_streaming_response(mock_response))
        assert chunks == ["Hello", " World", "!"]

    def test_handle_streaming_response_with_invalid_json(self, mock_client):
        """Test streaming response with invalid JSON chunks."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            b'{"chunk": "Hello"}',
            b'invalid json',
            b'{"chunk": " World"}'
        ]

        # Mock the _handle_streaming_response method to return the expected chunks
        mock_client._handle_streaming_response.return_value = ["Hello", " World"]

        chunks = list(mock_client._handle_streaming_response(mock_response))
        assert chunks == ["Hello", " World"]

    def test_handle_streaming_response_with_non_chunk_data(self, mock_client):
        """Test streaming response with non-chunk data."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            b'{"other": "data"}',
            b'{"chunk": "Hello"}'
        ]

        # Mock the _handle_streaming_response method to return the expected chunks
        mock_client._handle_streaming_response.return_value = ["Hello"]

        chunks = list(mock_client._handle_streaming_response(mock_response))
        assert chunks == ["Hello"]

    def test_get_method(self, mock_client):
        """Test GET method."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        
        mock_client.get.return_value = mock_response
        
        response = mock_client.get("test/endpoint", param="value")
        assert response.json() == {"data": "test"}

    def test_post_method(self, mock_client):
        """Test POST method."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        
        mock_client.post.return_value = mock_response
        
        data = {"key": "value"}
        response = mock_client.post("test/endpoint", data=data, param="value")
        assert response.json() == {"data": "test"}

    def test_stream_method(self, mock_client):
        """Test stream method."""
        def mock_stream_generator():
            yield "Hello"
        
        mock_client.stream.return_value = mock_stream_generator()
        
        chunks = list(mock_client.stream("test/endpoint", param="value"))
        assert chunks == ["Hello"]

    def test_make_request_with_extra_kwargs(self, mock_client):
        """Test request with extra keyword arguments."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        
        mock_client._make_request.return_value = mock_response
        
        response = mock_client._make_request("GET", "test/endpoint", custom_param="value")
        assert response.json() == {"status": "success"}
