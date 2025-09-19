"""
Cross-module integration tests for Venice AI SDK.

These tests verify integration between different modules
and ensure proper data flow and error handling across the system.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from venice_sdk.venice_client import VeniceClient
from venice_sdk.config import Config
from venice_sdk.errors import VeniceAPIError


@pytest.mark.integration
class TestCrossModuleIntegration:
    """Cross-module integration tests."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.api_key = os.getenv("VENICE_API_KEY", "test-api-key")
        self.config = Config(api_key=self.api_key)
        self.client = VeniceClient(self.config)

    def test_chat_models_characters_integration(self):
        """Test integration between chat, models, and characters modules."""
        with patch.object(self.client.http_client, 'get') as mock_get:
            with patch.object(self.client.http_client, 'post') as mock_post:
                # Mock responses
                def mock_get_side_effect(url, **kwargs):
                    if "models" in url:
                        response = MagicMock()
                        response.status_code = 200
                        response.json.return_value = {
                            "data": [{
                                "id": "llama-3.3-8b",
                                "name": "Llama 3.3 8B",
                                "type": "text",
                                "capabilities": {
                                    "supportsFunctionCalling": True,
                                    "supportsWebSearch": False
                                },
                                "model_spec": {
                                    "capabilities": {
                                        "supportsFunctionCalling": True,
                                        "supportsWebSearch": False
                                    },
                                    "availableContextTokens": 4096
                                }
                            }]
                        }
                        return response
                    elif "characters" in url:
                        response = MagicMock()
                        response.status_code = 200
                        response.json.return_value = {
                            "data": [{
                                "id": "assistant-1",
                                "name": "Helpful Assistant",
                                "description": "A friendly AI assistant",
                                "category": "assistant",
                                "tags": ["helpful", "friendly"],
                                "capabilities": {
                                    "text_generation": True,
                                    "voice_synthesis": True
                                },
                                "personality": {
                                    "tone": "professional",
                                    "style": "conversational"
                                },
                                "background": "I am an AI assistant designed to help users."
                            }]
                        }
                        return response
                    return MagicMock()
                
                def mock_post_side_effect(url, **kwargs):
                    if "chat/completions" in url:
                        response = MagicMock()
                        response.status_code = 200
                        response.json.return_value = {
                            "choices": [{
                                "message": {
                                    "content": "Hello! I'm your helpful AI assistant. How can I assist you today?",
                                    "role": "assistant"
                                }
                            }],
                            "model": "llama-3.3-8b",
                            "usage": {"total_tokens": 25}
                        }
                        return response
                    return MagicMock()
                
                mock_get.side_effect = mock_get_side_effect
                mock_post.side_effect = mock_post_side_effect
                
                # Test integration workflow
                # 1. Get available models
                models = self.client.models.list()
                assert len(models) > 0
                selected_model = models[0]
                
                # 2. Get available characters
                characters = self.client.characters.list()
                assert len(characters) > 0
                selected_character = characters[0]
                
                # 3. Use character with model for chat
                character_params = selected_character.to_venice_parameters()
                messages = [
                    {"role": "user", "content": "Hello! Can you help me?"}
                ]
                
                response = self.client.chat.complete(
                    messages=messages,
                    model=selected_model["id"],
                    temperature=0.7,
                    max_tokens=100,
                    **character_params
                )
                
                assert response is not None
                assert "choices" in response
                assert response["model"] == selected_model["id"]

    def test_audio_characters_embeddings_integration(self):
        """Test integration between audio, characters, and embeddings modules."""
        with patch.object(self.client.http_client, 'get') as mock_get:
            with patch.object(self.client.http_client, 'post') as mock_post:
                # Mock responses
                def mock_get_side_effect(url, **kwargs):
                    if "voices" in url:
                        response = MagicMock()
                        response.status_code = 200
                        response.json.return_value = {
                            "data": [{
                                "id": "alloy",
                                "name": "Alloy",
                                "category": "premium",
                                "description": "A clear and professional voice"
                            }]
                        }
                        return response
                    elif "characters" in url:
                        response = MagicMock()
                        response.status_code = 200
                        response.json.return_value = {
                            "data": [{
                                "id": "assistant-1",
                                "name": "Helpful Assistant",
                                "description": "A friendly AI assistant",
                                "category": "assistant",
                                "tags": ["helpful", "friendly"],
                                "capabilities": {
                                    "text_generation": True,
                                    "voice_synthesis": True
                                },
                                "personality": {
                                    "tone": "professional",
                                    "style": "conversational"
                                },
                                "background": "I am an AI assistant designed to help users."
                            }]
                        }
                        return response
                    return MagicMock()
                
                def mock_post_side_effect(url, **kwargs):
                    if "audio/speech" in url:
                        response = MagicMock()
                        response.status_code = 200
                        response.json.return_value = {
                            "data": [{
                                "url": "https://example.com/generated-audio.mp3",
                                "created": 1234567890
                            }]
                        }
                        return response
                    elif "embeddings" in url:
                        response = MagicMock()
                        response.status_code = 200
                        response.json.return_value = {
                            "data": [{
                                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                                "index": 0
                            }],
                            "model": "text-embedding-3-small",
                            "usage": {"total_tokens": 5}
                        }
                        return response
                    return MagicMock()
                
                mock_get.side_effect = mock_get_side_effect
                mock_post.side_effect = mock_post_side_effect
                
                # Test integration workflow
                # 1. Get available voices
                voices = self.client.audio.get_voices()
                assert len(voices) > 0
                selected_voice = voices[0]
                
                # 2. Get characters with voice capabilities
                characters = self.client.characters.list()
                voice_characters = [
                    char for char in characters 
                    if char.has_capability("voice_synthesis")
                ]
                assert len(voice_characters) > 0
                selected_character = voice_characters[0]
                
                # 3. Generate text from character
                character_text = f"Hello! I'm {selected_character.name}. {selected_character.description}"
                
                # 4. Generate audio from character text
                audio_result = self.client.audio.speech(
                    input_text=character_text,
                    voice=selected_voice.id,
                    model="tts-1"
                )
                assert audio_result is not None
                assert hasattr(audio_result, 'audio_data')
                assert hasattr(audio_result, 'format')
                
                # 5. Generate embeddings for character text
                embedding_result = self.client.embeddings.generate_single(
                    text=character_text,
                    model="text-embedding-3-small"
                )
                assert embedding_result is not None
                assert isinstance(embedding_result, list)
                assert len(embedding_result) > 0

    def test_images_models_styles_integration(self):
        """Test integration between images, models, and styles modules."""
        with patch.object(self.client.http_client, 'get') as mock_get:
            with patch.object(self.client.http_client, 'post') as mock_post:
                # Mock responses
                def mock_get_side_effect(url, **kwargs):
                    if "models" in url:
                        response = MagicMock()
                        response.status_code = 200
                        response.json.return_value = {
                            "data": [{
                                "id": "dall-e-3",
                                "name": "DALL-E 3",
                                "type": "image",
                                "capabilities": {
                                    "image_generation": True,
                                    "image_editing": True
                                },
                                "model_spec": {
                                    "capabilities": {
                                        "image_generation": True,
                                        "image_editing": True
                                    },
                                    "availableContextTokens": 4096
                                }
                            }]
                        }
                        return response
                    elif "styles" in url:
                        response = MagicMock()
                        response.status_code = 200
                        response.json.return_value = {
                            "data": [{
                                "id": "vivid",
                                "name": "Vivid",
                                "description": "High contrast and vibrant colors",
                                "category": "artistic",
                                "preview_url": "https://example.com/vivid-preview.jpg"
                            }]
                        }
                        return response
                    return MagicMock()
                
                def mock_post_side_effect(url, **kwargs):
                    if "image/generate" in url:
                        response = MagicMock()
                        response.status_code = 200
                        response.json.return_value = {
                            "data": [{
                                "url": "https://example.com/generated-image.png",
                                "revised_prompt": "A beautiful sunset over mountains with vibrant colors"
                            }],
                            "created": 1234567890
                        }
                        return response
                    return MagicMock()
                
                mock_get.side_effect = mock_get_side_effect
                mock_post.side_effect = mock_post_side_effect
                
                # Test integration workflow
                # 1. Get available image models
                models = self.client.models.list()
                image_models = [
                    model for model in models 
                    if model.get("type") == "image"
                ]
                assert len(image_models) > 0
                selected_model = image_models[0]
                
                # 2. Get available styles
                styles = self.client.image_styles.list_styles()
                assert len(styles) > 0
                selected_style = styles[0]
                
                # 3. Generate image with model and style
                image_result = self.client.images.generate(
                    prompt="A beautiful landscape",
                    model=selected_model["id"],
                    style=selected_style.id,
                    size="1024x1024",
                    quality="hd"
                )
                
                assert image_result is not None
                assert hasattr(image_result, 'url')
                assert image_result.url is not None

    def test_account_billing_models_integration(self):
        """Test integration between account, billing, and models modules."""
        with patch.object(self.client.http_client, 'get') as mock_get:
            # Mock responses
            def mock_get_side_effect(url, **kwargs):
                if "api_keys" in url:
                    response = MagicMock()
                    response.status_code = 200
                    response.json.return_value = {
                        "data": [{
                            "id": "key-123",
                            "name": "Test Key",
                            "created": 1234567890,
                            "last_used": 1234567890,
                            "permissions": ["read", "write"],
                            "is_active": True
                        }]
                    }
                    return response
                elif "billing" in url:
                    response = MagicMock()
                    response.status_code = 200
                    response.json.return_value = {
                        "data": {
                            "total_usage": 1000,
                            "current_period": "2024-01",
                            "credits_remaining": 5000,
                            "usage_by_model": {
                                "llama-3.3-8b": {
                                    "requests": 500,
                                    "tokens": 25000
                                }
                            },
                            "billing_period_start": "2024-01-01T00:00:00Z",
                            "billing_period_end": "2024-01-31T23:59:59Z"
                        }
                    }
                    return response
                elif "models" in url:
                    response = MagicMock()
                    response.status_code = 200
                    response.json.return_value = {
                        "data": [{
                            "id": "llama-3.3-8b",
                            "name": "Llama 3.3 8B",
                            "type": "text",
                            "capabilities": {
                                "supportsFunctionCalling": True,
                                "supportsWebSearch": False
                            },
                            "model_spec": {
                                "capabilities": {
                                    "supportsFunctionCalling": True,
                                    "supportsWebSearch": False
                                },
                                "availableContextTokens": 4096
                            }
                        }]
                    }
                    return response
                return MagicMock()
            
            mock_get.side_effect = mock_get_side_effect
            
            # Test integration workflow
            # 1. Get account information
            api_keys = self.client.api_keys.list()
            assert len(api_keys) > 0
            
            # 2. Get billing information
            usage_info = self.client.billing.get_usage()
            assert usage_info is not None
            assert usage_info.total_usage == 1000
            
            # 3. Get models used in billing
            models = self.client.models.list()
            assert len(models) > 0
            
            # 4. Cross-reference model usage with available models
            used_models = list(usage_info.usage_by_model.keys())
            available_models = [model["id"] for model in models]
            
            for used_model in used_models:
                assert used_model in available_models
            
            # 5. Verify integration worked
            assert len(used_models) > 0
            assert len(available_models) > 0

    def test_embeddings_models_advanced_integration(self):
        """Test integration between embeddings, models, and models_advanced modules."""
        with patch.object(self.client.http_client, 'get') as mock_get:
            with patch.object(self.client.http_client, 'post') as mock_post:
                # Mock responses
                def mock_get_side_effect(url, **kwargs):
                    if "/models/traits" in url:
                        response = MagicMock()
                        response.status_code = 200
                        response.json.return_value = {
                            "data": {
                                "text-embedding-3-small": {
                                    "capabilities": {
                                        "embedding_generation": True,
                                        "similarity_calculation": True
                                    },
                                    "traits": {
                                        "context_length": 8192,
                                        "max_tokens": 4096,
                                        "temperature_range": [0.0, 2.0]
                                    },
                                    "performance_metrics": {
                                        "speed": "fast",
                                        "quality": "high"
                                    }
                                }
                            }
                        }
                        return response
                    elif "models" in url:
                        response = MagicMock()
                        response.status_code = 200
                        response.json.return_value = {
                            "data": [{
                                "id": "text-embedding-3-small",
                                "name": "Text Embedding 3 Small",
                                "type": "embedding",
                                "capabilities": {
                                    "embedding_generation": True
                                },
                                "model_spec": {
                                    "capabilities": {
                                        "embedding_generation": True
                                    },
                                    "availableContextTokens": 8192
                                }
                            }]
                        }
                        return response
                    return MagicMock()
                
                def mock_post_side_effect(url, **kwargs):
                    if "embeddings" in url:
                        response = MagicMock()
                        response.status_code = 200
                        response.json.return_value = {
                            "data": [{
                                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                                "index": 0
                            }],
                            "model": "text-embedding-3-small",
                            "usage": {"total_tokens": 5}
                        }
                        return response
                    return MagicMock()
                
                mock_get.side_effect = mock_get_side_effect
                mock_post.side_effect = mock_post_side_effect
                
                # Test integration workflow
                # 1. Get available embedding models
                models = self.client.models.list()
                embedding_models = [
                    model for model in models 
                    if model.get("type") == "embedding"
                ]
                assert len(embedding_models) > 0
                selected_model = embedding_models[0]["id"]
                
                # 2. Get model traits
                traits = self.client.models_traits.get_traits()
                assert len(traits) > 0
                assert selected_model in traits
                
                # 3. Verify model capabilities
                model_traits = traits[selected_model]
                assert model_traits.has_capability("embedding_generation")
                
                # 4. Generate embeddings using the model
                text = "This is a test for embeddings integration."
                result = self.client.embeddings.generate_single(
                    text=text,
                    model=selected_model
                )

                assert result is not None
                assert isinstance(result, list)
                assert len(result) > 0
                
                # 5. Find models by capability
                embedding_capable_models = self.client.models_traits.find_models_by_capability("embedding_generation")
                assert len(embedding_capable_models) > 0
                assert selected_model in embedding_capable_models

    def test_error_propagation_integration(self):
        """Test error propagation across integrated modules."""
        with patch.object(self.client.http_client, 'get') as mock_get:
            with patch.object(self.client.http_client, 'post') as mock_post:
                # Mock error responses to raise exceptions directly
                mock_get.side_effect = VeniceAPIError("Invalid API key", status_code=401)
                mock_post.side_effect = VeniceAPIError("Invalid API key", status_code=401)
                
                # Test error propagation across modules
                modules_to_test = [
                    ("models", lambda: self.client.models.list()),
                    ("characters", lambda: self.client.characters.list()),
                    ("audio", lambda: self.client.audio.get_voices()),
                    ("embeddings", lambda: self.client.embeddings.generate_single("test", "text-embedding-3-small")),
                    ("images", lambda: self.client.images.generate("test", "dall-e-3")),
                    ("account", lambda: self.client.api_keys.list()),
                    ("billing", lambda: self.client.billing.get_usage())
                ]
                
                for module_name, test_func in modules_to_test:
                    if module_name == "audio":
                        # Audio module has hardcoded voices, so it won't raise an exception
                        result = test_func()
                        assert isinstance(result, list)
                        assert len(result) > 0
                    else:
                        with pytest.raises(VeniceAPIError) as exc_info:
                            test_func()
                        
                        assert exc_info.value.status_code == 401
                        assert "Invalid API key" in str(exc_info.value)

    def test_performance_integration(self):
        """Test performance across integrated modules."""
        import time
        
        with patch.object(self.client.http_client, 'get') as mock_get:
            with patch.object(self.client.http_client, 'post') as mock_post:
                # Mock fast responses
                def mock_fast_response(url, **kwargs):
                    response = MagicMock()
                    response.status_code = 200
                    if "models" in url:
                        response.json.return_value = {"data": []}
                    elif "characters" in url:
                        response.json.return_value = {"data": []}
                    elif "voices" in url:
                        response.json.return_value = {"data": []}
                    elif "chat/completions" in url:
                        response.json.return_value = {
                            "choices": [{"message": {"content": "Hello"}}]
                        }
                    elif "embeddings" in url:
                        response.json.return_value = {
                            "data": [{"embedding": [0.1, 0.2, 0.3], "index": 0}],
                            "model": "text-embedding-3-small"
                        }
                    return response
                
                mock_get.side_effect = mock_fast_response
                mock_post.side_effect = mock_fast_response
                
                # Test performance across modules
                start_time = time.time()
                
                # Multiple module operations
                self.client.models.list()
                self.client.characters.list()
                self.client.audio.get_voices()
                self.client.chat.complete(
                    messages=[{"role": "user", "content": "Hello"}],
                    model="llama-3.3-8b"
                )
                self.client.embeddings.generate_single(
                    text="Hello world",
                    model="text-embedding-3-small"
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # Should complete quickly with mocked responses
                assert response_time < 1.0

    def test_concurrent_integration(self):
        """Test concurrent access across integrated modules."""
        import threading
        import time
        
        with patch.object(self.client.http_client, 'get') as mock_get:
            with patch.object(self.client.http_client, 'post') as mock_post:
                # Mock responses
                def mock_response(url, **kwargs):
                    response = MagicMock()
                    response.status_code = 200
                    if "models" in url and "traits" not in url:
                        response.json.return_value = {"data": []}
                    elif "characters" in url:
                        response.json.return_value = {"data": []}
                    elif "voices" in url:
                        response.json.return_value = {"data": []}
                    elif "chat/completions" in url:
                        response.json.return_value = {
                            "choices": [{"message": {"content": "Hello"}}]
                        }
                    elif "embeddings" in url:
                        response.json.return_value = {
                            "data": [{"embedding": [0.1, 0.2, 0.3], "index": 0}],
                            "model": "text-embedding-3-small"
                        }
                    else:
                        # Default response for any other URL
                        response.json.return_value = {"data": []}
                    return response
                
                mock_get.side_effect = mock_response
                mock_post.side_effect = mock_response
                
                results = []
                errors = []
                
                def module_operation():
                    try:
                        # Mix of different module operations
                        self.client.models.list()
                        self.client.characters.list()
                        self.client.audio.get_voices()
                        self.client.chat.complete(
                            messages=[{"role": "user", "content": "Hello"}],
                            model="llama-3.3-8b"
                        )
                        self.client.embeddings.generate_single(
                            text="Hello world",
                            model="text-embedding-3-small"
                        )
                        results.append("success")
                    except Exception as e:
                        errors.append(e)
                
                # Start multiple threads
                threads = []
                for _ in range(5):
                    thread = threading.Thread(target=module_operation)
                    threads.append(thread)
                    thread.start()
                
                # Wait for all threads to complete
                for thread in threads:
                    thread.join()
                
                # Verify results
                assert len(results) == 5
                assert len(errors) == 0

    def test_data_consistency_integration(self):
        """Test data consistency across integrated modules."""
        with patch.object(self.client.http_client, 'get') as mock_get:
            # Mock consistent responses
            def mock_consistent_response(url, **kwargs):
                response = MagicMock()
                response.status_code = 200
                if "models" in url:
                    response.json.return_value = {
                        "data": [{
                            "id": "llama-3.3-8b",
                            "name": "Llama 3.3 8B",
                            "type": "text"
                        }]
                    }
                elif "characters" in url:
                    response.json.return_value = {
                        "data": [{
                            "id": "assistant-1",
                            "name": "Helpful Assistant",
                            "description": "A friendly AI assistant"
                        }]
                    }
                return response
            
            mock_get.side_effect = mock_consistent_response
            
            # Test data consistency
            # 1. Get data from multiple modules
            models1 = self.client.models.list()
            characters1 = self.client.characters.list()
            
            # 2. Get data again
            models2 = self.client.models.list()
            characters2 = self.client.characters.list()
            
            # 3. Verify consistency
            assert models1 == models2
            assert characters1 == characters2
            
            # 4. Verify data structure consistency
            assert len(models1) == len(models2)
            assert len(characters1) == len(characters2)
            
            if models1 and models2:
                assert models1[0]["id"] == models2[0]["id"]
                assert models1[0]["name"] == models2[0]["name"]
            
            if characters1 and characters2:
                assert characters1[0].id == characters2[0].id
                assert characters1[0].name == characters2[0].name
