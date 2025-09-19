"""
Comprehensive unit tests for the models_advanced module.
"""

import pytest
from unittest.mock import patch, MagicMock
from venice_sdk.models_advanced import (
    ModelTraits, CompatibilityMapping, ModelsTraitsAPI, ModelsCompatibilityAPI,
    ModelRecommendationEngine, get_model_traits, get_compatibility_mapping,
    find_models_by_capability
)
from venice_sdk.errors import VeniceAPIError, ModelNotFoundError


class TestModelTraitsComprehensive:
    """Comprehensive test suite for ModelTraits class."""

    def test_model_traits_initialization(self):
        """Test ModelTraits initialization with all parameters."""
        traits = ModelTraits(
            model_id="llama-3.3-70b",
            capabilities={"function_calling": True, "streaming": True},
            traits={"speed": "high", "quality": "excellent"},
            performance_metrics={"accuracy": 0.95, "latency": 100},
            supported_formats=["json", "text"],
            context_length=4096,
            max_tokens=2048,
            temperature_range=(0.0, 2.0),
            languages=["en", "es", "fr"]
        )
        
        assert traits.model_id == "llama-3.3-70b"
        assert traits.capabilities == {"function_calling": True, "streaming": True}
        assert traits.traits == {"speed": "high", "quality": "excellent"}
        assert traits.performance_metrics == {"accuracy": 0.95, "latency": 100}
        assert traits.supported_formats == ["json", "text"]
        assert traits.context_length == 4096
        assert traits.max_tokens == 2048
        assert traits.temperature_range == (0.0, 2.0)
        assert traits.languages == ["en", "es", "fr"]

    def test_model_traits_initialization_with_defaults(self):
        """Test ModelTraits initialization with default values."""
        traits = ModelTraits(
            model_id="test-model",
            capabilities={},
            traits={}
        )
        
        assert traits.model_id == "test-model"
        assert traits.capabilities == {}
        assert traits.traits == {}
        assert traits.performance_metrics is None
        assert traits.supported_formats is None
        assert traits.context_length is None
        assert traits.max_tokens is None
        assert traits.temperature_range is None
        assert traits.languages is None

    def test_has_capability(self):
        """Test has_capability method."""
        traits = ModelTraits("test", {"function_calling": True}, {})
        
        assert traits.has_capability("function_calling") is True
        assert traits.has_capability("streaming") is False

    def test_get_capability_value(self):
        """Test get_capability_value method."""
        traits = ModelTraits("test", {"function_calling": True}, {})
        
        assert traits.get_capability_value("function_calling") is True
        assert traits.get_capability_value("streaming") is None
        assert traits.get_capability_value("streaming", False) is False

    def test_has_trait(self):
        """Test has_trait method."""
        traits = ModelTraits("test", {}, {"speed": "high"})
        
        assert traits.has_trait("speed") is True
        assert traits.has_trait("quality") is False

    def test_get_trait_value(self):
        """Test get_trait_value method."""
        traits = ModelTraits("test", {}, {"speed": "high"})
        
        assert traits.get_trait_value("speed") == "high"
        assert traits.get_trait_value("quality") is None
        assert traits.get_trait_value("quality", "medium") == "medium"

    def test_supports_function_calling(self):
        """Test supports_function_calling method."""
        traits1 = ModelTraits("test", {"function_calling": True}, {})
        traits2 = ModelTraits("test", {}, {"function_calling": True})
        traits3 = ModelTraits("test", {}, {})
        
        assert traits1.supports_function_calling() is True
        assert traits2.supports_function_calling() is True
        assert traits3.supports_function_calling() is False

    def test_supports_streaming(self):
        """Test supports_streaming method."""
        traits1 = ModelTraits("test", {"streaming": True}, {})
        traits2 = ModelTraits("test", {}, {"streaming": True})
        traits3 = ModelTraits("test", {}, {})
        
        assert traits1.supports_streaming() is True
        assert traits2.supports_streaming() is True
        assert traits3.supports_streaming() is False

    def test_supports_web_search(self):
        """Test supports_web_search method."""
        traits1 = ModelTraits("test", {"web_search": True}, {})
        traits2 = ModelTraits("test", {}, {"web_search": True})
        traits3 = ModelTraits("test", {}, {})
        
        assert traits1.supports_web_search() is True
        assert traits2.supports_web_search() is True
        assert traits3.supports_web_search() is False

    def test_supports_vision(self):
        """Test supports_vision method."""
        traits1 = ModelTraits("test", {"vision": True}, {})
        traits2 = ModelTraits("test", {}, {"vision": True})
        traits3 = ModelTraits("test", {}, {})
        
        assert traits1.supports_vision() is True
        assert traits2.supports_vision() is True
        assert traits3.supports_vision() is False

    def test_supports_audio(self):
        """Test supports_audio method."""
        traits1 = ModelTraits("test", {"audio": True}, {})
        traits2 = ModelTraits("test", {}, {"audio": True})
        traits3 = ModelTraits("test", {}, {})
        
        assert traits1.supports_audio() is True
        assert traits2.supports_audio() is True
        assert traits3.supports_audio() is False


