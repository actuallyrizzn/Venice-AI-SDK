"""
Integration tests for Venice AI SDK API endpoints.

These tests verify the integration between different API components
and ensure proper data flow across the system.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from venice_sdk.venice_client import VeniceClient
from venice_sdk.config import Config
from venice_sdk.errors import VeniceAPIError


@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for API endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.api_key = os.getenv("VENICE_API_KEY", "test-api-key")
        self.config = Config(api_key=self.api_key)
        self.client = VeniceClient(self.config)

    def test_chat_to_models_integration(self):
        """Test integration between chat and models APIs."""
        # Mock the HTTP client to return realistic responses
        with patch.object(self.client.http_client, 'post') as mock_post, \
             patch.object(self.client.http_client, 'get') as mock_get:
            # Mock chat completion response
            mock_chat_response = MagicMock()
            mock_chat_response.status_code = 200
            mock_chat_response.json.return_value = {
                "choices": [{"message": {"content": "Hello! I'm a helpful assistant."}}],
                "model": "llama-3.3-8b",
                "usage": {"total_tokens": 20}
            }
            
            # Mock models list response
            mock_models_response = MagicMock()
            mock_models_response.status_code = 200
            mock_models_response.json.return_value = {
                "data": [{
                    "id": "llama-3.3-8b",
                    "name": "Llama 3.3 8B",
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
            
            # Configure mock to return different responses based on endpoint
            def mock_post_side_effect(url, **kwargs):
                if "chat/completions" in url:
                    return mock_chat_response
                return mock_chat_response

            def mock_get_side_effect(url, **kwargs):
                if "models" in url:
                    return mock_models_response
                return mock_models_response

            mock_post.side_effect = mock_post_side_effect
            mock_get.side_effect = mock_get_side_effect
            
            # Test the integration
            # 1. Get available models
            models = self.client.models.list()
            assert len(models) > 0
            assert models[0]["id"] == "llama-3.3-8b"
            
            # 2. Use a model for chat completion
            messages = [{"role": "user", "content": "Hello!"}]
            response = self.client.chat.complete(
                messages=messages,
                model=models[0]["id"],
                max_tokens=50
            )
            
            assert response is not None
            assert "choices" in response
            assert response["model"] == "llama-3.3-8b"

    def test_audio_to_characters_integration(self):
        """Test integration between audio and characters APIs."""
        with patch.object(self.client.http_client, 'get') as mock_get:
            # Mock voices response
            mock_voices_response = MagicMock()
            mock_voices_response.status_code = 200
            mock_voices_response.json.return_value = {
                "data": [{
                    "id": "alloy",
                    "name": "Alloy",
                    "category": "premium",
                    "description": "A clear and professional voice"
                }]
            }
            
            # Mock characters response
            mock_characters_response = MagicMock()
            mock_characters_response.status_code = 200
            mock_characters_response.json.return_value = {
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
            
            def mock_get_side_effect(url, **kwargs):
                if "voices" in url:
                    return mock_voices_response
                elif "characters" in url:
                    return mock_characters_response
                return mock_voices_response
            
            mock_get.side_effect = mock_get_side_effect
            
            # Test the integration
            # 1. Get available voices
            voices = self.client.audio.get_voices()
            assert len(voices) > 0
            assert voices[0].id == "alloy"
            
            # 2. Get characters that support voice synthesis
            characters = self.client.characters.list()
            assert len(characters) > 0
            
            # 3. Find characters with voice capabilities
            voice_characters = [
                char for char in characters 
                if char.has_capability("voice_synthesis")
            ]
            assert len(voice_characters) > 0

    def test_embeddings_to_models_integration(self):
        """Test integration between embeddings and models APIs."""
        with patch.object(self.client.http_client, 'post') as mock_post:
            # Mock embeddings response
            mock_embeddings_response = MagicMock()
            mock_embeddings_response.status_code = 200
            mock_embeddings_response.json.return_value = {
                "data": [{
                    "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                    "index": 0
                }],
                "model": "text-embedding-3-small",
                "usage": {
                    "prompt_tokens": 5,
                    "total_tokens": 5
                }
            }
            
            # Mock models response
            mock_models_response = MagicMock()
            mock_models_response.status_code = 200
            mock_models_response.json.return_value = {
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
            
            def mock_post_side_effect(url, **kwargs):
                if "embeddings" in url:
                    return mock_embeddings_response
                return mock_embeddings_response
            
            mock_post.side_effect = mock_post_side_effect
            
            with patch.object(self.client.http_client, 'get') as mock_get:
                mock_get.return_value = mock_models_response
                
                # Test the integration
                # 1. Get embedding models
                models = self.client.models.list()
                embedding_models = [
                    model for model in models 
                    if model.get("type") == "embedding"
                ]
                assert len(embedding_models) > 0
                
                # 2. Generate embeddings using the model
                text = "This is a test for embeddings integration."
                result = self.client.embeddings.generate_single(
                    text=text,
                    model=embedding_models[0]["id"]
                )

                assert result is not None
                assert isinstance(result, list)
                assert len(result) > 0

    def test_images_to_styles_integration(self):
        """Test integration between images and styles APIs."""
        with patch.object(self.client.http_client, 'post') as mock_post:
            # Mock image generation response
            mock_image_response = MagicMock()
            mock_image_response.status_code = 200
            mock_image_response.json.return_value = {
                "data": [{
                    "url": "https://example.com/generated-image.png",
                    "revised_prompt": "A beautiful sunset over mountains"
                }],
                "created": 1234567890
            }
            
            mock_post.return_value = mock_image_response
            
            with patch.object(self.client.http_client, 'get') as mock_get:
                # Mock styles response
                mock_styles_response = MagicMock()
                mock_styles_response.status_code = 200
                mock_styles_response.json.return_value = {
                    "data": [{
                        "id": "vivid",
                        "name": "Vivid",
                        "description": "High contrast and vibrant colors",
                        "category": "artistic",
                        "preview_url": "https://example.com/vivid-preview.jpg"
                    }]
                }
                
                mock_get.return_value = mock_styles_response
                
                # Test the integration
                # 1. Get available styles
                styles = self.client.image_styles.list_styles()
                assert len(styles) > 0
                assert styles[0].id == "vivid"
                
                # 2. Generate image with a specific style
                result = self.client.images.generate(
                    prompt="A beautiful landscape",
                    model="dall-e-3",
                    style=styles[0].id
                )
                
                assert result is not None
                assert hasattr(result, 'url')
                assert result.url is not None

    def test_account_to_billing_integration(self):
        """Test integration between account and billing APIs."""
        with patch.object(self.client.http_client, 'get') as mock_get:
            # Mock API keys response
            mock_keys_response = MagicMock()
            mock_keys_response.status_code = 200
            mock_keys_response.json.return_value = {
                "data": [{
                    "id": "key-123",
                    "name": "Test Key",
                    "created": 1234567890,
                    "last_used": 1234567890,
                    "permissions": ["read", "write"],
                    "is_active": True
                }]
            }
            
            # Mock billing response
            mock_billing_response = MagicMock()
            mock_billing_response.status_code = 200
            mock_billing_response.json.return_value = {
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
            
            def mock_get_side_effect(url, **kwargs):
                if "api-keys" in url:
                    return mock_keys_response
                elif "billing" in url:
                    return mock_billing_response
                return mock_keys_response
            
            mock_get.side_effect = mock_get_side_effect
            
            # Test the integration
            # 1. Get API keys
            api_keys = self.client.api_keys.list()
            assert len(api_keys) > 0
            assert api_keys[0].id == "key-123"
            
            # 2. Get billing information
            usage_info = self.client.billing.get_usage()
            assert usage_info is not None
            assert usage_info.total_usage == 1000
            assert usage_info.credits_remaining == 5000

    def test_models_advanced_integration(self):
        """Test integration between models advanced APIs."""
        with patch.object(self.client.http_client, 'get') as mock_get:
            # Mock traits response
            mock_traits_response = MagicMock()
            mock_traits_response.status_code = 200
            mock_traits_response.json.return_value = {
                "data": {
                    "llama-3.3-8b": {
                        "capabilities": {
                            "function_calling": True,
                            "streaming": True,
                            "web_search": False
                        },
                        "traits": {
                            "context_length": 4096,
                            "max_tokens": 2048,
                            "temperature_range": [0.0, 2.0]
                        },
                        "performance_metrics": {
                            "speed": "fast",
                            "quality": "high"
                        }
                    }
                }
            }
            
            # Mock compatibility response
            mock_compatibility_response = MagicMock()
            mock_compatibility_response.status_code = 200
            mock_compatibility_response.json.return_value = {
                "data": {
                    "openai_to_venice": {
                        "gpt-3.5-turbo": "llama-3.3-8b",
                        "gpt-4": "llama-3.3-70b"
                    },
                    "venice_to_openai": {
                        "llama-3.3-8b": "gpt-3.5-turbo",
                        "llama-3.3-70b": "gpt-4"
                    }
                }
            }
            
            def mock_get_side_effect(url, **kwargs):
                if "traits" in url:
                    return mock_traits_response
                elif "compatibility" in url:
                    return mock_compatibility_response
                return mock_traits_response
            
            mock_get.side_effect = mock_get_side_effect
            
            # Test the integration
            # 1. Get model traits
            traits = self.client.models_traits.get_traits()
            assert len(traits) > 0
            assert "llama-3.3-8b" in traits
            
            # 2. Get compatibility mapping
            mapping = self.client.models_compatibility.get_mapping()
            assert mapping is not None
            assert hasattr(mapping, 'openai_to_venice')
            
            # 3. Use traits to find compatible models
            model_traits = traits["llama-3.3-8b"]
            if model_traits.has_capability("function_calling"):
                # Find models with function calling capability
                function_models = self.client.models_traits.find_models_by_capability("function_calling")
                assert len(function_models) > 0
                assert "llama-3.3-8b" in function_models

    def test_end_to_end_workflow_integration(self):
        """Test complete end-to-end workflow integration."""
        with patch.object(self.client.http_client, 'get') as mock_get:
            with patch.object(self.client.http_client, 'post') as mock_post:
                # Mock all responses for a complete workflow
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
                            "choices": [{"message": {"content": "Hello! I'm here to help."}}],
                            "model": "llama-3.3-8b",
                            "usage": {"total_tokens": 15}
                        }
                        return response
                    elif "embeddings" in url:
                        response = MagicMock()
                        response.status_code = 200
                        response.json.return_value = {
                            "data": [{
                                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                                "index": 0,
                                "object": "embedding"
                            }],
                            "model": "text-embedding-3-small",
                            "usage": {"total_tokens": 5}
                        }
                        return response
                    return MagicMock()
                
                mock_get.side_effect = mock_get_side_effect
                mock_post.side_effect = mock_post_side_effect
                
                # Complete workflow test
                # 1. Discover available models
                models = self.client.models.list()
                assert len(models) > 0
                text_model = models[0]
                
                # 2. Discover available characters
                characters = self.client.characters.list()
                assert len(characters) > 0
                assistant = characters[0]
                
                # 3. Use character with model for chat
                character_params = assistant.to_venice_parameters()
                messages = [
                    {"role": "user", "content": "Hello!"}
                ]
                
                chat_response = self.client.chat.complete(
                    messages=messages,
                    model=text_model["id"],
                    temperature=0.7,
                    max_tokens=100
                )
                
                assert chat_response is not None
                assert "choices" in chat_response
                
                # 4. Generate embeddings for the conversation
                conversation_text = " ".join([msg["content"] for msg in messages])
                embedding_result = self.client.embeddings.generate_single(
                    text=conversation_text,
                    model="text-embedding-3-small"
                )
                
                assert embedding_result is not None
                assert isinstance(embedding_result, list)
                assert len(embedding_result) > 0
                
                # 5. Get account summary
                summary = self.client.get_account_summary()
                assert summary is not None
                assert isinstance(summary, dict)

    def test_error_handling_integration(self):
        """Test error handling across integrated APIs."""
        with patch.object(self.client.http_client, 'get') as mock_get:
            with patch.object(self.client.http_client, 'post') as mock_post:
                # Mock API error response by making the HTTP client raise VeniceAPIError
                from venice_sdk.errors import VeniceAPIError
                
                def mock_get_error(url, **kwargs):
                    raise VeniceAPIError("Invalid API key", status_code=401)
                
                def mock_post_error(url, **kwargs):
                    raise VeniceAPIError("Invalid API key", status_code=401)

                mock_get.side_effect = mock_get_error
                mock_post.side_effect = mock_post_error

                # Test error propagation across APIs
                with pytest.raises(VeniceAPIError) as exc_info:
                    self.client.models.list()
                
                assert exc_info.value.status_code == 401
                assert "Invalid API key" in str(exc_info.value)
                
                with pytest.raises(VeniceAPIError) as exc_info:
                    self.client.chat.complete(
                        messages=[{"role": "user", "content": "Hello"}],
                        model="llama-3.3-8b"
                    )
                
                assert exc_info.value.status_code == 401

    def test_performance_integration(self):
        """Test performance across integrated APIs."""
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
                    elif "chat/completions" in url:
                        response.json.return_value = {
                            "choices": [{"message": {"content": "Hello"}}]
                        }
                    return response
                
                mock_get.side_effect = mock_fast_response
                mock_post.side_effect = mock_fast_response
                
                # Test performance
                start_time = time.time()
                
                # Multiple API calls
                self.client.models.list()
                self.client.characters.list()
                self.client.chat.complete(
                    messages=[{"role": "user", "content": "Hello"}],
                    model="llama-3.3-8b"
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # Should complete quickly (mocked responses)
                assert response_time < 1.0  # Less than 1 second

    def test_concurrent_integration(self):
        """Test concurrent access across integrated APIs."""
        import threading
        import time
        
        with patch.object(self.client.http_client, 'get') as mock_get:
            with patch.object(self.client.http_client, 'post') as mock_post:
                # Mock responses
                def mock_response(url, **kwargs):
                    response = MagicMock()
                    response.status_code = 200
                    if "models" in url:
                        response.json.return_value = {"data": []}
                    elif "characters" in url:
                        response.json.return_value = {"data": []}
                    elif "chat/completions" in url:
                        response.json.return_value = {
                            "choices": [{"message": {"content": "Hello"}}]
                        }
                    return response
                
                mock_get.side_effect = mock_response
                mock_post.side_effect = mock_response
                
                results = []
                errors = []
                
                def api_call():
                    try:
                        # Mix of different API calls
                        models = self.client.models.list()
                        characters = self.client.characters.list()
                        chat_response = self.client.chat.complete(
                            messages=[{"role": "user", "content": "Hello"}],
                            model="llama-3.3-8b"
                        )
                        results.append("success")
                    except Exception as e:
                        errors.append(e)
                
                # Start multiple threads
                threads = []
                for _ in range(5):
                    thread = threading.Thread(target=api_call)
                    threads.append(thread)
                    thread.start()
                
                # Wait for all threads to complete
                for thread in threads:
                    thread.join()
                
                # Verify results
                assert len(results) == 5
                assert len(errors) == 0
