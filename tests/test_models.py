"""
Tests for the models module.
"""

from unittest.mock import patch, MagicMock
import pytest
from venice_sdk.models import ModelsAPI
from venice_sdk.errors import VeniceAPIError


@pytest.fixture
def mock_client():
    """Create a mock HTTP client."""
    client = MagicMock()
    return client


@pytest.fixture
def models_api(mock_client):
    """Create a ModelsAPI instance."""
    return ModelsAPI(mock_client)


def test_models_api_initialization(models_api, mock_client):
    """Test ModelsAPI initialization."""
    assert models_api.client == mock_client


def test_list_models_success(models_api, mock_client):
    """Test successful model listing."""
    mock_response = {
        "data": [
            {
                "id": "llama-3.3-70b",
                "object": "model",
                "created": 1677652288,
                "owned_by": "venice",
                "permission": [],
                "root": "llama-3.3-70b",
                "parent": None
            },
            {
                "id": "llama-3.3-13b",
                "object": "model",
                "created": 1677652288,
                "owned_by": "venice",
                "permission": [],
                "root": "llama-3.3-13b",
                "parent": None
            }
        ]
    }
    mock_client.get.return_value = mock_response

    models = models_api.list()
    assert len(models) == 2
    assert models[0]["id"] == "llama-3.3-70b"
    assert models[1]["id"] == "llama-3.3-13b"
    mock_client.get.assert_called_once_with("/models")


def test_list_models_api_error(models_api, mock_client):
    """Test model listing with API error."""
    mock_client.get.side_effect = VeniceAPIError("API error occurred")

    with pytest.raises(VeniceAPIError) as exc_info:
        models_api.list()
    assert "API error occurred" in str(exc_info.value)


def test_get_model_success(models_api, mock_client):
    """Test successful model retrieval."""
    mock_response = {
        "id": "llama-3.3-70b",
        "object": "model",
        "created": 1677652288,
        "owned_by": "venice",
        "permission": [],
        "root": "llama-3.3-70b",
        "parent": None
    }
    mock_client.get.return_value = mock_response

    model = models_api.get("llama-3.3-70b")
    assert model["id"] == "llama-3.3-70b"
    mock_client.get.assert_called_once_with("/models/llama-3.3-70b")


def test_get_model_not_found(models_api, mock_client):
    """Test model retrieval for non-existent model."""
    mock_client.get.side_effect = VeniceAPIError("Model not found", status_code=404)

    with pytest.raises(VeniceAPIError) as exc_info:
        models_api.get("non-existent-model")
    assert "Model not found" in str(exc_info.value)


def test_validate_model_success(models_api, mock_client):
    """Test successful model validation."""
    mock_response = {
        "id": "llama-3.3-70b",
        "object": "model",
        "created": 1677652288,
        "owned_by": "venice",
        "permission": [],
        "root": "llama-3.3-70b",
        "parent": None
    }
    mock_client.get.return_value = mock_response

    assert models_api.validate("llama-3.3-70b") is True
    mock_client.get.assert_called_once_with("/models/llama-3.3-70b")


def test_validate_model_failure(models_api, mock_client):
    """Test model validation for non-existent model."""
    mock_client.get.side_effect = VeniceAPIError("Model not found", status_code=404)

    assert models_api.validate("non-existent-model") is False
    mock_client.get.assert_called_once_with("/models/non-existent-model") 