class TestCompatibilityMappingComprehensive:
    """Comprehensive test suite for CompatibilityMapping class."""

    def test_compatibility_mapping_initialization(self):
        """Test CompatibilityMapping initialization."""
        mapping = CompatibilityMapping(
            openai_to_venice={"gpt-4": "llama-3.3-70b", "gpt-3.5-turbo": "llama-3.3-8b"},
            venice_to_openai={"llama-3.3-70b": "gpt-4", "llama-3.3-8b": "gpt-3.5-turbo"},
            provider_mappings={"anthropic": {"claude-3": "llama-3.3-70b"}}
        )
        
        assert mapping.openai_to_venice == {"gpt-4": "llama-3.3-70b", "gpt-3.5-turbo": "llama-3.3-8b"}
        assert mapping.venice_to_openai == {"llama-3.3-70b": "gpt-4", "llama-3.3-8b": "gpt-3.5-turbo"}
        assert mapping.provider_mappings == {"anthropic": {"claude-3": "llama-3.3-70b"}}

    def test_get_venice_model(self):
        """Test get_venice_model method."""
        mapping = CompatibilityMapping(
            openai_to_venice={"gpt-4": "llama-3.3-70b"},
            venice_to_openai={},
            provider_mappings={}
        )
        
        assert mapping.get_venice_model("gpt-4") == "llama-3.3-70b"
        assert mapping.get_venice_model("gpt-3.5-turbo") is None

    def test_get_openai_model(self):
        """Test get_openai_model method."""
        mapping = CompatibilityMapping(
            openai_to_venice={},
            venice_to_openai={"llama-3.3-70b": "gpt-4"},
            provider_mappings={}
        )
        
        assert mapping.get_openai_model("llama-3.3-70b") == "gpt-4"
        assert mapping.get_openai_model("llama-3.3-8b") is None

    def test_get_provider_model(self):
        """Test get_provider_model method."""
        mapping = CompatibilityMapping(
            openai_to_venice={},
            venice_to_openai={},
            provider_mappings={"anthropic": {"claude-3": "llama-3.3-70b"}}
        )
        
        assert mapping.get_provider_model("anthropic", "claude-3") == "llama-3.3-70b"
        assert mapping.get_provider_model("anthropic", "claude-2") is None
        assert mapping.get_provider_model("openai", "gpt-4") is None

    def test_list_available_mappings(self):
        """Test list_available_mappings method."""
        mapping = CompatibilityMapping(
            openai_to_venice={},
            venice_to_openai={},
            provider_mappings={"anthropic": {}, "cohere": {}}
        )
        
        mappings = mapping.list_available_mappings()
        assert set(mappings) == {"anthropic", "cohere"}


