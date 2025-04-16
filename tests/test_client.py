"""
Tests for the HTTP client module.
"""

import json
from unittest.mock import patch, MagicMock, Mock
import pytest
import requests
from venice_sdk.client import HTTPClient
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
    mock_success = MagicMock()
    mock_success.status_code = 200
    mock_success.json.return_value = {"status": "success"}
    
    with patch.object(client.session, "request") as mock_request:
        mock_request.side_effect = [
            requests.exceptions.RequestException("Connection error"),
            mock_success
        ]
        
        response = client._make_request("GET", "test/endpoint")
        assert response.json() == {"status": "success"}
        assert mock_request.call_count == 2


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
    mock_session = mocker.patch.object(client, "_session")
    mock_session.request.side_effect = [
        requests.exceptions.ConnectionError("Connection failed"),
        requests.exceptions.ConnectionError("Connection failed"),
        requests.exceptions.ConnectionError("Connection failed")
    ]

    with pytest.raises(VeniceConnectionError) as exc_info:
        client._make_request("GET", "test")
    
    assert "Failed to connect after 3 attempts" in str(exc_info.value)
    assert mock_session.request.call_count == 3


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
    mock_session = mocker.patch.object(client, "_session")
    mock_session.request.return_value = mock_response

    response = client.get("models")
    assert response.json() == {"success": True}
    mock_session.request.assert_called_once_with(
        "GET",
        f"{client.config.base_url}/models",
        headers=client._headers,
        timeout=client.config.timeout
    )


def test_post_success(client, mock_response, mocker):
    """Test successful POST request"""
    mock_session = mocker.patch.object(client, "_session")
    mock_session.request.return_value = mock_response
    data = {"test": "data"}

    response = client.post("chat/completions", data=data)
    assert response.json() == {"success": True}
    mock_session.request.assert_called_once_with(
        "POST",
        f"{client.config.base_url}/chat/completions",
        headers=client._headers,
        json=data,
        timeout=client.config.timeout
    )


def test_get_api_error(client, mock_error_response, mocker):
    """Test GET request with API error"""
    mock_session = mocker.patch.object(client, "_session")
    mock_session.request.return_value = mock_error_response

    with pytest.raises(VeniceAPIError) as exc_info:
        client.get("models")
    
    assert "Bad request" in str(exc_info.value)


@patch("requests.Session.get")
def test_get_connection_error(mock_get, client):
    """Test GET request with connection error."""
    mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

    with pytest.raises(VeniceConnectionError) as exc_info:
        client.get("/test")
    assert "Connection failed" in str(exc_info.value)


@patch("requests.Session.get")
def test_get_timeout(mock_get, client):
    """Test GET request timeout."""
    mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

    with pytest.raises(VeniceConnectionError) as exc_info:
        client.get("/test")
    assert "Request timed out" in str(exc_info.value)


@patch("requests.Session.get")
def test_get_invalid_json(mock_get, client):
    """Test GET request with invalid JSON response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
    mock_get.return_value = mock_response

    with pytest.raises(VeniceError) as exc_info:
        client.get("/test")
    assert "Invalid JSON response" in str(exc_info.value)


@patch("requests.Session.get")
def test_get_custom_timeout(mock_get, client):
    """Test GET request with custom timeout."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_get.return_value = mock_response

    client.get("/test", timeout=60)
    mock_get.assert_called_once_with(
        "https://api.venice.ai/api/v1/test",
        params=None,
        timeout=60
    ) 