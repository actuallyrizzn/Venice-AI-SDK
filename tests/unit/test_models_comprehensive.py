"""
Comprehensive unit tests for the models module.
"""

import pytest
from unittest.mock import patch, MagicMock
from venice_sdk.models import (
    ModelCapabilities, Model, ModelsAPI, 
    get_models, get_model_by_id, get_text_models
)
from venice_sdk.errors import VeniceAPIError


class TestModelCapabilitiesComprehensive:
    """Comprehensive test suite for ModelCapabilities class."""

    def test_model_capabilities_initialization(self):
        """Test ModelCapabilities initialization."""
        capabilities = ModelCapabilities(
            supports_function_calling=True,
            supports_web_search=False,
            available_context_tokens=4096
        )
        
        assert capabilities.supports_function_calling is True
        assert capabilities.supports_web_search is False
        assert capabilities.available_context_tokens == 4096

    def test_model_capabilities_with_all_false(self):
        """Test ModelCapabilities with all capabilities disabled."""
        capabilities = ModelCapabilities(
            supports_function_calling=False,
            supports_web_search=False,
            available_context_tokens=0
        )
        
        assert capabilities.supports_function_calling is False
        assert capabilities.supports_web_search is False
        assert capabilities.available_context_tokens == 0

    def test_model_capabilities_with_large_context(self):
        """Test ModelCapabilities with large context window."""
        capabilities = ModelCapabilities(
            supports_function_calling=True,
            supports_web_search=True,
            available_context_tokens=128000
        )
        
        assert capabilities.supports_function_calling is True
        assert capabilities.supports_web_search is True
        assert capabilities.available_context_tokens == 128000

    def test_model_capabilities_equality(self):
        """Test ModelCapabilities equality comparison."""
        caps1 = ModelCapabilities(True, False, 4096)
        caps2 = ModelCapabilities(True, False, 4096)
        caps3 = ModelCapabilities(False, True, 4096)
        
        assert caps1 == caps2
        assert caps1 != caps3

    def test_model_capabilities_string_representation(self):
        """Test ModelCapabilities string representation."""
        capabilities = ModelCapabilities(True, False, 4096)
        caps_str = str(capabilities)
        
        assert "ModelCapabilities" in caps_str
        assert "True" in caps_str
        assert "False" in caps_str
        assert "4096" in caps_str


class TestModelComprehensive:
    """Comprehensive test suite for Model class."""

    def test_model_initialization(self):
        """Test Model initialization."""
        capabilities = ModelCapabilities(True, False, 4096)
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

    def test_model_with_minimal_description(self):
        """Test Model with minimal description."""
        capabilities = ModelCapabilities(False, False, 0)
        model = Model(
            id="minimal-model",
            name="Minimal Model",
            type="text",
            capabilities=capabilities,
            description=""
        )
        
        assert model.description == ""

    def test_model_with_long_description(self):
        """Test Model with long description."""
        capabilities = ModelCapabilities(True, True, 128000)
        long_description = "This is a very long description that contains multiple sentences and provides detailed information about the model's capabilities, performance characteristics, and use cases. It should be able to handle various types of content and provide accurate responses."
        
        model = Model(
            id="long-desc-model",
            name="Long Description Model",
            type="text",
            capabilities=capabilities,
            description=long_description
        )
        
        assert model.description == long_description

    def test_model_with_special_characters(self):
        """Test Model with special characters in fields."""
        capabilities = ModelCapabilities(True, True, 4096)
        model = Model(
            id="model-with-special-chars!@#$%",
            name="Model with Special Chars!@#$%",
            type="text",
            capabilities=capabilities,
            description="Description with special chars: !@#$%^&*()"
        )
        
        assert model.id == "model-with-special-chars!@#$%"
        assert model.name == "Model with Special Chars!@#$%"
        assert model.description == "Description with special chars: !@#$%^&*()"

    def test_model_equality(self):
        """Test Model equality comparison."""
        capabilities = ModelCapabilities(True, False, 4096)
        model1 = Model("test", "Test", "text", capabilities, "desc")
        model2 = Model("test", "Test", "text", capabilities, "desc")
        model3 = Model("different", "Test", "text", capabilities, "desc")
        
        assert model1 == model2
        assert model1 != model3

    def test_model_string_representation(self):
        """Test Model string representation."""
        capabilities = ModelCapabilities(True, False, 4096)
        model = Model("test-model", "Test Model", "text", capabilities, "A test model")
        model_str = str(model)
        
        assert "Model" in model_str
        assert "test-model" in model_str
        assert "Test Model" in model_str


