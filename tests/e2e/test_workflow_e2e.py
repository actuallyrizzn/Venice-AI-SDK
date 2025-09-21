"""
End-to-end tests for complete Venice AI SDK workflows.

These tests verify complete user workflows from start to finish,
testing the entire system as a user would interact with it.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from venice_sdk.venice_client import VeniceClient, create_client
from venice_sdk.config import Config, load_config
from venice_sdk.errors import VeniceAPIError


@pytest.mark.e2e
class TestWorkflowE2E:
    """End-to-end workflow tests."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.api_key = os.getenv("VENICE_API_KEY", "test-api-key")
        self.config = Config(api_key=self.api_key)

    def test_complete_ai_assistant_workflow(self):
        """Test complete AI assistant workflow from setup to conversation."""
        # Mock all API responses for a complete workflow
        with patch('venice_sdk.venice_client.HTTPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            # Mock models discovery
            mock_models_response = MagicMock()
            mock_models_response.status_code = 200
            mock_models_response.json.return_value = {
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
            
            # Mock characters discovery
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
            
            # Mock chat completion
            mock_chat_response = MagicMock()
            mock_chat_response.status_code = 200
            mock_chat_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": "Hello! I'm your helpful AI assistant. How can I assist you today?",
                        "role": "assistant"
                    }
                }],
                "model": "llama-3.3-8b",
                "usage": {"total_tokens": 25}
            }
            
            # Mock streaming response
            def mock_stream_generator():
                yield {"choices": [{"delta": {"content": "Hello"}}]}
                yield {"choices": [{"delta": {"content": "! How can I help?"}}]}
                yield {"choices": [{"delta": {"content": ""}}]}
            
            # Configure mock client
            def mock_get_side_effect(url, **kwargs):
                if "models" in url:
                    return mock_models_response
                elif "characters" in url:
                    return mock_characters_response
                return mock_models_response
            
            def mock_post_side_effect(url, **kwargs):
                if "chat/completions" in url:
                    return mock_chat_response
                return mock_chat_response
            
            def mock_stream_side_effect(url, **kwargs):
                return mock_stream_generator()
            
            mock_client.get.side_effect = mock_get_side_effect
            mock_client.post.side_effect = mock_post_side_effect
            mock_client.stream.side_effect = mock_stream_side_effect
            
            # Complete E2E workflow
            # 1. Initialize client
            client = VeniceClient(self.config)
            
            # 2. Discover available models
            models = client.models.list()
            assert len(models) > 0
            selected_model = models[0]
            assert selected_model["id"] == "llama-3.3-8b"
            
            # 3. Discover available characters
            characters = client.characters.list()
            assert len(characters) > 0
            selected_character = characters[0]
            assert selected_character.id == "assistant-1"
            
            # 4. Configure character for conversation
            character_params = selected_character.to_venice_parameters()
            assert "character_slug" in character_params
            
            # 5. Start conversation
            messages = [
                {"role": "user", "content": "Hello! Can you help me with a question?"}
            ]
            
            response = client.chat.complete(
                messages=messages,
                model=selected_model["id"],
                temperature=0.7,
                max_tokens=100,
                **character_params
            )
            
            assert response is not None
            assert "choices" in response
            assert len(response["choices"]) > 0
            assert "message" in response["choices"][0]
            assert "content" in response["choices"][0]["message"]
            
            # 6. Continue conversation
            messages.append({
                "role": "assistant",
                "content": response["choices"][0]["message"]["content"]
            })
            messages.append({
                "role": "user",
                "content": "What are your capabilities?"
            })
            
            follow_up_response = client.chat.complete(
                messages=messages,
                model=selected_model["id"],
                temperature=0.7,
                max_tokens=100,
                **character_params
            )
            
            assert follow_up_response is not None
            assert "choices" in follow_up_response
            
            # 7. Test streaming conversation
            messages.append({
                "role": "assistant",
                "content": follow_up_response["choices"][0]["message"]["content"]
            })
            messages.append({
                "role": "user",
                "content": "Can you explain that in more detail?"
            })
            
            stream_chunks = list(client.chat.complete(
                messages=messages,
                model=selected_model["id"],
                temperature=0.7,
                max_tokens=100,
                stream=True,
                **character_params
            ))
            
            assert len(stream_chunks) > 0
            assert all(isinstance(chunk, str) for chunk in stream_chunks)

    def test_content_creation_workflow(self):
        """Test complete content creation workflow."""
        with patch('venice_sdk.venice_client.HTTPClient') as mock_client_class:
            with patch('requests.get') as mock_requests_get:
                mock_client = MagicMock()
                mock_client_class.return_value = mock_client
                
                # Mock image generation
                mock_image_response = MagicMock()
                mock_image_response.status_code = 200
                mock_image_response.json.return_value = {
                    "data": [{
                        "url": "https://example.com/generated-image.png",
                        "revised_prompt": "A beautiful sunset over mountains with vibrant colors"
                    }],
                    "created": 1234567890
                }
                
                # Mock image styles
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
                
                # Mock audio generation
                mock_audio_response = MagicMock()
                mock_audio_response.status_code = 200
                mock_audio_response.content = b"fake_audio_data"
                
                # Mock voices
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
                
                # Configure mock client
                def mock_get_side_effect(url, **kwargs):
                    if "styles" in url:
                        return mock_styles_response
                    elif "voices" in url:
                        return mock_voices_response
                    return mock_styles_response
                
                def mock_post_side_effect(url, **kwargs):
                    if "images/generations" in url:
                        return mock_image_response
                    elif "audio/speech" in url:
                        return mock_audio_response
                    return mock_image_response
                
                mock_client.get.side_effect = mock_get_side_effect
                mock_client.post.side_effect = mock_post_side_effect

                # Mock image download
                mock_download_response = MagicMock()
                mock_download_response.status_code = 200
                mock_download_response.content = b"fake_image_data"
                mock_download_response.raise_for_status.return_value = None  # Don't raise an exception
                mock_requests_get.return_value = mock_download_response

                # Complete content creation workflow
                client = VeniceClient(self.config)

                # 1. Discover available styles
                styles = client.image_styles.list_styles()
                assert len(styles) > 0
                selected_style = styles[0]
                assert selected_style.id == "vivid"

                # 2. Generate image with style
                image_result = client.images.generate(
                    prompt="A beautiful sunset over mountains",
                    model="dall-e-3",
                    style=selected_style.id,
                    size="1024x1024",
                    quality="hd"
                )
                
                assert image_result is not None
                assert hasattr(image_result, 'url')
                assert image_result.url is not None
                
                # 3. Save image to file
                with tempfile.TemporaryDirectory() as temp_dir:
                    output_path = Path(temp_dir) / "generated_image.png"
                    saved_path = image_result.save(output_path)
                    assert saved_path == output_path
                    assert output_path.exists()
                
                # 4. Discover available voices
                voices = client.audio.get_voices()
                assert len(voices) > 0
                selected_voice = voices[0]
                assert selected_voice.id == "af_alloy"
                
                # 5. Generate audio narration
                audio_result = client.audio.speech(
                    input_text="This is a beautiful sunset over mountains with vibrant colors.",
                    voice=selected_voice.id,
                    model="tts-1",
                    response_format="mp3"
                )
                
                assert audio_result is not None
                assert hasattr(audio_result, 'audio_data')
                assert hasattr(audio_result, 'format')
                assert audio_result.audio_data is not None
                
                # 6. Save audio to file
                with tempfile.TemporaryDirectory() as temp_dir:
                    audio_path = Path(temp_dir) / "narration.mp3"
                    saved_audio_path = audio_result.save(audio_path)
                    assert saved_audio_path == audio_path
                    assert audio_path.exists()

    def test_data_analysis_workflow(self):
        """Test complete data analysis workflow with embeddings."""
        with patch('venice_sdk.venice_client.HTTPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            # Mock embeddings generation
            mock_embeddings_response = MagicMock()
            mock_embeddings_response.status_code = 200
            mock_embeddings_response.json.return_value = {
                "data": [
                    {"embedding": [0.1, 0.2, 0.3, 0.4, 0.5], "index": 0},
                    {"embedding": [0.2, 0.3, 0.4, 0.5, 0.6], "index": 1},
                    {"embedding": [0.3, 0.4, 0.5, 0.6, 0.7], "index": 2}
                ],
                "model": "text-embedding-3-small",
                "usage": {"total_tokens": 15}
            }
            
            # Mock models for embeddings
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
            
            # Configure mock client
            def mock_get_side_effect(url, **kwargs):
                if "models" in url:
                    return mock_models_response
                return mock_models_response
            
            def mock_post_side_effect(url, **kwargs):
                if "embeddings" in url:
                    return mock_embeddings_response
                return mock_embeddings_response
            
            mock_client.get.side_effect = mock_get_side_effect
            mock_client.post.side_effect = mock_post_side_effect
            
            # Complete data analysis workflow
            client = VeniceClient(self.config)
            
            # 1. Discover embedding models
            models = client.models.list()
            embedding_models = [
                model for model in models 
                if model.get("type") == "embedding"
            ]
            assert len(embedding_models) > 0
            selected_model = embedding_models[0]["id"]
            
            # 2. Prepare documents for analysis
            documents = [
                "Machine learning is a subset of artificial intelligence.",
                "Deep learning uses neural networks with multiple layers.",
                "Natural language processing helps computers understand text."
            ]
            
            # 3. Generate embeddings for documents
            embeddings_result = client.embeddings.generate(
                input_text=documents,
                model=selected_model
            )
            
            assert embeddings_result is not None
            assert hasattr(embeddings_result, 'embeddings')
            assert len(embeddings_result.embeddings) == len(documents)
            
            # 4. Perform similarity analysis
            from venice_sdk.embeddings import EmbeddingSimilarity

            embeddings = embeddings_result.embeddings
            similarities = []

            for i in range(len(embeddings)):
                for j in range(i + 1, len(embeddings)):
                    similarity = EmbeddingSimilarity.cosine_similarity(
                        embeddings[i].embedding, embeddings[j].embedding
                    )
                    similarities.append(similarity)
            
            assert len(similarities) > 0
            assert all(isinstance(sim, float) for sim in similarities)
            
            # 5. Perform semantic search
            from venice_sdk.embeddings import SemanticSearch
            
            search = SemanticSearch(client.embeddings)
            search.add_documents(documents)
            
            query = "What is artificial intelligence?"
            results = search.search(query, top_k=2)
            
            assert isinstance(results, list)
            assert len(results) <= 2
            
            # 6. Perform clustering analysis
            from venice_sdk.embeddings import EmbeddingClustering
            
            embedding_vectors = [emb.embedding for emb in embeddings]
            clusters = EmbeddingClustering.kmeans_clusters(embedding_vectors, k=2)
            
            assert isinstance(clusters, list)
            assert len(clusters) == len(documents)
            assert all(0 <= cluster_id < 2 for cluster_id in clusters)

    def test_account_management_workflow(self):
        """Test complete account management workflow."""
        with patch('venice_sdk.venice_client.HTTPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
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
                            "tokens": 25000,
                            "cost": 12.75
                        }
                    }
                }
            }
            
            # Mock rate limits response
            mock_limits_response = MagicMock()
            mock_limits_response.status_code = 200
            mock_limits_response.json.return_value = {
                "data": {
                    "requests_per_minute": 60,
                    "requests_per_hour": 1000,
                    "requests_per_day": 10000,
                    "tokens_per_minute": 10000,
                    "tokens_per_hour": 100000,
                    "tokens_per_day": 1000000,
                    "current_usage": {
                        "requests_per_minute": 10,
                        "tokens_per_minute": 1000
                    }
                }
            }
            
            # Configure mock client
            def mock_get_side_effect(url, **kwargs):
                if "api_keys" in url and "rate_limits" in url:
                    return mock_limits_response
                elif "api_keys" in url:
                    return mock_keys_response
                elif "billing" in url:
                    return mock_billing_response
                return mock_keys_response
            
            mock_client.get.side_effect = mock_get_side_effect
            
            # Complete account management workflow
            client = VeniceClient(self.config)
            
            # 1. List API keys
            api_keys = client.api_keys.list()
            assert len(api_keys) > 0
            assert api_keys[0].id == "key-123"
            assert api_keys[0].is_active is True
            
            # 2. Check rate limits
            rate_limits = client.api_keys.get_rate_limits()
            assert rate_limits is not None
            assert rate_limits.requests_per_minute == 60
            assert rate_limits.requests_per_day == 10000
            
            # 3. Get usage information
            usage_info = client.billing.get_usage()
            assert usage_info is not None
            assert usage_info.total_usage == 1000
            assert usage_info.credits_remaining == 5000
            
            # 4. Get account summary
            summary = client.get_account_summary()
            assert summary is not None
            assert "api_keys" in summary
            assert "usage" in summary
            assert "rate_limits" in summary
            
            # 5. Check rate limit status
            status = client.get_rate_limit_status()
            assert status is not None
            assert "current_usage" in status
            assert "limits" in status
            assert "status" in status

    def test_model_selection_workflow(self):
        """Test complete model selection and recommendation workflow."""
        with patch('venice_sdk.venice_client.HTTPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            # Mock models response
            mock_models_response = MagicMock()
            mock_models_response.status_code = 200
            mock_models_response.json.return_value = {
                "data": [
                    {
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
                                "supportsWebSearch": False,
                                "supportsLogProbs": True
                            },
                            "availableContextTokens": 4096
                        }
                    },
                    {
                        "id": "llama-3.3-70b",
                        "name": "Llama 3.3 70B",
                        "type": "text",
                        "capabilities": {
                            "supportsFunctionCalling": True,
                            "supportsWebSearch": True
                        },
                        "model_spec": {
                            "capabilities": {
                                "supportsFunctionCalling": True,
                                "supportsWebSearch": True,
                                "supportsLogProbs": True
                            },
                            "availableContextTokens": 8192
                        }
                    }
                ]
            }
            
            # Mock traits response (same as models response since get_traits uses /models endpoint)
            mock_traits_response = mock_models_response
            
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
            
            # Configure mock client
            def mock_get_side_effect(url, **kwargs):
                if "models/compatibility" in url:
                    return mock_compatibility_response
                elif "models" in url:
                    return mock_models_response
                return mock_models_response
            
            mock_client.get.side_effect = mock_get_side_effect
            
            # Complete model selection workflow
            client = VeniceClient(self.config)
            
            # 1. Discover available models
            models = client.models.list()
            assert len(models) > 0
            
            # 2. Get model traits
            traits = client.models_traits.get_traits()
            assert len(traits) > 0
            assert "llama-3.3-8b" in traits
            assert "llama-3.3-70b" in traits
            
            # 3. Find models by capability
            function_models = client.models_traits.find_models_by_capability("supportsFunctionCalling")
            assert len(function_models) > 0
            assert "llama-3.3-8b" in function_models
            assert "llama-3.3-70b" in function_models
            
            # 4. Get best models for task
            chat_models = client.models_traits.get_best_models_for_task("chat")
            assert len(chat_models) > 0
            
            # 5. Get compatibility mapping
            mapping = client.models_compatibility.get_mapping()
            assert mapping is not None
            assert hasattr(mapping, 'openai_to_venice')
            assert "gpt-3.5-turbo" in mapping.openai_to_venice
            
            # 6. Get model recommendations
            recommendations = client.models_traits.get_best_models_for_task("chat")
            assert len(recommendations) > 0

    def test_error_recovery_workflow(self):
        """Test error recovery and resilience workflow."""
        with patch('venice_sdk.venice_client.HTTPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            # Mock error responses
            mock_error_response = MagicMock()
            mock_error_response.status_code = 429
            mock_error_response.json.return_value = {
                "error": {
                    "message": "Rate limit exceeded",
                    "type": "rate_limit_exceeded",
                    "retry_after": 60
                }
            }
            
            # Mock success response after retry
            mock_success_response = MagicMock()
            mock_success_response.status_code = 200
            mock_success_response.json.return_value = {
                "choices": [{"message": {"content": "Hello! I'm here to help."}}],
                "model": "llama-3.3-8b",
                "usage": {"total_tokens": 15}
            }
            
            # Configure mock client to fail first, then succeed
            call_count = 0
            def mock_post_side_effect(url, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    from venice_sdk.errors import VeniceAPIError
                    raise VeniceAPIError("Rate limit exceeded", status_code=429)
                else:
                    return mock_success_response

            mock_client.post.side_effect = mock_post_side_effect
            
            # Test error recovery workflow
            client = VeniceClient(self.config)
            
            # 1. First call should fail with rate limit
            with pytest.raises(VeniceAPIError) as exc_info:
                client.chat.complete(
                    messages=[{"role": "user", "content": "Hello"}],
                    model="llama-3.3-8b"
                )
            
            assert exc_info.value.status_code == 429
            assert "Rate limit exceeded" in str(exc_info.value)
            
            # 2. Second call should succeed (simulating retry)
            response = client.chat.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-8b"
            )
            
            assert response is not None
            assert "choices" in response

    def test_performance_optimization_workflow(self):
        """Test performance optimization workflow."""
        import time
        
        with patch('venice_sdk.venice_client.HTTPClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
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
            
            mock_client.get.side_effect = mock_fast_response
            mock_client.post.side_effect = mock_fast_response
            
            # Test performance optimization workflow
            client = VeniceClient(self.config)
            
            # 1. Measure initial performance
            start_time = time.time()
            
            # 2. Perform multiple operations
            models = client.models.list()
            characters = client.characters.list()
            response = client.chat.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-8b"
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # 3. Verify performance
            assert response_time < 1.0  # Should be fast with mocked responses
            assert models is not None
            assert characters is not None
            assert response is not None
            
            # 4. Test caching behavior
            start_time = time.time()
            
            # Second call should be faster due to caching
            models2 = client.models.list()
            characters2 = client.characters.list()
            
            end_time = time.time()
            cached_response_time = end_time - start_time
            
            # Cached calls should be faster
            assert cached_response_time < response_time
            assert models == models2
            assert characters == characters2

    def test_configuration_management_workflow(self):
        """Test configuration management workflow."""
        # Test configuration loading and management
        with patch.dict(os.environ, {
            'VENICE_API_KEY': 'test-api-key',
            'VENICE_BASE_URL': 'https://api.venice.ai/api/v1',
            'VENICE_DEFAULT_MODEL': 'llama-3.3-8b',
            'VENICE_TIMEOUT': '60',
            'VENICE_MAX_RETRIES': '5',
            'VENICE_RETRY_DELAY': '2'
        }):
            # 1. Load configuration from environment
            config = load_config()
            assert config.api_key == 'test-api-key'
            assert config.base_url == 'https://api.venice.ai/api/v1'
            assert config.default_model == 'llama-3.3-8b'
            assert config.timeout == 60
            assert config.max_retries == 5
            assert config.retry_delay == 2
            
            # 2. Create client with configuration
            client = VeniceClient(config)
            assert client.config == config
            
            # 3. Test configuration overrides
            custom_config = Config(
                api_key='custom-key',
                base_url='https://custom-api.example.com/v1',
                default_model='custom-model',
                timeout=120,
                max_retries=10,
                retry_delay=5
            )
            
            custom_client = VeniceClient(custom_config)
            assert custom_client.config.api_key == 'custom-key'
            assert custom_client.config.base_url == 'https://custom-api.example.com/v1'
            assert custom_client.config.default_model == 'custom-model'
            assert custom_client.config.timeout == 120
            assert custom_client.config.max_retries == 10
            assert custom_client.config.retry_delay == 5
            
            # 4. Test create_client convenience function
            convenience_client = create_client(
                api_key='convenience-key',
                base_url='https://convenience-api.example.com/v1'
            )
            assert convenience_client.config.api_key == 'convenience-key'
            assert convenience_client.config.base_url == 'https://convenience-api.example.com/v1'
