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
                    "id": "af_alloy",
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
            assert voices[0].id == "af_alloy"
            
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

    def test_video_to_models_integration(self):
        """Test integration between video and models APIs."""
        with patch.object(self.client.http_client, 'get') as mock_get, \
             patch.object(self.client.http_client, 'post') as mock_post:
            # Mock models list response
            mock_models_response = MagicMock()
            mock_models_response.status_code = 200
            mock_models_response.json.return_value = {
                "data": [{
                    "id": "kling-2.6-pro-text-to-video",
                    "name": "Kling 2.6 Pro",
                    "type": "video",
                    "model_spec": {
                        "capabilities": {
                            "textToVideo": True,
                            "imageToVideo": False
                        }
                    }
                }, {
                    "id": "kling-2.6-pro-image-to-video",
                    "name": "Kling 2.6 Pro Image",
                    "type": "video",
                    "model_spec": {
                        "capabilities": {
                            "textToVideo": False,
                            "imageToVideo": True
                        }
                    }
                }]
            }
            
            # Mock video queue response
            mock_queue_response = MagicMock()
            mock_queue_response.status_code = 200
            mock_queue_response.json.return_value = {
                "job_id": "video_job_123",
                "status": "queued",
                "created_at": "2024-01-01T00:00:00Z"
            }
            
            # Mock video retrieve response
            mock_retrieve_response = MagicMock()
            mock_retrieve_response.status_code = 200
            mock_retrieve_response.json.return_value = {
                "job_id": "video_job_123",
                "status": "completed",
                "video_url": "https://example.com/video.mp4",
                "progress": 100.0,
                "completed_at": "2024-01-01T00:00:10Z"
            }
            
            def mock_get_side_effect(url, **kwargs):
                if "models" in url:
                    return mock_models_response
                return mock_models_response
            
            def mock_post_side_effect(url, **kwargs):
                if "video/queue" in url:
                    return mock_queue_response
                elif "video/retrieve" in url:
                    return mock_retrieve_response
                return mock_queue_response
            
            mock_get.side_effect = mock_get_side_effect
            mock_post.side_effect = mock_post_side_effect
            
            # Test the integration
            # 1. Get available video models
            models = self.client.models.list()
            video_models = [
                model for model in models 
                if model.get("type") == "video"
            ]
            assert len(video_models) > 0
            
            # 2. Queue video generation using a video model
            text_to_video_model = next(
                (m for m in video_models if m.get("id") == "kling-2.6-pro-text-to-video"),
                None
            )
            assert text_to_video_model is not None
            
            job = self.client.video.queue(
                model=text_to_video_model["id"],
                prompt="A beautiful sunset over the ocean",
                duration=5,
                resolution="1080p"
            )
            
            assert job is not None
            assert job.job_id == "video_job_123"
            assert job.status == "queued"
            
            # 3. Retrieve video job status (model is required)
            retrieved_job = self.client.video.retrieve(job.job_id, model=text_to_video_model["id"])
            assert retrieved_job.status == "completed"
            assert retrieved_job.video_url == "https://example.com/video.mp4"

    def test_video_quote_integration(self):
        """Test integration between video quote and queue APIs."""
        with patch.object(self.client.http_client, 'post') as mock_post:
            # Mock quote response
            mock_quote_response = MagicMock()
            mock_quote_response.status_code = 200
            mock_quote_response.json.return_value = {
                "estimated_cost": 0.50,
                "currency": "USD",
                "estimated_duration": 120,
                "pricing_breakdown": {
                    "base_cost": 0.30,
                    "duration_cost": 0.20
                }
            }
            
            # Mock queue response
            mock_queue_response = MagicMock()
            mock_queue_response.status_code = 200
            mock_queue_response.json.return_value = {
                "job_id": "video_job_123",
                "status": "queued"
            }
            
            call_count = 0
            def mock_post_side_effect(url, **kwargs):
                nonlocal call_count
                call_count += 1
                if "video/quote" in url:
                    return mock_quote_response
                elif "video/queue" in url:
                    return mock_queue_response
                return mock_quote_response
            
            mock_post.side_effect = mock_post_side_effect
            
            # Test the integration
            # 1. Get quote first
            quote = self.client.video.quote(
                model="kling-2.6-pro-text-to-video",
                prompt="A cat playing with yarn",
                duration=3,
                resolution="720p"
            )
            
            assert quote.estimated_cost == 0.50
            assert quote.currency == "USD"
            
            # 2. Queue the job with same parameters
            job = self.client.video.queue(
                model="kling-2.6-pro-text-to-video",
                prompt="A cat playing with yarn",
                duration=3,
                resolution="720p"
            )
            
            assert job.job_id == "video_job_123"
            assert call_count == 2  # Quote + Queue

    def test_images_to_video_integration(self):
        """Test integration between images and video APIs."""
        with patch.object(self.client.http_client, 'post') as mock_post, \
             patch('requests.get') as mock_requests_get:
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
            
            # Mock image download
            mock_image_download = MagicMock()
            mock_image_download.status_code = 200
            mock_image_download.content = b"fake_image_data"
            mock_image_download.raise_for_status.return_value = None
            mock_requests_get.return_value = mock_image_download
            
            # Mock video queue response
            mock_video_queue_response = MagicMock()
            mock_video_queue_response.status_code = 200
            mock_video_queue_response.json.return_value = {
                "job_id": "video_job_123",
                "status": "queued"
            }
            
            call_count = 0
            def mock_post_side_effect(url, **kwargs):
                nonlocal call_count
                call_count += 1
                if "images/generations" in url:
                    return mock_image_response
                elif "video/queue" in url:
                    return mock_video_queue_response
                return mock_image_response
            
            mock_post.side_effect = mock_post_side_effect
            
            # Test the integration workflow
            # 1. Generate an image
            image_result = self.client.images.generate(
                prompt="A serene mountain landscape",
                model="dall-e-3",
                size="1024x1024"
            )
            
            assert image_result is not None
            assert image_result.url is not None
            
            # 2. Use the generated image for image-to-video
            job = self.client.video.queue(
                model="kling-2.6-pro-image-to-video",
                image=image_result.url,
                prompt="Animate this image with gentle movement",
                duration=3,
                resolution="720p"
            )
            
            assert job is not None
            assert job.job_id == "video_job_123"
            assert call_count == 2  # Image generation + Video queue

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
                "data": [
                    {
                        "timestamp": "2024-01-01T12:00:00Z",
                        "sku": "llama-3.3-8b-llm-output-mtoken",
                        "pricePerUnitUsd": 2,
                        "units": 0.5,
                        "amount": -1.0,
                        "currency": "VCU",
                        "notes": "API Inference"
                    }
                ]
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
            assert usage_info.total_usage == 1000  # Calculated from amount * 1000
            assert usage_info.credits_remaining == 0  # Not available in API response

    def test_models_advanced_integration(self):
        """Test integration between models advanced APIs."""
        with patch.object(self.client.http_client, 'get') as mock_get:
            # Mock traits response (same as models response since get_traits uses /models endpoint)
            mock_traits_response = MagicMock()
            mock_traits_response.status_code = 200
            mock_traits_response.json.return_value = {
                "data": [
                    {
                        "id": "llama-3.3-8b",
                        "model_spec": {
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
                            "availableContextTokens": 4096
                        }
                    }
                ]
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
                if "compatibility" in url:
                    return mock_compatibility_response
                elif "models" in url:
                    return mock_traits_response
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
