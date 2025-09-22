"""
Comprehensive unit tests for the venice_client module.
"""

import pytest
from unittest.mock import patch, MagicMock
from venice_sdk.venice_client import VeniceClient, create_client
from venice_sdk.config import Config


class TestVeniceClientComprehensive:
    """Comprehensive test suite for VeniceClient class."""

    def test_venice_client_initialization_with_config(self, mock_config):
        """Test VeniceClient initialization with provided config."""
        client = VeniceClient(config=mock_config)
        
        assert client.config == mock_config
        assert client._http_client is not None
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
        """Test VeniceClient initialization without config (loads from environment)."""
        with patch('venice_sdk.venice_client.load_config') as mock_load_config:
            mock_config = MagicMock()
            mock_load_config.return_value = mock_config
            
            client = VeniceClient()
            
            assert client.config == mock_config
            mock_load_config.assert_called_once()

    def test_venice_client_http_client_property(self, mock_config):
        """Test VeniceClient http_client property."""
        client = VeniceClient(config=mock_config)
        http_client = client.http_client
        
        assert http_client == client._http_client

    def test_venice_client_get_account_summary(self, mock_config):
        """Test VeniceClient get_account_summary method."""
        with patch('venice_sdk.venice_client.HTTPClient') as mock_http_client_class:
            mock_http_client = MagicMock()
            mock_http_client_class.return_value = mock_http_client
            
            with patch('venice_sdk.venice_client.APIKeysAPI') as mock_api_keys_class:
                with patch('venice_sdk.venice_client.BillingAPI') as mock_billing_class:
                    mock_api_keys = MagicMock()
                    mock_billing = MagicMock()
                    mock_api_keys_class.return_value = mock_api_keys
                    mock_billing_class.return_value = mock_billing
                    
                    # Mock the API methods
                    mock_usage_info = MagicMock()
                    mock_usage_info.total_usage = 100
                    mock_usage_info.credits_remaining = 50
                    mock_usage_info.current_period = "2024-01"
                    mock_billing.get_usage.return_value = mock_usage_info
                    
                    mock_rate_limits = MagicMock()
                    mock_rate_limits.requests_per_minute = 60
                    mock_rate_limits.requests_per_day = 1000
                    mock_rate_limits.tokens_per_minute = 10000
                    mock_rate_limits.tokens_per_day = 100000
                    mock_api_keys.get_rate_limits.return_value = mock_rate_limits
                    
                    # Mock API keys to return some data
                    mock_api_key = MagicMock()
                    mock_api_key.is_active = True
                    mock_api_keys.list.return_value = [mock_api_key]

                    client = VeniceClient(config=mock_config)
                    result = client.get_account_summary()

                    # Check that the result has the expected structure
                    assert "usage" in result
                    assert "rate_limits" in result
                    assert "api_keys" in result
                    assert result["usage"]["total_usage"] == 100

    def test_venice_client_get_rate_limit_status(self, mock_config):
        """Test VeniceClient get_rate_limit_status method."""
        with patch('venice_sdk.venice_client.HTTPClient') as mock_http_client_class:
            mock_http_client = MagicMock()
            mock_http_client_class.return_value = mock_http_client
            
            with patch('venice_sdk.venice_client.APIKeysAPI') as mock_api_keys_class:
                with patch('venice_sdk.venice_client.BillingAPI') as mock_billing_class:
                    mock_api_keys = MagicMock()
                    mock_billing = MagicMock()
                    mock_api_keys_class.return_value = mock_api_keys
                    mock_billing_class.return_value = mock_billing
                    
                    # Mock the API methods
                    mock_rate_limits = MagicMock()
                    mock_rate_limits.requests_per_minute = 60
                    mock_rate_limits.requests_per_day = 1000
                    mock_rate_limits.tokens_per_minute = 10000
                    mock_rate_limits.tokens_per_day = 100000
                    mock_rate_limits.current_usage = {
                        "requests_per_minute": 10,
                        "requests_per_day": 100,
                        "tokens_per_minute": 1000,
                        "tokens_per_day": 10000
                    }
                    mock_rate_limits.reset_time = None
                    mock_api_keys.get_rate_limits.return_value = mock_rate_limits
                    
                    client = VeniceClient(config=mock_config)
                    result = client.get_rate_limit_status()
                    
                    # Check that the result has the expected structure
                    assert "limits" in result
                    assert "current_usage" in result
                    assert "reset_time" in result
                    assert "status" in result
                    assert result["limits"]["requests_per_minute"] == 60
                    assert result["current_usage"]["requests_per_minute"] == 10
                    assert result["status"] == "ok"

    def test_venice_client_clear_caches_with_all_caches(self, mock_config):
        """Test VeniceClient clear_caches method with all caches present."""
        client = VeniceClient(config=mock_config)
        
        # Mock the cache clearing methods
        client.models_traits.clear_cache = MagicMock()
        client.models_compatibility.clear_cache = MagicMock()
        client.characters.clear_cache = MagicMock()
        
        client.clear_caches()
        
        client.models_traits.clear_cache.assert_called_once()
        client.models_compatibility.clear_cache.assert_called_once()
        client.characters.clear_cache.assert_called_once()

    def test_venice_client_clear_caches_with_missing_caches(self, mock_config):
        """Test VeniceClient clear_caches method with some caches missing."""
        client = VeniceClient(config=mock_config)
        
        # Mock only some cache clearing methods
        client.models_traits.clear_cache = MagicMock()
        # Don't add clear_cache to models_compatibility and characters
        
        # Should not raise an error
        client.clear_caches()
        
        client.models_traits.clear_cache.assert_called_once()

    def test_venice_client_clear_caches_with_no_caches(self, mock_config):
        """Test VeniceClient clear_caches method with no caches present."""
        client = VeniceClient(config=mock_config)
        
        # Don't add clear_cache methods to any APIs
        # Should not raise an error
        client.clear_caches()

    def test_venice_client_api_attributes_are_initialized(self, mock_config):
        """Test that all API attributes are properly initialized."""
        client = VeniceClient(config=mock_config)
        
        # Check that all expected APIs are present and are the correct types
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

    def test_venice_client_http_client_reuse(self, mock_config):
        """Test that all APIs use the same HTTP client instance."""
        client = VeniceClient(config=mock_config)
        
        # All APIs should have the same HTTP client
        assert client.chat.client == client._http_client
        assert client.models.client == client._http_client
        assert client.images.client == client._http_client
        assert client.audio.client == client._http_client
        assert client.characters.client == client._http_client
        assert client.api_keys.client == client._http_client
        assert client.billing.client == client._http_client
        assert client.models_traits.client == client._http_client
        assert client.models_compatibility.client == client._http_client
        assert client.embeddings.client == client._http_client

    def test_venice_client_config_persistence(self, mock_config):
        """Test that config is properly stored and accessible."""
        client = VeniceClient(config=mock_config)
        
        assert client.config == mock_config
        assert client.config.api_key == mock_config.api_key
        assert client.config.base_url == mock_config.base_url

    def test_venice_client_string_representation(self, mock_config):
        """Test VeniceClient string representation."""
        client = VeniceClient(config=mock_config)
        client_str = str(client)
        
        assert "VeniceClient" in client_str

    def test_venice_client_repr(self, mock_config):
        """Test VeniceClient repr."""
        client = VeniceClient(config=mock_config)
        client_repr = repr(client)
        
        assert "VeniceClient" in client_repr