class TestModelsAPIComprehensive:
    """Comprehensive test suite for ModelsAPI class."""

    def test_models_api_initialization(self, mock_client):
        """Test ModelsAPI initialization."""
        models_api = ModelsAPI(mock_client)
        assert models_api.client == mock_client

    def test_list_success(self, mock_client, mock_models_response):
        """Test successful model listing."""
        mock_client.get.return_value = mock_models_response
        models_api = ModelsAPI(mock_client)
        
        models = models_api.list()
        
        assert len(models) == 1
        assert models[0]["id"] == "llama-3.3-70b"
        assert models[0]["name"] == "Llama 3.3 70B"
        mock_client.get.assert_called_once_with("models")

    def test_list_with_empty_response(self, mock_client):
        """Test model listing with empty response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_client.get.return_value = mock_response
        models_api = ModelsAPI(mock_client)
        
        models = models_api.list()
        
        assert models == []

    def test_list_with_multiple_models(self, mock_client):
        """Test model listing with multiple models."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"id": "model1", "name": "Model 1", "type": "text"},
                {"id": "model2", "name": "Model 2", "type": "text"},
                {"id": "model3", "name": "Model 3", "type": "image"}
            ]
        }
        mock_client.get.return_value = mock_response
        models_api = ModelsAPI(mock_client)
        
        models = models_api.list()
        
        assert len(models) == 3
        assert models[0]["id"] == "model1"
        assert models[1]["id"] == "model2"
        assert models[2]["id"] == "model3"

    def test_get_success(self, mock_client, mock_models_response):
        """Test successful model retrieval."""
        mock_client.get.return_value = mock_models_response
        models_api = ModelsAPI(mock_client)
        
        model = models_api.get("llama-3.3-70b")
        
        assert model["id"] == "llama-3.3-70b"
        assert model["name"] == "Llama 3.3 70B"

    def test_get_model_not_found(self, mock_client, mock_models_response):
        """Test model retrieval when model not found."""
        mock_client.get.return_value = mock_models_response
        models_api = ModelsAPI(mock_client)
        
        with pytest.raises(VeniceAPIError, match="Model nonexistent-model not found"):
            models_api.get("nonexistent-model")

    def test_get_with_empty_model_list(self, mock_client):
        """Test model retrieval with empty model list."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_client.get.return_value = mock_response
        models_api = ModelsAPI(mock_client)
        
        with pytest.raises(VeniceAPIError, match="Model test-model not found"):
            models_api.get("test-model")

    def test_validate_success(self, mock_client, mock_models_response):
        """Test successful model validation."""
        mock_client.get.return_value = mock_models_response
        models_api = ModelsAPI(mock_client)
        
        result = models_api.validate("llama-3.3-70b")
        
        assert result is True

    def test_validate_failure(self, mock_client, mock_models_response):
        """Test model validation failure."""
        mock_client.get.return_value = mock_models_response
        models_api = ModelsAPI(mock_client)
        
        result = models_api.validate("nonexistent-model")
        
        assert result is False

    def test_validate_with_api_error(self, mock_client):
        """Test model validation with API error."""
        mock_client.get.side_effect = VeniceAPIError("API error", status_code=500)
        models_api = ModelsAPI(mock_client)
        
        result = models_api.validate("test-model")
        
        assert result is False

    def test_validate_with_connection_error(self, mock_client):
        """Test model validation with connection error."""
        mock_client.get.side_effect = Exception("Connection error")
        models_api = ModelsAPI(mock_client)
        
        result = models_api.validate("test-model")
        
        assert result is False


class TestGetModelsComprehensive:
    """Comprehensive test suite for get_models function."""

    def test_get_models_with_client(self, mock_client, mock_models_response):
        """Test get_models with provided client."""
        mock_client.get.return_value = mock_models_response
        models = get_models(client=mock_client)
        
        assert len(models) == 1
        assert isinstance(models[0], Model)
        assert models[0].id == "llama-3.3-70b"
        assert models[0].name == "llama-3.3-70b"
        assert models[0].type == "text"
        assert models[0].capabilities.supports_function_calling is True
        assert models[0].capabilities.supports_web_search is True
        assert models[0].capabilities.available_context_tokens == 4096

    def test_get_models_without_client(self):
        """Test get_models without provided client."""
        with patch('venice_sdk.models.HTTPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "data": [{
                    "id": "test-model",
                    "type": "text",
                    "model_spec": {
                        "capabilities": {
                            "supportsFunctionCalling": True,
                            "supportsWebSearch": False
                        },
                        "availableContextTokens": 2048
                    },
                    "description": "Test model"
                }]
            }
            mock_client.get.return_value = mock_response
            
            models = get_models()
            
            assert len(models) == 1
            assert models[0].id == "test-model"
            assert models[0].capabilities.supports_function_calling is True
            assert models[0].capabilities.supports_web_search is False

    def test_get_models_with_multiple_models(self, mock_client):
        """Test get_models with multiple models."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "model1",
                    "type": "text",
                    "model_spec": {
                        "capabilities": {
                            "supportsFunctionCalling": True,
                            "supportsWebSearch": True
                        },
                        "availableContextTokens": 4096
                    },
                    "description": "Model 1"
                },
                {
                    "id": "model2",
                    "type": "image",
                    "model_spec": {
                        "capabilities": {
                            "supportsFunctionCalling": False,
                            "supportsWebSearch": False
                        },
                        "availableContextTokens": 1024
                    },
                    "description": "Model 2"
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        models = get_models(client=mock_client)
        
        assert len(models) == 2
        assert models[0].id == "model1"
        assert models[0].type == "text"
        assert models[1].id == "model2"
        assert models[1].type == "image"

    def test_get_models_with_missing_description(self, mock_client):
        """Test get_models with missing description field."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{
                "id": "test-model",
                "type": "text",
                "model_spec": {
                    "capabilities": {
                        "supportsFunctionCalling": True,
                        "supportsWebSearch": False
                    },
                    "availableContextTokens": 2048,
                    "modelSource": "Custom Source"
                }
            }]
        }
        mock_client.get.return_value = mock_response
        
        models = get_models(client=mock_client)
        
        assert len(models) == 1
        assert models[0].description == "Custom Source"

    def test_get_models_with_missing_model_source(self, mock_client):
        """Test get_models with missing modelSource field."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{
                "id": "test-model",
                "type": "text",
                "model_spec": {
                    "capabilities": {
                        "supportsFunctionCalling": True,
                        "supportsWebSearch": False
                    },
                    "availableContextTokens": 2048
                }
            }]
        }
        mock_client.get.return_value = mock_response
        
        models = get_models(client=mock_client)
        
        assert len(models) == 1
        assert models[0].description == "No description available"


