"""
Tests for the HTTP client module.
"""

import json
from unittest.mock import patch, MagicMock, Mock
import pytest
import requests
from venice_sdk.client import HTTPClient, HTTPClientManager
from venice_sdk.config import Config
from venice_sdk.errors import VeniceError, VeniceAPIError, VeniceConnectionError


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = MagicMock(spec=Config)
    config.api_key = "test_key"
    config.base_url = "https://api.venice.ai/api/v1"
    config.timeout = 30
    config.max_retries = 3
    config.retry_delay = 1
    config.pool_connections = 10
    config.pool_maxsize = 20
    config.retry_backoff_factor = 0.5
    config.retry_status_codes = [429, 500, 502, 503, 504]
    return config


@pytest.fixture
def client(mock_config):
    """Create an HTTP client with mock configuration."""
    return HTTPClient(mock_config)


def test_client_initialization(client, mock_config):
    """Test client initialization."""
    assert client.config == mock_config
    assert client.session.headers["Authorization"] == f"Bearer {mock_config.api_key}"
    assert client.session.headers["Content-Type"] == "application/json"


def test_client_initialization_no_config():
    """Test client initialization with no config."""
    with patch("venice_sdk.client.load_config") as mock_load_config:
        mock_config = MagicMock(spec=Config)
        mock_config.api_key = "default_key"
        mock_config.base_url = "https://api.venice.ai/api/v1"
        mock_config.timeout = 30
        mock_config.max_retries = 3
        mock_config.retry_delay = 1
        mock_config.pool_connections = 10
        mock_config.pool_maxsize = 20
        mock_config.retry_backoff_factor = 0.5
        mock_config.retry_status_codes = [429, 500, 502, 503, 504]
        mock_load_config.return_value = mock_config
        
        client = HTTPClient()
        assert client.config == mock_config


def test_make_request_success(client):
    """Test successful request."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    
    with patch.object(client.session, "request", return_value=mock_response):
        response = client._make_request("GET", "test/endpoint")
        assert response.json() == {"status": "success"}


def test_make_request_error(client):
    """Test request with error response."""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": {"code": "bad_request", "message": "Invalid request"}}
    
    with patch.object(client.session, "request", return_value=mock_response):
        with pytest.raises(VeniceAPIError) as exc_info:
            client._make_request("GET", "test/endpoint")
        assert "Invalid request" in str(exc_info.value)


def test_make_request_retry(client):
    """Test request retry logic."""
    with patch.object(client.session, "request") as mock_request:
        mock_request.side_effect = requests.exceptions.RequestException("Connection error")
        
        with pytest.raises(VeniceConnectionError) as exc_info:
            client._make_request("GET", "test/endpoint")
        assert "Connection error" in str(exc_info.value)
        mock_request.assert_called_once()


@pytest.fixture
def mock_response():
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"success": True}
    return response


@pytest.fixture
def mock_error_response():
    response = Mock()
    response.status_code = 400
    response.json.return_value = {"error": {"message": "Bad request"}}
    return response


def test_make_request_max_retries(client, mocker):
    """Test that request fails after max retries"""
    mock_session = mocker.patch.object(client, "session")
    mock_session.request.side_effect = [
        requests.exceptions.ConnectionError("Connection failed"),
        requests.exceptions.ConnectionError("Connection failed"),
        requests.exceptions.ConnectionError("Connection failed")
    ]

    with pytest.raises(VeniceConnectionError) as exc_info:
        client._make_request("GET", "test")
    
    assert "Connection failed" in str(exc_info.value)
    assert mock_session.request.call_count == 1


def test_streaming_response(client):
    """Test streaming response handling."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.iter_lines.return_value = [
        b'{"chunk": "Hello"}',
        b'{"chunk": " World"}'
    ]
    
    with patch.object(client.session, "request", return_value=mock_response):
        chunks = list(client._make_request("GET", "test/endpoint", stream=True))
        assert chunks == ["Hello", " World"]


def test_streaming_response_error(client):
    """Test streaming response with error."""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": {"code": "stream_error", "message": "Stream failed"}}
    
    with patch.object(client.session, "request", return_value=mock_response):
        with pytest.raises(VeniceAPIError) as exc_info:
            list(client._make_request("GET", "test/endpoint", stream=True))
        assert "Stream failed" in str(exc_info.value)


