"""
Tests for the models module.
"""

from unittest.mock import MagicMock, patch
import pytest
from venice_sdk.models import (
    Model,
    ModelCapabilities,
    ModelsAPI,
    get_models,
    get_model_by_id,
    get_text_models
)
from venice_sdk.errors import VeniceAPIError
from venice_sdk.client import HTTPClient


@pytest.fixture
def mock_client():
    """Create a mock HTTP client."""
    client = MagicMock(spec=HTTPClient)
    return client


@pytest.fixture
def models_api(mock_client):
    """Create a ModelsAPI instance."""
    return ModelsAPI(mock_client)


def test_model_capabilities_initialization():
    """Test ModelCapabilities initialization."""
    capabilities = ModelCapabilities(
        supports_function_calling=True,
        supports_web_search=True,
        available_context_tokens=4096
    )
    assert capabilities.supports_function_calling is True
    assert capabilities.supports_web_search is True
    assert capabilities.available_context_tokens == 4096


def test_model_initialization():
    """Test Model initialization."""
    capabilities = ModelCapabilities(
        supports_function_calling=True,
        supports_web_search=True,
        available_context_tokens=4096
    )
    model = Model(
        id="test-model",
        name="Test Model",
        type="text",
        capabilities=capabilities,
        description="A test model"
    )
    assert model.id == "test-model"
    assert model.name == "Test Model"
    assert model.type == "text"
    assert model.capabilities == capabilities
    assert model.description == "A test model"


def test_models_api_initialization(models_api, mock_client):
    """Test ModelsAPI initialization."""
    assert models_api.client == mock_client


def test_list_models_success(models_api, mock_client):
    """Test successful model listing."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {
                "id": "llama-3.3-70b",
                "name": "Llama 3.3 70B",
                "type": "text",
                "capabilities": {
                    "supports_function_calling": True,
                    "supports_web_search": True,
                    "available_context_tokens": 4096
                },
                "description": "A powerful language model"
            },
            {
                "id": "llama-3.3-13b",
                "name": "Llama 3.3 13B",
                "type": "text",
                "capabilities": {
                    "supports_function_calling": True,
                    "supports_web_search": True,
                    "available_context_tokens": 4096
                },
                "description": "A smaller language model"
            }
        ]
    }
    mock_client.get.return_value = mock_response

    models = models_api.list()
    assert len(models) == 2
    assert models[0]["id"] == "llama-3.3-70b"
    assert models[1]["id"] == "llama-3.3-13b"
    mock_client.get.assert_called_once_with("models")


def test_list_models_api_error(models_api, mock_client):
    """Test model listing with API error."""
    mock_client.get.side_effect = VeniceAPIError("API error occurred")

    with pytest.raises(VeniceAPIError) as exc_info:
        models_api.list()
    assert "API error occurred" in str(exc_info.value)


def test_get_model_success(models_api, mock_client):
    """Test successful model retrieval."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "llama-3.3-70b",
        "name": "Llama 3.3 70B",
        "type": "text",
        "capabilities": {
            "supports_function_calling": True,
            "supports_web_search": True,
            "available_context_tokens": 4096
        },
        "description": "A powerful language model"
    }
    mock_client.get.return_value = mock_response

    model = models_api.get("llama-3.3-70b")
    assert model["id"] == "llama-3.3-70b"
    assert model["name"] == "Llama 3.3 70B"
    mock_client.get.assert_called_once_with("models/llama-3.3-70b")


def test_get_model_not_found(models_api, mock_client):
    """Test model retrieval for non-existent model."""
    mock_client.get.side_effect = VeniceAPIError("Model not found", status_code=404)

    with pytest.raises(VeniceAPIError) as exc_info:
        models_api.get("non-existent-model")
    assert "Model not found" in str(exc_info.value)


def test_validate_model_success(models_api, mock_client):
    """Test successful model validation."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "llama-3.3-70b",
        "name": "Llama 3.3 70B",
        "type": "text",
        "capabilities": {
            "supports_function_calling": True,
            "supports_web_search": True,
            "available_context_tokens": 4096
        },
        "description": "A powerful language model"
    }
    mock_client.get.return_value = mock_response

    assert models_api.validate("llama-3.3-70b") is True
    mock_client.get.assert_called_once_with("models/llama-3.3-70b")


def test_validate_model_failure(models_api, mock_client):
    """Test model validation for non-existent model."""
    mock_client.get.side_effect = VeniceAPIError("Model not found", status_code=404)

    assert models_api.validate("non-existent-model") is False
    mock_client.get.assert_called_once_with("models/non-existent-model")


def test_get_models_utility(mock_client):
    """Test the get_models utility function."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {
                "id": "llama-3.3-70b",
                "name": "Llama 3.3 70B",
                "type": "text",
                "capabilities": {
                    "supports_function_calling": True,
                    "supports_web_search": True,
                    "available_context_tokens": 4096
                },
                "description": "A powerful language model"
            }
        ]
    }
    mock_client.get.return_value = mock_response

    with patch('venice_sdk.models.HTTPClient', return_value=mock_client):
        models = get_models()
        assert len(models) == 1
        assert isinstance(models[0], Model)
        assert models[0].id == "llama-3.3-70b"


def test_get_model_by_id_utility(mock_client):
    """Test the get_model_by_id utility function."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "llama-3.3-70b",
        "name": "Llama 3.3 70B",
        "type": "text",
        "capabilities": {
            "supports_function_calling": True,
            "supports_web_search": True,
            "available_context_tokens": 4096
        },
        "description": "A powerful language model"
    }
    mock_client.get.return_value = mock_response

    with patch('venice_sdk.models.HTTPClient', return_value=mock_client):
        model = get_model_by_id("llama-3.3-70b")
        assert isinstance(model, Model)
        assert model.id == "llama-3.3-70b"


def test_get_text_models_utility(mock_client):
    """Test the get_text_models utility function."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {
                "id": "llama-3.3-70b",
                "name": "Llama 3.3 70B",
                "type": "text",
                "capabilities": {
                    "supports_function_calling": True,
                    "supports_web_search": True,
                    "available_context_tokens": 4096
                },
                "description": "A powerful language model"
            },
            {
                "id": "image-model",
                "name": "Image Model",
                "type": "image",
                "capabilities": {
                    "supports_function_calling": False,
                    "supports_web_search": False,
                    "available_context_tokens": 0
                },
                "description": "An image model"
            }
        ]
    }
    mock_client.get.return_value = mock_response

    with patch('venice_sdk.models.HTTPClient', return_value=mock_client):
        models = get_text_models()
        assert len(models) == 1
        assert isinstance(models[0], Model)
        assert models[0].id == "llama-3.3-70b"
        assert models[0].type == "text" 