class TestGetModelByIdComprehensive:
    """Comprehensive test suite for get_model_by_id function."""

    def test_get_model_by_id_success(self, mock_client, mock_models_response):
        """Test successful model retrieval by ID."""
        mock_client.get.return_value = mock_models_response
        model = get_model_by_id("llama-3.3-70b", client=mock_client)
        
        assert model is not None
        assert isinstance(model, Model)
        assert model.id == "llama-3.3-70b"
        assert model.capabilities.supports_function_calling is True

    def test_get_model_by_id_not_found(self, mock_client, mock_models_response):
        """Test model retrieval by ID when model not found."""
        mock_client.get.return_value = mock_models_response
        model = get_model_by_id("nonexistent-model", client=mock_client)
        
        assert model is None

    def test_get_model_by_id_without_client(self):
        """Test get_model_by_id without provided client."""
        with patch('venice_sdk.models.HTTPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "data": [{
                    "id": "test-model",
                    "type": "text",
                    "model_spec": {
                        "capabilities": {
                            "supportsFunctionCalling": True,
                            "supportsWebSearch": False
                        },
                        "availableContextTokens": 2048
                    },
                    "description": "Test model"
                }]
            }
            mock_client.get.return_value = mock_response
            
            model = get_model_by_id("test-model")
            
            assert model is not None
            assert model.id == "test-model"

    def test_get_model_by_id_with_api_error(self, mock_client):
        """Test get_model_by_id with API error."""
        mock_client.get.side_effect = VeniceAPIError("API error", status_code=500)
        model = get_model_by_id("test-model", client=mock_client)
        
        assert model is None


