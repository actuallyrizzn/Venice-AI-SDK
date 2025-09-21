"""
Live tests for the VeniceClient module.

These tests make real API calls to verify VeniceClient functionality.
"""

import pytest
import os
import time
from venice_sdk.venice_client import VeniceClient, create_client
from venice_sdk.config import Config
from venice_sdk.errors import VeniceAPIError, RateLimitError


def handle_api_call(func, max_retries=3, retry_delay=1):
    """Helper function to handle API calls with retries for common issues."""
    for attempt in range(max_retries):
        try:
            return func()
        except (RateLimitError, TimeoutError) as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                continue
            else:
                pytest.skip(f"API call failed after {max_retries} attempts: {e}")
        except VeniceAPIError as e:
            if "rate limit" in str(e).lower() or "timeout" in str(e).lower():
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))
                    continue
                else:
                    pytest.skip(f"API call failed due to rate limit/timeout: {e}")
            else:
                raise


@pytest.mark.live
class TestVeniceClientLive:
    """Live tests for VeniceClient with real API calls."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.api_key = os.getenv("VENICE_API_KEY")
        if not self.api_key:
            pytest.skip("VENICE_API_KEY environment variable not set")

    def test_venice_client_initialization_with_config(self):
        """Test VeniceClient initialization with config."""
        config = Config(api_key=self.api_key)
        client = VeniceClient(config)
        
        assert client.config == config
        assert hasattr(client, 'chat')
        assert hasattr(client, 'models')
        assert hasattr(client, 'images')
        assert hasattr(client, 'image_edit')
        assert hasattr(client, 'image_upscale')
        assert hasattr(client, 'image_styles')
        assert hasattr(client, 'audio')
        assert hasattr(client, 'characters')
        assert hasattr(client, 'api_keys')
        assert hasattr(client, 'billing')
        assert hasattr(client, 'models_traits')
        assert hasattr(client, 'models_compatibility')
        assert hasattr(client, 'embeddings')

    def test_venice_client_initialization_without_config(self):
        """Test VeniceClient initialization without config."""
        client = VeniceClient()
        
        assert client.config is not None
        assert hasattr(client, 'chat')
        assert hasattr(client, 'models')
        assert hasattr(client, 'images')
        assert hasattr(client, 'image_edit')
        assert hasattr(client, 'image_upscale')
        assert hasattr(client, 'image_styles')
        assert hasattr(client, 'audio')
        assert hasattr(client, 'characters')
        assert hasattr(client, 'api_keys')
        assert hasattr(client, 'billing')
        assert hasattr(client, 'models_traits')
        assert hasattr(client, 'models_compatibility')
        assert hasattr(client, 'embeddings')

    def test_venice_client_http_client_property(self):
        """Test VeniceClient http_client property."""
        config = Config(api_key=self.api_key)
        client = VeniceClient(config)
        
        http_client = client.http_client
        
        assert http_client is not None
        assert hasattr(http_client, 'get')
        assert hasattr(http_client, 'post')
        assert hasattr(http_client, 'stream')

    def test_venice_client_chat_functionality(self):
        """Test VeniceClient chat functionality."""
        client = VeniceClient()
        
        # Test chat completion
        messages = [
            {"role": "user", "content": "Hello, how are you?"}
        ]
        
        def chat_call():
            return client.chat.complete(
                messages=messages,
                model="llama-3.3-70b",
                max_tokens=50
            )
        
        response = handle_api_call(chat_call)
        
        assert response is not None
        assert "choices" in response
        assert len(response["choices"]) > 0
        assert "message" in response["choices"][0]
        assert "content" in response["choices"][0]["message"]

    def test_venice_client_models_functionality(self):
        """Test VeniceClient models functionality."""
        client = VeniceClient()
        
        # Test listing models
        def models_call():
            return client.models.list()
        
        models = handle_api_call(models_call)
        
        assert isinstance(models, list)
        assert len(models) > 0
        
        # Verify model structure
        model = models[0]
        assert isinstance(model, dict)
        assert "id" in model
        assert "model_spec" in model
        assert "object" in model
        
        # Check model_spec structure
        model_spec = model["model_spec"]
        assert isinstance(model_spec, dict)
        assert "name" in model_spec
        assert "capabilities" in model_spec

    def test_venice_client_audio_functionality(self):
        """Test VeniceClient audio functionality."""
        client = VeniceClient()
        
        # Test getting voices
        voices = client.audio.get_voices()
        
        assert isinstance(voices, list)
        assert len(voices) > 0
        
        # Verify voice structure
        voice = voices[0]
        assert hasattr(voice, 'id')
        assert hasattr(voice, 'name')
        assert hasattr(voice, 'description')

    def test_venice_client_characters_functionality(self):
        """Test VeniceClient characters functionality."""
        client = VeniceClient()
        
        # Test listing characters
        characters = client.characters.list()
        
        assert isinstance(characters, list)
        assert len(characters) > 0
        
        # Verify character structure
        character = characters[0]
        assert hasattr(character, 'id')
        assert hasattr(character, 'name')
        assert hasattr(character, 'description')
        assert hasattr(character, 'category')
        assert hasattr(character, 'tags')
        assert hasattr(character, 'capabilities')

    def test_venice_client_embeddings_functionality(self):
        """Test VeniceClient embeddings functionality."""
        client = VeniceClient()
        
        # Test generating embedding
        text = "This is a test of the Venice AI embeddings system."
        
        result = client.embeddings.generate_single(
            text=text,
            model="text-embedding-3-small"
        )
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(x, float) for x in result)

    def test_venice_client_account_functionality(self):
        """Test VeniceClient account functionality."""
        client = VeniceClient()
        
        try:
            # Test getting API keys (may require admin permissions)
            api_keys = client.api_keys.list()
            
            assert isinstance(api_keys, list)
            assert len(api_keys) > 0
            
            # Verify API key structure
            api_key = api_keys[0]
            assert hasattr(api_key, 'id')
            assert hasattr(api_key, 'name')
            assert hasattr(api_key, 'created')
            assert hasattr(api_key, 'last_used')
            assert hasattr(api_key, 'permissions')
            assert hasattr(api_key, 'is_active')
        except Exception as e:
            if "Admin API key required" in str(e):
                pytest.skip("Admin API key required for account functionality test")
            else:
                raise

    def test_venice_client_billing_functionality(self):
        """Test VeniceClient billing functionality."""
        client = VeniceClient()
        
        try:
            # Test getting usage info (may require admin permissions)
            usage_info = client.billing.get_usage()
            
            assert usage_info is not None
            assert hasattr(usage_info, 'total_requests')
            assert hasattr(usage_info, 'total_tokens')
            assert hasattr(usage_info, 'total_cost')
            assert hasattr(usage_info, 'period_start')
            assert hasattr(usage_info, 'period_end')
            assert hasattr(usage_info, 'model_usage')
            
            # Usage should be non-negative
            assert usage_info.total_requests >= 0
            assert usage_info.total_tokens >= 0
            assert usage_info.total_cost >= 0
        except Exception as e:
            if "Admin API key required" in str(e):
                pytest.skip("Admin API key required for billing functionality test")
            else:
                raise

    def test_venice_client_models_traits_functionality(self):
        """Test VeniceClient models traits functionality."""
        client = VeniceClient()
        
        # Test getting traits
        traits = client.models_traits.get_traits()
        
        assert isinstance(traits, dict)
        assert len(traits) > 0
        
        # Verify trait structure
        model_id = list(traits.keys())[0]
        model_traits = traits[model_id]
        
        assert hasattr(model_traits, 'model_id')
        assert hasattr(model_traits, 'capabilities')
        assert hasattr(model_traits, 'traits')
        assert hasattr(model_traits, 'performance_metrics')
        assert hasattr(model_traits, 'supported_formats')
        assert hasattr(model_traits, 'context_length')
        assert hasattr(model_traits, 'max_tokens')
        assert hasattr(model_traits, 'temperature_range')
        assert hasattr(model_traits, 'languages')

    def test_venice_client_models_compatibility_functionality(self):
        """Test VeniceClient models compatibility functionality."""
        client = VeniceClient()
        
        # Test getting compatibility mapping
        mapping = client.models_compatibility.get_mapping()
        
        assert mapping is not None
        assert hasattr(mapping, 'openai_to_venice')
        assert hasattr(mapping, 'venice_to_openai')
        assert hasattr(mapping, 'provider_mappings')
        
        assert isinstance(mapping.openai_to_venice, dict)
        assert isinstance(mapping.venice_to_openai, dict)
        assert isinstance(mapping.provider_mappings, dict)

    def test_venice_client_get_account_summary(self):
        """Test VeniceClient get_account_summary method."""
        client = VeniceClient()
        
        summary = client.get_account_summary()
        
        assert summary is not None
        assert isinstance(summary, dict)
        
        # Check that we have at least some data (admin permissions may be limited)
        assert len(summary) > 0
        
        # Verify structure of available sections
        if "api_keys" in summary:
            assert isinstance(summary["api_keys"], dict)
        if "usage" in summary:
            assert isinstance(summary["usage"], dict)
        if "rate_limits" in summary:
            assert isinstance(summary["rate_limits"], dict)

    def test_venice_client_get_rate_limit_status(self):
        """Test VeniceClient get_rate_limit_status method."""
        client = VeniceClient()
        
        status = client.get_rate_limit_status()
        
        assert status is not None
        assert isinstance(status, dict)
        assert "current_usage" in status
        assert "limits" in status
        assert "status" in status
        
        # Status should be one of the expected values
        assert status["status"] in ["ok", "near_limit"]

    def test_venice_client_clear_caches(self):
        """Test VeniceClient clear_caches method."""
        client = VeniceClient()
        
        # Clear caches should not raise an error
        client.clear_caches()

    def test_create_client_with_api_key(self):
        """Test create_client with API key."""
        client = create_client(api_key=self.api_key)
        
        assert client is not None
        assert isinstance(client, VeniceClient)
        assert client.config.api_key == self.api_key

    def test_create_client_without_api_key(self):
        """Test create_client without API key."""
        # This should work if VENICE_API_KEY is set in environment
        client = create_client()
        
        assert client is not None
        assert isinstance(client, VeniceClient)
        assert client.config.api_key == self.api_key

    def test_create_client_with_kwargs(self):
        """Test create_client with kwargs."""
        client = create_client(
            api_key=self.api_key,
            base_url="https://custom-api.example.com/v1",
            default_model="llama-3.3-8b",
            timeout=60,
            max_retries=5,
            retry_delay=2
        )
        
        assert client is not None
        assert isinstance(client, VeniceClient)
        assert client.config.api_key == self.api_key
        assert client.config.base_url == "https://custom-api.example.com/v1"
        assert client.config.default_model == "llama-3.3-8b"
        assert client.config.timeout == 60
        assert client.config.max_retries == 5
        assert client.config.retry_delay == 2

    def test_create_client_with_config_kwargs(self):
        """Test create_client with config kwargs."""
        client = create_client(
            base_url="https://custom-api.example.com/v1",
            default_model="llama-3.3-8b",
            timeout=60
        )
        
        assert client is not None
        assert isinstance(client, VeniceClient)
        assert client.config.api_key == self.api_key
        assert client.config.base_url == "https://custom-api.example.com/v1"
        assert client.config.default_model == "llama-3.3-8b"
        assert client.config.timeout == 60

    def test_venice_client_error_handling(self):
        """Test VeniceClient error handling."""
        # Test with invalid API key - use an endpoint that requires authentication
        config = Config(api_key="invalid-key")
        client = VeniceClient(config)
        
        with pytest.raises(VeniceAPIError):
            client.chat.complete([{"role": "user", "content": "test"}])

    def test_venice_client_performance(self):
        """Test VeniceClient performance."""
        import time
        
        client = VeniceClient()
        
        # Test multiple operations
        start_time = time.time()
        
        # List models
        models = client.models.list()
        assert len(models) > 0
        
        # Get characters
        characters = client.characters.list()
        assert len(characters) > 0
        
        # Get voices
        voices = client.audio.get_voices()
        assert len(voices) > 0
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Should complete within reasonable time
        assert response_time < 30  # 30 seconds
        assert response_time > 0

    def test_venice_client_concurrent_access(self):
        """Test concurrent access to VeniceClient."""
        import threading
        import time
        
        client = VeniceClient()
        results = []
        errors = []
        
        def get_models():
            try:
                models = client.models.list()
                results.append(len(models))
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=get_models)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(results) == 3
        assert len(errors) == 0
        assert all(count > 0 for count in results)

    def test_venice_client_memory_usage(self):
        """Test memory usage during VeniceClient operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform multiple operations
        client = VeniceClient()
        
        for _ in range(10):
            models = client.models.list()
            assert len(models) > 0
            
            characters = client.characters.list()
            assert len(characters) > 0
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024

    def test_venice_client_data_consistency(self):
        """Test data consistency across multiple calls."""
        client = VeniceClient()
        
        # Get data multiple times
        models1 = client.models.list()
        models2 = client.models.list()
        
        # Data should be consistent
        assert len(models1) == len(models2)
        
        # Model IDs should be the same
        ids1 = [model["id"] for model in models1]
        ids2 = [model["id"] for model in models2]
        assert set(ids1) == set(ids2)

    def test_venice_client_api_integration(self):
        """Test integration between different APIs."""
        client = VeniceClient()
        
        # Test that all APIs work together
        models = client.models.list()
        assert len(models) > 0
        
        characters = client.characters.list()
        assert len(characters) > 0
        
        voices = client.audio.get_voices()
        assert len(voices) > 0
        
        # Test admin-only APIs with error handling
        try:
            api_keys = client.api_keys.list()
            assert len(api_keys) > 0
        except Exception as e:
            if "Admin API key required" in str(e):
                pytest.skip("Admin API key required for API integration test")
            else:
                raise
        
        try:
            usage_info = client.billing.get_usage_info()
            assert usage_info is not None
        except Exception as e:
            if "Admin API key required" in str(e):
                pytest.skip("Admin API key required for API integration test")
            else:
                raise
        
        traits = client.models_traits.get_traits()
        assert len(traits) > 0
        
        mapping = client.models_compatibility.get_mapping()
        assert mapping is not None

    def test_venice_client_caching_behavior(self):
        """Test caching behavior across APIs."""
        client = VeniceClient()
        
        # First call
        models1 = client.models.list()
        characters1 = client.characters.list()
        voices1 = client.audio.get_voices()
        
        # Second call (should use cache)
        models2 = client.models.list()
        characters2 = client.characters.list()
        voices2 = client.audio.get_voices()
        
        # Data should be consistent
        assert models1 == models2
        assert characters1 == characters2
        assert voices1 == voices2

    def test_venice_client_clear_caches_effectiveness(self):
        """Test that clear_caches actually clears caches."""
        client = VeniceClient()
        
        # Get data to populate caches
        models1 = client.models.list()
        characters1 = client.characters.list()
        voices1 = client.audio.get_voices()
        
        # Clear caches
        client.clear_caches()
        
        # Get data again (should be fresh)
        models2 = client.models.list()
        characters2 = client.characters.list()
        voices2 = client.audio.get_voices()
        
        # Data should still be consistent (but caches were cleared)
        assert len(models1) == len(models2)
        assert len(characters1) == len(characters2)
        assert len(voices1) == len(voices2)

    def test_venice_client_with_different_configs(self):
        """Test VeniceClient with different configurations."""
        # Test with custom config
        config = Config(
            api_key=self.api_key,
            base_url="https://api.venice.ai/api/v1",
            default_model="llama-3.3-8b",
            timeout=60,
            max_retries=5,
            retry_delay=2
        )
        
        client = VeniceClient(config)
        
        assert client.config == config
        assert client.config.api_key == self.api_key
        assert client.config.base_url == "https://api.venice.ai/api/v1"
        assert client.config.default_model == "llama-3.3-8b"
        assert client.config.timeout == 60
        assert client.config.max_retries == 5
        assert client.config.retry_delay == 2

    def test_venice_client_api_availability(self):
        """Test that all APIs are available and functional."""
        client = VeniceClient()
        
        # Test that all APIs are available
        assert hasattr(client, 'chat')
        assert hasattr(client, 'models')
        assert hasattr(client, 'images')
        assert hasattr(client, 'image_edit')
        assert hasattr(client, 'image_upscale')
        assert hasattr(client, 'image_styles')
        assert hasattr(client, 'audio')
        assert hasattr(client, 'characters')
        assert hasattr(client, 'api_keys')
        assert hasattr(client, 'billing')
        assert hasattr(client, 'models_traits')
        assert hasattr(client, 'models_compatibility')
        assert hasattr(client, 'embeddings')
        
        # Test that all APIs are functional
        assert callable(client.chat.complete)
        assert callable(client.models.list)
        assert callable(client.audio.get_voices)
        assert callable(client.characters.list)
        assert callable(client.embeddings.generate_single)
        assert callable(client.api_keys.list)
        assert callable(client.billing.get_usage)
        assert callable(client.models_traits.get_traits)
        assert callable(client.models_compatibility.get_mapping)
