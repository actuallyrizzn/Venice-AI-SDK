"""
Live tests for the Config module.

These tests verify configuration functionality with real environment variables.
"""

import pytest
import os
import tempfile
from pathlib import Path
from venice_sdk.config import Config, load_config
# ValueError is a built-in Python exception, not from venice_sdk.errors


@pytest.mark.live
class TestConfigLive:
    """Live tests for Config with real environment variables."""

    def test_config_initialization_with_api_key(self):
        """Test Config initialization with API key."""
        api_key = "test-api-key-123"
        config = Config(api_key=api_key)
        
        assert config.api_key == api_key
        assert config.base_url == "https://api.venice.ai/api/v1"
        assert config.default_model is None
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.retry_delay == 1

    def test_config_initialization_with_all_parameters(self):
        """Test Config initialization with all parameters."""
        api_key = "test-api-key-123"
        base_url = "https://custom-api.example.com/v1"
        default_model = "llama-3.3-8b"
        timeout = 60
        max_retries = 5
        retry_delay = 2
        
        config = Config(
            api_key=api_key,
            base_url=base_url,
            default_model=default_model,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay
        )
        
        assert config.api_key == api_key
        assert config.base_url == base_url
        assert config.default_model == default_model
        assert config.timeout == timeout
        assert config.max_retries == max_retries
        assert config.retry_delay == retry_delay

    def test_config_initialization_with_empty_api_key(self):
        """Test Config initialization with empty API key."""
        with pytest.raises(ValueError, match="API key must be provided"):
            Config(api_key="")

    def test_config_initialization_with_none_api_key(self):
        """Test Config initialization with None API key."""
        with pytest.raises(ValueError, match="API key must be provided"):
            Config(api_key=None)

    def test_config_headers_property(self):
        """Test Config headers property."""
        api_key = "test-api-key-123"
        config = Config(api_key=api_key)
        
        headers = config.headers
        
        assert isinstance(headers, dict)
        assert "Authorization" in headers
        assert "Content-Type" in headers
        assert headers["Authorization"] == f"Bearer {api_key}"
        assert headers["Content-Type"] == "application/json"

    def test_config_headers_with_different_api_keys(self):
        """Test Config headers with different API keys."""
        api_keys = ["key1", "key2", "key3"]
        
        for api_key in api_keys:
            config = Config(api_key=api_key)
            headers = config.headers
            
            assert headers["Authorization"] == f"Bearer {api_key}"

    def test_load_config_from_environment(self):
        """Test load_config from environment variables."""
        # Set environment variables
        original_api_key = os.environ.get("VENICE_API_KEY")
        original_base_url = os.environ.get("VENICE_BASE_URL")
        original_default_model = os.environ.get("VENICE_DEFAULT_MODEL")
        original_timeout = os.environ.get("VENICE_TIMEOUT")
        original_max_retries = os.environ.get("VENICE_MAX_RETRIES")
        original_retry_delay = os.environ.get("VENICE_RETRY_DELAY")
        
        try:
            # Set test environment variables
            os.environ["VENICE_API_KEY"] = "env-api-key-123"
            os.environ["VENICE_BASE_URL"] = "https://env-api.example.com/v1"
            os.environ["VENICE_DEFAULT_MODEL"] = "env-model"
            os.environ["VENICE_TIMEOUT"] = "45"
            os.environ["VENICE_MAX_RETRIES"] = "4"
            os.environ["VENICE_RETRY_DELAY"] = "3"
            
            config = load_config()
            
            assert config.api_key == "env-api-key-123"
            assert config.base_url == "https://env-api.example.com/v1"
            assert config.default_model == "env-model"
            assert config.timeout == 45
            assert config.max_retries == 4
            assert config.retry_delay == 3
            
        finally:
            # Restore original environment variables
            if original_api_key is not None:
                os.environ["VENICE_API_KEY"] = original_api_key
            elif "VENICE_API_KEY" in os.environ:
                del os.environ["VENICE_API_KEY"]
            
            if original_base_url is not None:
                os.environ["VENICE_BASE_URL"] = original_base_url
            elif "VENICE_BASE_URL" in os.environ:
                del os.environ["VENICE_BASE_URL"]
            
            if original_default_model is not None:
                os.environ["VENICE_DEFAULT_MODEL"] = original_default_model
            elif "VENICE_DEFAULT_MODEL" in os.environ:
                del os.environ["VENICE_DEFAULT_MODEL"]
            
            if original_timeout is not None:
                os.environ["VENICE_TIMEOUT"] = original_timeout
            elif "VENICE_TIMEOUT" in os.environ:
                del os.environ["VENICE_TIMEOUT"]
            
            if original_max_retries is not None:
                os.environ["VENICE_MAX_RETRIES"] = original_max_retries
            elif "VENICE_MAX_RETRIES" in os.environ:
                del os.environ["VENICE_MAX_RETRIES"]
            
            if original_retry_delay is not None:
                os.environ["VENICE_RETRY_DELAY"] = original_retry_delay
            elif "VENICE_RETRY_DELAY" in os.environ:
                del os.environ["VENICE_RETRY_DELAY"]

    def test_load_config_with_explicit_api_key(self):
        """Test load_config with explicit API key."""
        # Set environment variables
        original_api_key = os.environ.get("VENICE_API_KEY")
        
        try:
            # Set test environment variable
            os.environ["VENICE_API_KEY"] = "env-api-key-123"
            
            # Override with explicit API key
            config = load_config(api_key="explicit-api-key-456")
            
            assert config.api_key == "explicit-api-key-456"
            assert config.base_url == "https://api.venice.ai/api/v1"
            
        finally:
            # Restore original environment variable
            if original_api_key is not None:
                os.environ["VENICE_API_KEY"] = original_api_key
            elif "VENICE_API_KEY" in os.environ:
                del os.environ["VENICE_API_KEY"]

    def test_load_config_without_api_key(self):
        """Test load_config without API key."""
        # Set environment variables
        original_api_key = os.environ.get("VENICE_API_KEY")
        
        try:
            # Remove API key from environment
            if "VENICE_API_KEY" in os.environ:
                del os.environ["VENICE_API_KEY"]
            
            with pytest.raises(ValueError, match="API key must be provided"):
                load_config()
                
        finally:
            # Restore original environment variable
            if original_api_key is not None:
                os.environ["VENICE_API_KEY"] = original_api_key

    def test_load_config_from_env_file(self):
        """Test load_config from .env file."""
        # Create temporary .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("VENICE_API_KEY=env-file-api-key-789\n")
            f.write("VENICE_BASE_URL=https://env-file-api.example.com/v1\n")
            f.write("VENICE_DEFAULT_MODEL=env-file-model\n")
            f.write("VENICE_TIMEOUT=60\n")
            f.write("VENICE_MAX_RETRIES=5\n")
            f.write("VENICE_RETRY_DELAY=2\n")
            env_file_path = f.name
        
        try:
            # Change to directory containing .env file
            original_cwd = os.getcwd()
            env_dir = Path(env_file_path).parent
            os.chdir(env_dir)
            
            # Rename the file to .env so load_dotenv can find it
            env_file = Path(env_file_path)
            env_file.rename(env_dir / ".env")
            
            # Remove API key from environment
            original_api_key = os.environ.get("VENICE_API_KEY")
            if "VENICE_API_KEY" in os.environ:
                del os.environ["VENICE_API_KEY"]
            
            config = load_config()
            
            assert config.api_key == "env-file-api-key-789"
            assert config.base_url == "https://env-file-api.example.com/v1"
            assert config.default_model == "env-file-model"
            assert config.timeout == 60
            assert config.max_retries == 5
            assert config.retry_delay == 2
            
        finally:
            # Restore original working directory
            os.chdir(original_cwd)
            
            # Restore original environment variable
            if original_api_key is not None:
                os.environ["VENICE_API_KEY"] = original_api_key
            
            # Clean up .env file
            env_file_path = env_dir / ".env"
            if env_file_path.exists():
                os.unlink(env_file_path)

    def test_load_config_with_invalid_timeout(self):
        """Test load_config with invalid timeout value."""
        # Set environment variables
        original_api_key = os.environ.get("VENICE_API_KEY")
        original_timeout = os.environ.get("VENICE_TIMEOUT")
        
        try:
            # Set test environment variables
            os.environ["VENICE_API_KEY"] = "test-api-key"
            os.environ["VENICE_TIMEOUT"] = "invalid-timeout"
            
            # Should raise ValueError for invalid timeout
            with pytest.raises(ValueError):
                load_config()
                
        finally:
            # Restore original environment variables
            if original_api_key is not None:
                os.environ["VENICE_API_KEY"] = original_api_key
            elif "VENICE_API_KEY" in os.environ:
                del os.environ["VENICE_API_KEY"]
            
            if original_timeout is not None:
                os.environ["VENICE_TIMEOUT"] = original_timeout
            elif "VENICE_TIMEOUT" in os.environ:
                del os.environ["VENICE_TIMEOUT"]

    def test_load_config_with_invalid_max_retries(self):
        """Test load_config with invalid max_retries value."""
        # Set environment variables
        original_api_key = os.environ.get("VENICE_API_KEY")
        original_max_retries = os.environ.get("VENICE_MAX_RETRIES")
        
        try:
            # Set test environment variables
            os.environ["VENICE_API_KEY"] = "test-api-key"
            os.environ["VENICE_MAX_RETRIES"] = "invalid-retries"
            
            # Should raise ValueError for invalid max_retries
            with pytest.raises(ValueError):
                load_config()
                
        finally:
            # Restore original environment variables
            if original_api_key is not None:
                os.environ["VENICE_API_KEY"] = original_api_key
            elif "VENICE_API_KEY" in os.environ:
                del os.environ["VENICE_API_KEY"]
            
            if original_max_retries is not None:
                os.environ["VENICE_MAX_RETRIES"] = original_max_retries
            elif "VENICE_MAX_RETRIES" in os.environ:
                del os.environ["VENICE_MAX_RETRIES"]

    def test_load_config_with_invalid_retry_delay(self):
        """Test load_config with invalid retry_delay value."""
        # Set environment variables
        original_api_key = os.environ.get("VENICE_API_KEY")
        original_retry_delay = os.environ.get("VENICE_RETRY_DELAY")
        
        try:
            # Set test environment variables
            os.environ["VENICE_API_KEY"] = "test-api-key"
            os.environ["VENICE_RETRY_DELAY"] = "invalid-delay"
            
            # Should raise ValueError for invalid retry_delay
            with pytest.raises(ValueError):
                load_config()
                
        finally:
            # Restore original environment variables
            if original_api_key is not None:
                os.environ["VENICE_API_KEY"] = original_api_key
            elif "VENICE_API_KEY" in os.environ:
                del os.environ["VENICE_API_KEY"]
            
            if original_retry_delay is not None:
                os.environ["VENICE_RETRY_DELAY"] = original_retry_delay
            elif "VENICE_RETRY_DELAY" in os.environ:
                del os.environ["VENICE_RETRY_DELAY"]

    def test_config_with_none_values(self):
        """Test Config with None values for optional parameters."""
        api_key = "test-api-key-123"
        config = Config(
            api_key=api_key,
            base_url=None,
            default_model=None,
            timeout=None,
            max_retries=None,
            retry_delay=None
        )
        
        assert config.api_key == api_key
        assert config.base_url == "https://api.venice.ai/api/v1"  # Default value
        assert config.default_model is None
        assert config.timeout == 30  # Default value
        assert config.max_retries == 3  # Default value
        assert config.retry_delay == 1  # Default value

    def test_config_with_empty_string_values(self):
        """Test Config with empty string values for optional parameters."""
        api_key = "test-api-key-123"
        config = Config(
            api_key=api_key,
            base_url="",
            default_model="",
            timeout=None,
            max_retries=None,
            retry_delay=None
        )
        
        assert config.api_key == api_key
        assert config.base_url == ""  # Empty string should be preserved
        assert config.default_model == ""  # Empty string should be preserved
        assert config.timeout == 30  # Default value
        assert config.max_retries == 3  # Default value
        assert config.retry_delay == 1  # Default value

    def test_config_with_whitespace_values(self):
        """Test Config with whitespace values for optional parameters."""
        api_key = "test-api-key-123"
        config = Config(
            api_key=api_key,
            base_url="   ",
            default_model="   ",
            timeout=None,
            max_retries=None,
            retry_delay=None
        )
        
        assert config.api_key == api_key
        assert config.base_url == "   "  # Whitespace should be preserved
        assert config.default_model == "   "  # Whitespace should be preserved
        assert config.timeout == 30  # Default value
        assert config.max_retries == 3  # Default value
        assert config.retry_delay == 1  # Default value

    def test_config_with_very_long_api_key(self):
        """Test Config with very long API key."""
        api_key = "a" * 1000  # Very long API key
        config = Config(api_key=api_key)
        
        assert config.api_key == api_key
        assert config.headers["Authorization"] == f"Bearer {api_key}"

    def test_config_with_special_characters_in_api_key(self):
        """Test Config with special characters in API key."""
        api_key = "test-api-key-with-special-chars-@#$%^&*()_+-=[]{}|;':\",./<>?"
        config = Config(api_key=api_key)
        
        assert config.api_key == api_key
        assert config.headers["Authorization"] == f"Bearer {api_key}"

    def test_config_with_unicode_in_api_key(self):
        """Test Config with unicode characters in API key."""
        api_key = "test-api-key-with-unicode-🌟🎵🎤"
        config = Config(api_key=api_key)
        
        assert config.api_key == api_key
        assert config.headers["Authorization"] == f"Bearer {api_key}"

    def test_config_with_very_long_base_url(self):
        """Test Config with very long base URL."""
        api_key = "test-api-key-123"
        base_url = "https://" + "a" * 1000 + ".example.com/v1"
        config = Config(api_key=api_key, base_url=base_url)
        
        assert config.api_key == api_key
        assert config.base_url == base_url

    def test_config_with_very_long_default_model(self):
        """Test Config with very long default model."""
        api_key = "test-api-key-123"
        default_model = "a" * 1000
        config = Config(api_key=api_key, default_model=default_model)
        
        assert config.api_key == api_key
        assert config.default_model == default_model

    def test_config_with_very_large_timeout(self):
        """Test Config with very large timeout."""
        api_key = "test-api-key-123"
        timeout = 999999
        config = Config(api_key=api_key, timeout=timeout)
        
        assert config.api_key == api_key
        assert config.timeout == timeout

    def test_config_with_very_large_max_retries(self):
        """Test Config with very large max_retries."""
        api_key = "test-api-key-123"
        max_retries = 999999
        config = Config(api_key=api_key, max_retries=max_retries)
        
        assert config.api_key == api_key
        assert config.max_retries == max_retries

    def test_config_with_very_large_retry_delay(self):
        """Test Config with very large retry_delay."""
        api_key = "test-api-key-123"
        retry_delay = 999999
        config = Config(api_key=api_key, retry_delay=retry_delay)
        
        assert config.api_key == api_key
        assert config.retry_delay == retry_delay

    def test_config_with_zero_values(self):
        """Test Config with zero values."""
        api_key = "test-api-key-123"
        config = Config(
            api_key=api_key,
            timeout=0,
            max_retries=0,
            retry_delay=0
        )
        
        assert config.api_key == api_key
        assert config.timeout == 0
        assert config.max_retries == 0
        assert config.retry_delay == 0

    def test_config_with_negative_values(self):
        """Test Config with negative values."""
        api_key = "test-api-key-123"
        config = Config(
            api_key=api_key,
            timeout=-1,
            max_retries=-1,
            retry_delay=-1
        )
        
        assert config.api_key == api_key
        assert config.timeout == -1
        assert config.max_retries == -1
        assert config.retry_delay == -1

    def test_config_with_float_values(self):
        """Test Config with float values."""
        api_key = "test-api-key-123"
        config = Config(
            api_key=api_key,
            timeout=30.5,
            max_retries=3.7,
            retry_delay=1.2
        )
        
        assert config.api_key == api_key
        assert config.timeout == 30.5
        assert config.max_retries == 3.7
        assert config.retry_delay == 1.2

    def test_config_equality(self):
        """Test Config equality comparison."""
        config1 = Config(api_key="test-key", timeout=30)
        config2 = Config(api_key="test-key", timeout=30)
        config3 = Config(api_key="test-key", timeout=60)
        
        assert config1 == config2
        assert config1 != config3

    def test_config_string_representation(self):
        """Test Config string representation."""
        config = Config(api_key="test-key", timeout=30)
        config_str = str(config)
        
        assert "Config" in config_str
        assert "test-key" in config_str
        assert "30" in config_str

    def test_config_repr(self):
        """Test Config repr."""
        config = Config(api_key="test-key", timeout=30)
        config_repr = repr(config)
        
        assert "Config" in config_repr
        assert "test-key" in config_repr
        assert "30" in config_repr