class TestCreateClientComprehensive:
    """Comprehensive test suite for create_client function."""

    def test_create_client_with_api_key(self):
        """Test create_client with provided API key."""
        with patch('venice_sdk.venice_client.Config') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            with patch('venice_sdk.venice_client.VeniceClient') as mock_client_class:
                mock_client = MagicMock()
                mock_client_class.return_value = mock_client
                
                result = create_client(api_key="test-key")
                
                mock_config_class.assert_called_once_with(api_key="test-key")
                mock_client_class.assert_called_once_with(mock_config)
                assert result == mock_client

    def test_create_client_with_api_key_and_kwargs(self):
        """Test create_client with API key and additional kwargs."""
        with patch('venice_sdk.venice_client.Config') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            with patch('venice_sdk.venice_client.VeniceClient') as mock_client_class:
                mock_client = MagicMock()
                mock_client_class.return_value = mock_client
                
                result = create_client(
                    api_key="test-key",
                    base_url="https://custom.api.com",
                    timeout=60
                )
                
                mock_config_class.assert_called_once_with(
                    api_key="test-key",
                    base_url="https://custom.api.com",
                    timeout=60
                )
                assert result == mock_client

    def test_create_client_without_api_key(self):
        """Test create_client without API key (loads from environment)."""
        with patch('venice_sdk.venice_client.load_config') as mock_load_config:
            mock_config = MagicMock()
            mock_load_config.return_value = mock_config
            
            with patch('venice_sdk.venice_client.VeniceClient') as mock_client_class:
                mock_client = MagicMock()
                mock_client_class.return_value = mock_client
                
                result = create_client()
                
                mock_load_config.assert_called_once()
                mock_client_class.assert_called_once_with(mock_config)
                assert result == mock_client

    def test_create_client_without_api_key_but_with_kwargs(self):
        """Test create_client without API key but with additional kwargs."""
        with patch('venice_sdk.venice_client.load_config') as mock_load_config:
            mock_config = MagicMock()
            mock_config.base_url = "https://api.venice.ai/api/v1"
            mock_config.timeout = 30
            mock_load_config.return_value = mock_config
            
            with patch('venice_sdk.venice_client.VeniceClient') as mock_client_class:
                mock_client = MagicMock()
                mock_client_class.return_value = mock_client
                
                result = create_client(
                    base_url="https://custom.api.com",
                    timeout=60
                )
                
                # Check that config was updated with kwargs
                assert mock_config.base_url == "https://custom.api.com"
                assert mock_config.timeout == 60
                mock_client_class.assert_called_once_with(mock_config)
                assert result == mock_client

    def test_create_client_with_invalid_kwargs(self):
        """Test create_client with invalid kwargs (not config attributes)."""
        with patch('venice_sdk.venice_client.load_config') as mock_load_config:
            mock_config = MagicMock()
            mock_config.base_url = "https://api.venice.ai/api/v1"
            mock_config.timeout = 30
            # Add hasattr method to mock
            mock_config.hasattr = MagicMock(return_value=False)
            mock_load_config.return_value = mock_config
            
            with patch('venice_sdk.venice_client.VeniceClient') as mock_client_class:
                mock_client = MagicMock()
                mock_client_class.return_value = mock_client
                
                result = create_client(
                    invalid_param="should_be_ignored",
                    timeout=60
                )
                
                # Only valid config attributes should be set
                assert mock_config.timeout == 60
                mock_client_class.assert_called_once_with(mock_config)
                assert result == mock_client

    def test_create_client_with_mixed_valid_invalid_kwargs(self):
        """Test create_client with mix of valid and invalid kwargs."""
        with patch('venice_sdk.venice_client.load_config') as mock_load_config:
            mock_config = MagicMock()
            mock_config.base_url = "https://api.venice.ai/api/v1"
            mock_config.timeout = 30
            mock_config.max_retries = 3
            mock_config.retry_delay = 1
            mock_config.default_model = None
            
            # Mock hasattr to return True for valid attributes
            def mock_hasattr(obj, name):
                valid_attrs = ['base_url', 'timeout', 'max_retries', 'retry_delay', 'default_model']
                return name in valid_attrs
            
            mock_config.hasattr = mock_hasattr
            mock_load_config.return_value = mock_config
            
            with patch('venice_sdk.venice_client.VeniceClient') as mock_client_class:
                mock_client = MagicMock()
                mock_client_class.return_value = mock_client
                
                result = create_client(
                    base_url="https://custom.api.com",
                    timeout=60,
                    max_retries=5,
                    invalid_param="should_be_ignored",
                    another_invalid="also_ignored"
                )
                
                # Only valid config attributes should be set
                assert mock_config.base_url == "https://custom.api.com"
                assert mock_config.timeout == 60
                assert mock_config.max_retries == 5
                mock_client_class.assert_called_once_with(mock_config)
                assert result == mock_client

    def test_create_client_with_none_values(self):
        """Test create_client with None values in kwargs."""
        with patch('venice_sdk.venice_client.load_config') as mock_load_config:
            mock_config = MagicMock()
            mock_config.base_url = "https://api.venice.ai/api/v1"
            mock_config.default_model = None
            
            def mock_hasattr(obj, name):
                return name in ['base_url', 'default_model']
            
            mock_config.hasattr = mock_hasattr
            mock_load_config.return_value = mock_config
            
            with patch('venice_sdk.venice_client.VeniceClient') as mock_client_class:
                mock_client = MagicMock()
                mock_client_class.return_value = mock_client
                
                result = create_client(
                    base_url=None,
                    default_model=None
                )
                
                assert mock_config.base_url is None
                assert mock_config.default_model is None
                mock_client_class.assert_called_once_with(mock_config)
                assert result == mock_client

    def test_create_client_with_empty_string_values(self):
        """Test create_client with empty string values in kwargs."""
        with patch('venice_sdk.venice_client.load_config') as mock_load_config:
            mock_config = MagicMock()
            mock_config.base_url = "https://api.venice.ai/api/v1"
            mock_config.default_model = None
            
            def mock_hasattr(obj, name):
                return name in ['base_url', 'default_model']
            
            mock_config.hasattr = mock_hasattr
            mock_load_config.return_value = mock_config
            
            with patch('venice_sdk.venice_client.VeniceClient') as mock_client_class:
                mock_client = MagicMock()
                mock_client_class.return_value = mock_client
                
                result = create_client(
                    base_url="",
                    default_model=""
                )
                
                assert mock_config.base_url == ""
                assert mock_config.default_model == ""
                mock_client_class.assert_called_once_with(mock_config)
                assert result == mock_client

    def test_create_client_with_boolean_values(self):
        """Test create_client with boolean values in kwargs."""
        with patch('venice_sdk.venice_client.load_config') as mock_load_config:
            mock_config = MagicMock()
            mock_config.timeout = 30
            mock_config.max_retries = 3
            
            def mock_hasattr(obj, name):
                return name in ['timeout', 'max_retries']
            
            mock_config.hasattr = mock_hasattr
            mock_load_config.return_value = mock_config
            
            with patch('venice_sdk.venice_client.VeniceClient') as mock_client_class:
                mock_client = MagicMock()
                mock_client_class.return_value = mock_client
                
                result = create_client(
                    timeout=120,
                    max_retries=10
                )
                
                assert mock_config.timeout == 120
                assert mock_config.max_retries == 10
                mock_client_class.assert_called_once_with(mock_config)
                assert result == mock_client

    def test_create_client_returns_venice_client_instance(self):
        """Test that create_client returns a VeniceClient instance."""
        with patch('venice_sdk.venice_client.Config') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            with patch('venice_sdk.venice_client.VeniceClient') as mock_client_class:
                mock_client = MagicMock()
                mock_client_class.return_value = mock_client
                
                result = create_client(api_key="test-key")
                
                assert result == mock_client
                assert isinstance(result, MagicMock)  # Since we're mocking VeniceClient