class TestModelsTraitsAPIComprehensive:
    """Comprehensive test suite for ModelsTraitsAPI class."""

    def test_models_traits_api_initialization(self, mock_client):
        """Test ModelsTraitsAPI initialization."""
        api = ModelsTraitsAPI(mock_client)
        assert api.client == mock_client
        assert api._traits_cache == {}

    def test_get_traits_success(self, mock_client):
        """Test successful traits retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "llama-3.3-70b": {
                    "capabilities": {"function_calling": True, "streaming": True},
                    "traits": {"speed": "high", "quality": "excellent"},
                    "context_length": 4096,
                    "max_tokens": 2048
                },
                "llama-3.3-8b": {
                    "capabilities": {"function_calling": False, "streaming": True},
                    "traits": {"speed": "very_high", "quality": "good"},
                    "context_length": 2048,
                    "max_tokens": 1024
                }
            }
        }
        mock_client.get.return_value = mock_response
        
        api = ModelsTraitsAPI(mock_client)
        traits = api.get_traits()
        
        assert len(traits) == 2
        assert "llama-3.3-70b" in traits
        assert "llama-3.3-8b" in traits
        assert isinstance(traits["llama-3.3-70b"], ModelTraits)
        assert traits["llama-3.3-70b"].supports_function_calling() is True

    def test_get_traits_with_cache(self, mock_client):
        """Test traits retrieval with caching."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"model1": {"name": "Test Model"}}}
        mock_client.get.return_value = mock_response

        api = ModelsTraitsAPI(mock_client)

        # First call
        traits1 = api.get_traits()
        assert mock_client.get.call_count == 1

        # Second call should use cache
        traits2 = api.get_traits()
        assert mock_client.get.call_count == 1
        assert traits1 == traits2

    def test_get_traits_without_cache(self, mock_client):
        """Test traits retrieval without caching."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {}}
        mock_client.get.return_value = mock_response
        
        api = ModelsTraitsAPI(mock_client)
        
        # First call
        traits1 = api.get_traits(use_cache=False)
        assert mock_client.get.call_count == 1
        
        # Second call should not use cache
        traits2 = api.get_traits(use_cache=False)
        assert mock_client.get.call_count == 2

    def test_get_traits_invalid_response(self, mock_client):
        """Test traits retrieval with invalid response format."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"invalid": "data"}
        mock_client.get.return_value = mock_response
        
        api = ModelsTraitsAPI(mock_client)
        
        with pytest.raises(ModelNotFoundError, match="Invalid response format from models traits endpoint"):
            api.get_traits()

    def test_get_model_traits(self, mock_client):
        """Test getting traits for a specific model."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "llama-3.3-70b": {
                    "capabilities": {"function_calling": True},
                    "traits": {"speed": "high"}
                }
            }
        }
        mock_client.get.return_value = mock_response
        
        api = ModelsTraitsAPI(mock_client)
        traits = api.get_model_traits("llama-3.3-70b")
        
        assert traits is not None
        assert isinstance(traits, ModelTraits)
        assert traits.model_id == "llama-3.3-70b"
        assert traits.supports_function_calling() is True

    def test_get_model_traits_not_found(self, mock_client):
        """Test getting traits for a model that doesn't exist."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {}}
        mock_client.get.return_value = mock_response
        
        api = ModelsTraitsAPI(mock_client)
        traits = api.get_model_traits("nonexistent-model")
        
        assert traits is None

    def test_get_capabilities(self, mock_client):
        """Test getting capabilities for a specific model."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "llama-3.3-70b": {
                    "capabilities": {"function_calling": True, "streaming": True},
                    "traits": {}
                }
            }
        }
        mock_client.get.return_value = mock_response
        
        api = ModelsTraitsAPI(mock_client)
        capabilities = api.get_capabilities("llama-3.3-70b")
        
        assert capabilities == {"function_calling": True, "streaming": True}

    def test_get_traits_dict(self, mock_client):
        """Test getting traits dictionary for a specific model."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "llama-3.3-70b": {
                    "capabilities": {},
                    "traits": {"speed": "high", "quality": "excellent"}
                }
            }
        }
        mock_client.get.return_value = mock_response
        
        api = ModelsTraitsAPI(mock_client)
        traits_dict = api.get_traits_dict("llama-3.3-70b")
        
        assert traits_dict == {"speed": "high", "quality": "excellent"}

    def test_find_models_by_capability(self, mock_client):
        """Test finding models by capability."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "llama-3.3-70b": {
                    "capabilities": {"function_calling": True, "streaming": True},
                    "traits": {}
                },
                "llama-3.3-8b": {
                    "capabilities": {"streaming": True},
                    "traits": {}
                }
            }
        }
        mock_client.get.return_value = mock_response
        
        api = ModelsTraitsAPI(mock_client)
        models = api.find_models_by_capability("function_calling")
        
        assert models == ["llama-3.3-70b"]

    def test_find_models_by_trait(self, mock_client):
        """Test finding models by trait."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "llama-3.3-70b": {
                    "capabilities": {},
                    "traits": {"speed": "high", "quality": "excellent"}
                },
                "llama-3.3-8b": {
                    "capabilities": {},
                    "traits": {"speed": "very_high"}
                }
            }
        }
        mock_client.get.return_value = mock_response
        
        api = ModelsTraitsAPI(mock_client)
        models = api.find_models_by_trait("speed")
        
        assert set(models) == {"llama-3.3-70b", "llama-3.3-8b"}

    def test_get_models_by_type(self, mock_client):
        """Test getting models by type."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "llama-3.3-70b": {
                    "capabilities": {"type": "text"},
                    "traits": {}
                },
                "dall-e-3": {
                    "capabilities": {"type": "image"},
                    "traits": {}
                }
            }
        }
        mock_client.get.return_value = mock_response
        
        api = ModelsTraitsAPI(mock_client)
        models = api.get_models_by_type("text")
        
        assert models == ["llama-3.3-70b"]

    def test_get_best_models_for_task(self, mock_client):
        """Test getting best models for a task."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "llama-3.3-70b": {
                    "capabilities": {"function_calling": True, "streaming": True, "web_search": True},
                    "traits": {}
                },
                "llama-3.3-8b": {
                    "capabilities": {"streaming": True},
                    "traits": {}
                }
            }
        }
        mock_client.get.return_value = mock_response
        
        api = ModelsTraitsAPI(mock_client)
        models = api.get_best_models_for_task("chat")
        
        assert "llama-3.3-70b" in models
        assert "llama-3.3-8b" in models
        # Should be sorted by score (descending)
        assert models[0] == "llama-3.3-70b"

    def test_clear_cache(self, mock_client):
        """Test clearing the traits cache."""
        api = ModelsTraitsAPI(mock_client)
        api._traits_cache = {"test": "cached"}
        
        api.clear_cache()
        assert api._traits_cache == {}


