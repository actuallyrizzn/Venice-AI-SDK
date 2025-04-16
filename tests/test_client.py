"""
Tests for the HTTP client module.
"""

import json
from unittest.mock import patch, MagicMock
import pytest
import requests
from venice_sdk.client import HTTPClient
from venice_sdk.errors import VeniceError, VeniceAPIError, VeniceConnectionError


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = MagicMock()
    config.api_key = "test_key"
    config.base_url = "https://api.venice.ai/api/v1"
    config.headers = {
        "Authorization": "Bearer test_key",
        "Content-Type": "application/json"
    }
    return config


@pytest.fixture
def client(mock_config):
    """Create an HTTP client instance."""
    return HTTPClient(mock_config)


def test_client_initialization(client, mock_config):
    """Test HTTP client initialization."""
    assert client.config == mock_config
    assert client.session.headers == mock_config.headers


@patch("requests.Session.get")
def test_get_success(mock_get, client):
    """Test successful GET request."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_get.return_value = mock_response

    response = client.get("/test")
    assert response == {"data": "test"}
    mock_get.assert_called_once_with(
        "https://api.venice.ai/api/v1/test",
        params=None,
        timeout=30
    )


@patch("requests.Session.post")
def test_post_success(mock_post, client):
    """Test successful POST request."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_post.return_value = mock_response

    data = {"key": "value"}
    response = client.post("/test", data)
    assert response == {"data": "test"}
    mock_post.assert_called_once_with(
        "https://api.venice.ai/api/v1/test",
        data=json.dumps(data),
        timeout=30
    )


@patch("requests.Session.get")
def test_get_api_error(mock_get, client):
    """Test GET request with API error."""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": "Bad request"}
    mock_get.return_value = mock_response

    with pytest.raises(VeniceAPIError) as exc_info:
        client.get("/test")
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