class TestGetTextModelsComprehensive:
    """Comprehensive test suite for get_text_models function."""

    def test_get_text_models_success(self, mock_client):
        """Test successful text models retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "text-model-1",
                    "type": "text",
                    "model_spec": {
                        "capabilities": {
                            "supportsFunctionCalling": True,
                            "supportsWebSearch": False
                        },
                        "availableContextTokens": 4096
                    },
                    "description": "Text model 1"
                },
                {
                    "id": "image-model-1",
                    "type": "image",
                    "model_spec": {
                        "capabilities": {
                            "supportsFunctionCalling": False,
                            "supportsWebSearch": False
                        },
                        "availableContextTokens": 1024
                    },
                    "description": "Image model 1"
                },
                {
                    "id": "text-model-2",
                    "type": "text",
                    "model_spec": {
                        "capabilities": {
                            "supportsFunctionCalling": False,
                            "supportsWebSearch": True
                        },
                        "availableContextTokens": 2048
                    },
                    "description": "Text model 2"
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        text_models = get_text_models(client=mock_client)
        
        assert len(text_models) == 2
        assert all(model.type == "text" for model in text_models)
        assert text_models[0].id == "text-model-1"
        assert text_models[1].id == "text-model-2"

    def test_get_text_models_no_text_models(self, mock_client):
        """Test get_text_models when no text models available."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "image-model-1",
                    "type": "image",
                    "model_spec": {
                        "capabilities": {
                            "supportsFunctionCalling": False,
                            "supportsWebSearch": False
                        },
                        "availableContextTokens": 1024
                    },
                    "description": "Image model 1"
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        text_models = get_text_models(client=mock_client)
        
        assert len(text_models) == 0

    def test_get_text_models_without_client(self):
        """Test get_text_models without provided client."""
        with patch('venice_sdk.models.get_models') as mock_get_models:
            mock_models = [
                Model("text1", "text1", "text", ModelCapabilities(True, False, 4096), "desc1"),
                Model("image1", "image1", "image", ModelCapabilities(False, False, 1024), "desc2"),
                Model("text2", "text2", "text", ModelCapabilities(False, True, 2048), "desc3")
            ]
            mock_get_models.return_value = mock_models
            
            text_models = get_text_models()
            
            assert len(text_models) == 2
            assert all(model.type == "text" for model in text_models)

    def test_get_text_models_with_mixed_types(self, mock_client):
        """Test get_text_models with various model types."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"id": "text1", "type": "text", "model_spec": {"capabilities": {"supportsFunctionCalling": True, "supportsWebSearch": False}, "availableContextTokens": 4096}, "description": "Text 1"},
                {"id": "image1", "type": "image", "model_spec": {"capabilities": {"supportsFunctionCalling": False, "supportsWebSearch": False}, "availableContextTokens": 1024}, "description": "Image 1"},
                {"id": "audio1", "type": "audio", "model_spec": {"capabilities": {"supportsFunctionCalling": False, "supportsWebSearch": False}, "availableContextTokens": 512}, "description": "Audio 1"},
                {"id": "text2", "type": "text", "model_spec": {"capabilities": {"supportsFunctionCalling": False, "supportsWebSearch": True}, "availableContextTokens": 2048}, "description": "Text 2"},
                {"id": "video1", "type": "video", "model_spec": {"capabilities": {"supportsFunctionCalling": False, "supportsWebSearch": False}, "availableContextTokens": 256}, "description": "Video 1"}
            ]
        }
        mock_client.get.return_value = mock_response
        
        text_models = get_text_models(client=mock_client)
        
        assert len(text_models) == 2
        assert text_models[0].id == "text1"
        assert text_models[1].id == "text2"