class TestModelsCompatibilityAPIComprehensive:
    """Comprehensive test suite for ModelsCompatibilityAPI class."""

    def test_models_compatibility_api_initialization(self, mock_client):
        """Test ModelsCompatibilityAPI initialization."""
        api = ModelsCompatibilityAPI(mock_client)
        assert api.client == mock_client
        assert api._mapping_cache is None

    def test_get_mapping_success(self, mock_client):
        """Test successful mapping retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "openai_to_venice": {"gpt-4": "llama-3.3-70b"},
                "venice_to_openai": {"llama-3.3-70b": "gpt-4"},
                "provider_mappings": {"anthropic": {"claude-3": "llama-3.3-70b"}}
            }
        }
        mock_client.get.return_value = mock_response
        
        api = ModelsCompatibilityAPI(mock_client)
        mapping = api.get_mapping()
        
        assert isinstance(mapping, CompatibilityMapping)
        assert mapping.get_venice_model("gpt-4") == "llama-3.3-70b"
        assert mapping.get_openai_model("llama-3.3-70b") == "gpt-4"

    def test_get_mapping_with_cache(self, mock_client):
        """Test mapping retrieval with caching."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {}}
        mock_client.get.return_value = mock_response
        
        api = ModelsCompatibilityAPI(mock_client)
        
        # First call
        mapping1 = api.get_mapping()
        assert mock_client.get.call_count == 1
        
        # Second call should use cache
        mapping2 = api.get_mapping()
        assert mock_client.get.call_count == 1
        assert mapping1 == mapping2

    def test_get_mapping_invalid_response(self, mock_client):
        """Test mapping retrieval with invalid response format."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"invalid": "data"}
        mock_client.get.return_value = mock_response
        
        api = ModelsCompatibilityAPI(mock_client)
        
        with pytest.raises(ModelNotFoundError, match="Invalid response format from compatibility mapping endpoint"):
            api.get_mapping()

    def test_get_venice_model(self, mock_client):
        """Test getting Venice model for OpenAI model."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "openai_to_venice": {"gpt-4": "llama-3.3-70b"},
                "venice_to_openai": {},
                "provider_mappings": {}
            }
        }
        mock_client.get.return_value = mock_response
        
        api = ModelsCompatibilityAPI(mock_client)
        venice_model = api.get_venice_model("gpt-4")
        
        assert venice_model == "llama-3.3-70b"

    def test_get_openai_model(self, mock_client):
        """Test getting OpenAI model for Venice model."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "openai_to_venice": {},
                "venice_to_openai": {"llama-3.3-70b": "gpt-4"},
                "provider_mappings": {}
            }
        }
        mock_client.get.return_value = mock_response
        
        api = ModelsCompatibilityAPI(mock_client)
        openai_model = api.get_openai_model("llama-3.3-70b")
        
        assert openai_model == "gpt-4"

    def test_migrate_openai_models(self, mock_client):
        """Test migrating OpenAI models to Venice equivalents."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "openai_to_venice": {"gpt-4": "llama-3.3-70b", "gpt-3.5-turbo": "llama-3.3-8b"},
                "venice_to_openai": {},
                "provider_mappings": {}
            }
        }
        mock_client.get.return_value = mock_response
        
        api = ModelsCompatibilityAPI(mock_client)
        migrated = api.migrate_openai_models(["gpt-4", "gpt-3.5-turbo", "gpt-3"])
        
        assert migrated == {"gpt-4": "llama-3.3-70b", "gpt-3.5-turbo": "llama-3.3-8b"}

    def test_get_available_providers(self, mock_client):
        """Test getting available providers."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "openai_to_venice": {},
                "venice_to_openai": {},
                "provider_mappings": {"anthropic": {}, "cohere": {}}
            }
        }
        mock_client.get.return_value = mock_response
        
        api = ModelsCompatibilityAPI(mock_client)
        providers = api.get_available_providers()
        
        assert set(providers) == {"anthropic", "cohere"}

    def test_clear_cache(self, mock_client):
        """Test clearing the mapping cache."""
        api = ModelsCompatibilityAPI(mock_client)
        api._mapping_cache = "cached"
        
        api.clear_cache()
        assert api._mapping_cache is None


class TestModelRecommendationEngineComprehensive:
    """Comprehensive test suite for ModelRecommendationEngine class."""

    def test_model_recommendation_engine_initialization(self, mock_client):
        """Test ModelRecommendationEngine initialization."""
        traits_api = ModelsTraitsAPI(mock_client)
        compatibility_api = ModelsCompatibilityAPI(mock_client)
        engine = ModelRecommendationEngine(traits_api, compatibility_api)
        
        assert engine.traits_api == traits_api
        assert engine.compatibility_api == compatibility_api

    def test_recommend_models_basic(self, mock_client):
        """Test basic model recommendation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "llama-3.3-70b": {
                    "capabilities": {"function_calling": True, "streaming": True, "web_search": True},
                    "traits": {"speed": "high", "quality": "excellent", "cost_level": "high"}
                }
            }
        }
        mock_client.get.return_value = mock_response
        
        traits_api = ModelsTraitsAPI(mock_client)
        compatibility_api = ModelsCompatibilityAPI(mock_client)
        engine = ModelRecommendationEngine(traits_api, compatibility_api)
        
        recommendations = engine.recommend_models("chat")
        
        assert len(recommendations) == 1
        assert recommendations[0]["model_id"] == "llama-3.3-70b"
        assert "score" in recommendations[0]
        assert "capabilities" in recommendations[0]

    def test_recommend_models_with_requirements(self, mock_client):
        """Test model recommendation with specific requirements."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "llama-3.3-70b": {
                    "capabilities": {"function_calling": True, "streaming": True},
                    "traits": {"speed": "high", "quality": "excellent"}
                }
            }
        }
        mock_client.get.return_value = mock_response
        
        traits_api = ModelsTraitsAPI(mock_client)
        compatibility_api = ModelsCompatibilityAPI(mock_client)
        engine = ModelRecommendationEngine(traits_api, compatibility_api)
        
        recommendations = engine.recommend_models(
            "chat",
            requirements={"function_calling": True},
            budget_constraint="high",
            performance_priority="quality"
        )
        
        assert len(recommendations) == 1
        assert recommendations[0]["model_id"] == "llama-3.3-70b"

    def test_calculate_recommendation_score(self, mock_client):
        """Test recommendation score calculation."""
        # Mock the get_traits method to return expected data
        mock_traits = {
            "test-model": ModelTraits(
                model_id="test-model",
                capabilities={"function_calling": True},
                traits={"speed": "high", "quality": "excellent", "cost_level": "low"}
            )
        }
        
        traits_api = ModelsTraitsAPI(mock_client)
        compatibility_api = ModelsCompatibilityAPI(mock_client)
        engine = ModelRecommendationEngine(traits_api, compatibility_api)
        
        # Mock the get_traits method
        with patch.object(traits_api, 'get_traits', return_value=mock_traits):
            traits = ModelTraits(
                model_id="test-model",
                capabilities={"function_calling": True},
                traits={"speed": "high", "quality": "excellent", "cost_level": "low"}
            )
            
            score = engine._calculate_recommendation_score(
                traits,
                "chat",
                {"function_calling": True},
                "low",
                "speed"
            )
            
            assert isinstance(score, float)
            assert score > 0


class TestConvenienceFunctionsComprehensive:
    """Comprehensive test suite for convenience functions."""

    def test_get_model_traits_with_client(self, mock_client):
        """Test get_model_traits with provided client."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "llama-3.3-70b": {
                    "capabilities": {"function_calling": True},
                    "traits": {"speed": "high"}
                }
            }
        }
        mock_client.get.return_value = mock_response
        
        traits = get_model_traits("llama-3.3-70b", client=mock_client)
        
        assert traits is not None
        assert isinstance(traits, ModelTraits)
        assert traits.model_id == "llama-3.3-70b"

    def test_get_model_traits_without_client(self):
        """Test get_model_traits without provided client."""
        with patch('venice_sdk.config.load_config') as mock_load_config:
            with patch('venice_sdk.venice_client.VeniceClient') as mock_venice_client:
                mock_config = MagicMock()
                mock_load_config.return_value = mock_config
                
                mock_client = MagicMock()
                mock_venice_client.return_value = mock_client
                
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "data": {
                        "llama-3.3-70b": {
                            "capabilities": {"function_calling": True},
                            "traits": {"speed": "high"}
                        }
                    }
                }
                mock_client.get.return_value = mock_response
                
                traits = get_model_traits("llama-3.3-70b")
                
                assert traits is not None
                assert isinstance(traits, ModelTraits)

    def test_get_compatibility_mapping_with_client(self, mock_client):
        """Test get_compatibility_mapping with provided client."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "openai_to_venice": {"gpt-4": "llama-3.3-70b"},
                "venice_to_openai": {"llama-3.3-70b": "gpt-4"},
                "provider_mappings": {}
            }
        }
        mock_client.get.return_value = mock_response
        
        mapping = get_compatibility_mapping(client=mock_client)
        
        assert isinstance(mapping, CompatibilityMapping)
        assert mapping.get_venice_model("gpt-4") == "llama-3.3-70b"

    def test_find_models_by_capability_with_client(self, mock_client):
        """Test find_models_by_capability with provided client."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "llama-3.3-70b": {
                    "capabilities": {"function_calling": True},
                    "traits": {}
                }
            }
        }
        mock_client.get.return_value = mock_response
        
        models = find_models_by_capability("function_calling", client=mock_client)
        
        assert models == ["llama-3.3-70b"]

    def test_find_models_by_capability_without_client(self):
        """Test find_models_by_capability without provided client."""
        with patch('venice_sdk.config.load_config') as mock_load_config:
            with patch('venice_sdk.venice_client.VeniceClient') as mock_venice_client:
                mock_config = MagicMock()
                mock_load_config.return_value = mock_config
                
                mock_client = MagicMock()
                mock_venice_client.return_value = mock_client
                
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "data": {
                        "llama-3.3-70b": {
                            "capabilities": {"function_calling": True},
                            "traits": {}
                        }
                    }
                }
                mock_client.get.return_value = mock_response
                
                models = find_models_by_capability("function_calling")
                
                assert models == ["llama-3.3-70b"]