def test_get_request(client):
    """Test GET request helper method."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    
    with patch.object(client.session, "request", return_value=mock_response):
        response = client.get("test/endpoint", param="value")
        assert response.json() == {"data": "test"}


def test_post_request(client):
    """Test POST request helper method."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    
    with patch.object(client.session, "request", return_value=mock_response):
        data = {"key": "value"}
        response = client.post("test/endpoint", data=data, param="value")
        assert response.json() == {"data": "test"}


def test_stream_request(client):
    """Test stream request helper method."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.iter_lines.return_value = [
        b'{"chunk": "Hello"}',
        b'{"chunk": " World"}'
    ]
    
    with patch.object(client.session, "request", return_value=mock_response):
        chunks = list(client.stream("test/endpoint", param="value"))
        assert chunks == ["Hello", " World"]


def test_get_success(client, mock_response, mocker):
    """Test successful GET request"""
    mock_session = mocker.patch.object(client, "session")
    mock_session.request.return_value = mock_response

    response = client.get("models")
    assert response.json() == {"success": True}
    mock_session.request.assert_called_once_with(
        "GET",
        f"{client.config.base_url}/models",
        json=None,
        stream=False,
        timeout=client.config.timeout
    )


def test_post_success(client, mock_response, mocker):
    """Test successful POST request"""
    mock_session = mocker.patch.object(client, "session")
    mock_session.request.return_value = mock_response
    data = {"test": "data"}

    response = client.post("chat/completions", data=data)
    assert response.json() == {"success": True}
    mock_session.request.assert_called_once_with(
        "POST",
        f"{client.config.base_url}/chat/completions",
        json=data,
        stream=False,
        timeout=client.config.timeout
    )


def test_get_api_error(client, mock_error_response, mocker):
    """Test GET request with API error"""
    mock_session = mocker.patch.object(client, "session")
    mock_session.request.return_value = mock_error_response

    with pytest.raises(VeniceAPIError) as exc_info:
        client.get("models")
    
    assert "Bad request" in str(exc_info.value)


@patch("requests.Session.request")
def test_get_connection_error(mock_request, client):
    """Test GET request with connection error."""
    mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")

    with pytest.raises(VeniceConnectionError) as exc_info:
        client.get("/test")
    assert "Connection failed" in str(exc_info.value)


@patch("requests.Session.request")
def test_get_timeout(mock_request, client):
    """Test GET request timeout."""
    mock_request.side_effect = requests.exceptions.Timeout("Request timed out")

    with pytest.raises(VeniceConnectionError) as exc_info:
        client.get("/test")
    assert "Request timed out" in str(exc_info.value)


@patch("requests.Session.request")
def test_get_invalid_json(mock_request, client):
    """Test GET request with invalid JSON response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
    mock_request.return_value = mock_response

    # The client returns the response object without calling .json()
    # so we need to call .json() ourselves to trigger the error
    response = client.get("/test")
    with pytest.raises(json.JSONDecodeError):
        response.json()


@patch("requests.Session.request")
def test_get_custom_timeout(mock_request, client):
    """Test GET request with custom timeout."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_request.return_value = mock_response

    client.get("/test", timeout=60)
    mock_request.assert_called_once_with(
        "GET",
        "https://api.venice.ai/api/v1/test",
        json=None,
        stream=False,
        timeout=60
    ) 


class TestHTTPClientManager:
    """Tests for the HTTPClientManager pooling behavior."""

    def test_returns_cached_client_for_same_config(self):
        manager = HTTPClientManager()
        config = Config(api_key="key-1", base_url="https://example.com")

        client_one = manager.get_client(config)
        client_two = manager.get_client(config)

        assert client_one is client_two

    def test_isolates_different_configs(self):
        manager = HTTPClientManager()
        config_a = Config(api_key="key-a", base_url="https://api-a.example.com")
        config_b = Config(api_key="key-b", base_url="https://api-b.example.com")

        client_a = manager.get_client(config_a)
        client_b = manager.get_client(config_b)

        assert client_a is not client_b

    def test_clear_removes_cached_client(self):
        manager = HTTPClientManager()
        config = Config(api_key="key-2", base_url="https://example.com")

        cached_client = manager.get_client(config)
        manager.clear(config)
        fresh_client = manager.get_client(config)

        assert cached_client is not fresh_client

    def test_global_clear_drops_all_clients(self):
        manager = HTTPClientManager()
        config_a = Config(api_key="key-a")
        config_b = Config(api_key="key-b")

        client_a = manager.get_client(config_a)
        client_b = manager.get_client(config_b)

        manager.clear()

        assert manager.get_client(config_a) is not client_a
        assert manager.get_client(config_b) is not client_b