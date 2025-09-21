"""
Comprehensive unit tests for the config module.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from venice_sdk.config import Config, load_config


class TestConfigComprehensive:
    """Comprehensive test suite for Config class."""

    def test_config_initialization_with_all_parameters(self):
        """Test Config initialization with all parameters."""
        config = Config(
            api_key="test-key",
            base_url="https://custom.api.com",
            default_model="llama-3.3-70b",
            timeout=60,
            max_retries=5,
            retry_delay=2
        )
        
        assert config.api_key == "test-key"
        assert config.base_url == "https://custom.api.com"
        assert config.default_model == "llama-3.3-70b"
        assert config.timeout == 60
        assert config.max_retries == 5
        assert config.retry_delay == 2

    def test_config_initialization_with_minimal_parameters(self):
        """Test Config initialization with only required parameters."""
        config = Config(api_key="test-key")
        
        assert config.api_key == "test-key"
        assert config.base_url == "https://api.venice.ai/api/v1"
        assert config.default_model is None
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.retry_delay == 1

    def test_config_initialization_with_empty_api_key(self):
        """Test Config initialization with empty API key."""
        with pytest.raises(ValueError, match="API key must be provided"):
            Config(api_key="")

    def test_config_initialization_with_none_api_key(self):
        """Test Config initialization with None API key."""
        with pytest.raises(ValueError, match="API key must be provided"):
            Config(api_key=None)

    def test_config_initialization_with_whitespace_api_key(self):
        """Test Config initialization with whitespace-only API key."""
        with pytest.raises(ValueError, match="API key must be provided"):
            Config(api_key="   ")

    def test_config_headers_property(self):
        """Test the headers property."""
        config = Config(api_key="test-key-123")
        headers = config.headers
        
        assert headers == {
            "Authorization": "Bearer test-key-123",
            "Content-Type": "application/json"
        }

    def test_config_headers_with_special_characters(self):
        """Test headers with special characters in API key."""
        config = Config(api_key="test-key-with-special-chars!@#$%")
        headers = config.headers
        
        assert headers == {
            "Authorization": "Bearer test-key-with-special-chars!@#$%",
            "Content-Type": "application/json"
        }

    def test_config_headers_immutability(self):
        """Test that headers property returns a new dict each time."""
        config = Config(api_key="test-key")
        headers1 = config.headers
        headers2 = config.headers
        
        assert headers1 == headers2
        assert headers1 is not headers2  # Different objects

    def test_config_with_custom_base_url(self):
        """Test Config with custom base URL."""
        config = Config(api_key="test-key", base_url="https://custom.venice.ai")
        assert config.base_url == "https://custom.venice.ai"

    def test_config_with_none_base_url(self):
        """Test Config with None base URL uses default."""
        config = Config(api_key="test-key", base_url=None)
        assert config.base_url == "https://api.venice.ai/api/v1"

    def test_config_with_empty_base_url(self):
        """Test Config with empty base URL is preserved."""
        config = Config(api_key="test-key", base_url="")
        assert config.base_url == ""

    def test_config_with_custom_timeout(self):
        """Test Config with custom timeout."""
        config = Config(api_key="test-key", timeout=120)
        assert config.timeout == 120

    def test_config_with_zero_timeout(self):
        """Test Config with zero timeout."""
        config = Config(api_key="test-key", timeout=0)
        assert config.timeout == 0

    def test_config_with_negative_timeout(self):
        """Test Config with negative timeout."""
        config = Config(api_key="test-key", timeout=-1)
        assert config.timeout == -1

    def test_config_with_custom_max_retries(self):
        """Test Config with custom max retries."""
        config = Config(api_key="test-key", max_retries=10)
        assert config.max_retries == 10

    def test_config_with_zero_max_retries(self):
        """Test Config with zero max retries."""
        config = Config(api_key="test-key", max_retries=0)
        assert config.max_retries == 0

    def test_config_with_negative_max_retries(self):
        """Test Config with negative max retries."""
        config = Config(api_key="test-key", max_retries=-1)
        assert config.max_retries == -1

    def test_config_with_custom_retry_delay(self):
        """Test Config with custom retry delay."""
        config = Config(api_key="test-key", retry_delay=5)
        assert config.retry_delay == 5

    def test_config_with_zero_retry_delay(self):
        """Test Config with zero retry delay."""
        config = Config(api_key="test-key", retry_delay=0)
        assert config.retry_delay == 0

    def test_config_with_negative_retry_delay(self):
        """Test Config with negative retry delay."""
        config = Config(api_key="test-key", retry_delay=-1)
        assert config.retry_delay == -1

    def test_config_with_custom_default_model(self):
        """Test Config with custom default model."""
        config = Config(api_key="test-key", default_model="gpt-4")
        assert config.default_model == "gpt-4"

    def test_config_with_empty_default_model(self):
        """Test Config with empty default model."""
        config = Config(api_key="test-key", default_model="")
        assert config.default_model == ""

    def test_config_with_none_default_model(self):
        """Test Config with None default model."""
        config = Config(api_key="test-key", default_model=None)
        assert config.default_model is None

    def test_config_string_representation(self):
        """Test Config string representation."""
        config = Config(api_key="test-key")
        config_str = str(config)
        assert "Config" in config_str
        assert "test-key" not in config_str  # API key should not be in string representation

    def test_config_repr(self):
        """Test Config repr."""
        config = Config(api_key="test-key")
        config_repr = repr(config)
        assert "Config" in config_repr
        assert "test-key" not in config_repr  # API key should not be in repr


class TestLoadConfigComprehensive:
    """Comprehensive test suite for load_config function."""

    def test_load_config_with_provided_api_key(self):
        """Test load_config with provided API key."""
        with patch.dict(os.environ, {}, clear=True):
            config = load_config(api_key="provided-key")
            
            assert config.api_key == "provided-key"
            assert config.base_url == "https://api.venice.ai/api/v1"
            assert config.default_model is None
            assert config.timeout == 30
            assert config.max_retries == 3
            assert config.retry_delay == 1

    def test_load_config_from_environment(self):
        """Test load_config loading from environment variables."""
        env_vars = {
            "VENICE_API_KEY": "env-key",
            "VENICE_BASE_URL": "https://env.venice.ai",
            "VENICE_DEFAULT_MODEL": "env-model",
            "VENICE_TIMEOUT": "60",
            "VENICE_MAX_RETRIES": "5",
            "VENICE_RETRY_DELAY": "2"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('venice_sdk.config.load_dotenv'):
                config = load_config()
                
                assert config.api_key == "env-key"
                assert config.base_url == "https://env.venice.ai"
                assert config.default_model == "env-model"
                assert config.timeout == 60
                assert config.max_retries == 5
                assert config.retry_delay == 2

    def test_load_config_with_mixed_sources(self):
        """Test load_config with API key from parameter and other values from environment."""
        env_vars = {
            "VENICE_BASE_URL": "https://env.venice.ai",
            "VENICE_DEFAULT_MODEL": "env-model",
            "VENICE_TIMEOUT": "45",
            "VENICE_MAX_RETRIES": "7",
            "VENICE_RETRY_DELAY": "3"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('venice_sdk.config.load_dotenv'):
                config = load_config(api_key="param-key")
                
                assert config.api_key == "param-key"
                assert config.base_url == "https://env.venice.ai"
                assert config.default_model == "env-model"
                assert config.timeout == 45
                assert config.max_retries == 7
                assert config.retry_delay == 3

    def test_load_config_with_no_api_key(self):
        """Test load_config with no API key provided or in environment."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('venice_sdk.config.load_dotenv'):
                with pytest.raises(ValueError, match="API key must be provided"):
                    load_config()

    def test_load_config_with_empty_api_key_in_env(self):
        """Test load_config with empty API key in environment."""
        env_vars = {"VENICE_API_KEY": ""}
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('venice_sdk.config.load_dotenv'):
                with pytest.raises(ValueError, match="API key must be provided"):
                    load_config()

    def test_load_config_with_none_api_key_in_env(self):
        """Test load_config with None API key in environment."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('venice_sdk.config.load_dotenv'):
                with pytest.raises(ValueError, match="API key must be provided"):
                    load_config()

    def test_load_config_with_partial_environment_variables(self):
        """Test load_config with only some environment variables set."""
        env_vars = {
            "VENICE_API_KEY": "env-key",
            "VENICE_BASE_URL": "https://custom.venice.ai"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('venice_sdk.config.load_dotenv'):
                config = load_config()
                
                assert config.api_key == "env-key"
                assert config.base_url == "https://custom.venice.ai"
                assert config.default_model is None
                assert config.timeout == 30
                assert config.max_retries == 3
                assert config.retry_delay == 1

    def test_load_config_with_invalid_timeout_string(self):
        """Test load_config with invalid timeout string in environment."""
        env_vars = {
            "VENICE_API_KEY": "env-key",
            "VENICE_TIMEOUT": "invalid"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('venice_sdk.config.load_dotenv'):
                with pytest.raises(ValueError):
                    load_config()

    def test_load_config_with_invalid_max_retries_string(self):
        """Test load_config with invalid max_retries string in environment."""
        env_vars = {
            "VENICE_API_KEY": "env-key",
            "VENICE_MAX_RETRIES": "invalid"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('venice_sdk.config.load_dotenv'):
                with pytest.raises(ValueError):
                    load_config()

    def test_load_config_with_invalid_retry_delay_string(self):
        """Test load_config with invalid retry_delay string in environment."""
        env_vars = {
            "VENICE_API_KEY": "env-key",
            "VENICE_RETRY_DELAY": "invalid"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('venice_sdk.config.load_dotenv'):
                with pytest.raises(ValueError):
                    load_config()

    def test_load_config_calls_load_dotenv(self):
        """Test that load_config calls load_dotenv."""
        with patch('venice_sdk.config.load_dotenv') as mock_load_dotenv:
            with patch.dict(os.environ, {"VENICE_API_KEY": "test-key"}, clear=True):
                load_config()
                mock_load_dotenv.assert_called_once()

    def test_load_config_with_whitespace_values(self):
        """Test load_config with whitespace values in environment."""
        env_vars = {
            "VENICE_API_KEY": "  env-key  ",
            "VENICE_BASE_URL": "  https://env.venice.ai  ",
            "VENICE_DEFAULT_MODEL": "  env-model  "
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('venice_sdk.config.load_dotenv'):
                config = load_config()
                
                assert config.api_key == "  env-key  "  # Whitespace preserved
                assert config.base_url == "  https://env.venice.ai  "
                assert config.default_model == "  env-model  "

    def test_load_config_with_numeric_strings(self):
        """Test load_config with numeric values as strings."""
        env_vars = {
            "VENICE_API_KEY": "env-key",
            "VENICE_TIMEOUT": "120",
            "VENICE_MAX_RETRIES": "10",
            "VENICE_RETRY_DELAY": "5"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('venice_sdk.config.load_dotenv'):
                config = load_config()
                
                assert config.timeout == 120
                assert config.max_retries == 10
                assert config.retry_delay == 5

    def test_load_config_with_zero_values(self):
        """Test load_config with zero values in environment."""
        env_vars = {
            "VENICE_API_KEY": "env-key",
            "VENICE_TIMEOUT": "0",
            "VENICE_MAX_RETRIES": "0",
            "VENICE_RETRY_DELAY": "0"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('venice_sdk.config.load_dotenv'):
                config = load_config()
                
                assert config.timeout == 0
                assert config.max_retries == 0
                assert config.retry_delay == 0

    def test_load_config_with_negative_values(self):
        """Test load_config with negative values in environment."""
        env_vars = {
            "VENICE_API_KEY": "env-key",
            "VENICE_TIMEOUT": "-1",
            "VENICE_MAX_RETRIES": "-1",
            "VENICE_RETRY_DELAY": "-1"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('venice_sdk.config.load_dotenv'):
                config = load_config()
                
                assert config.timeout == -1
                assert config.max_retries == -1
                assert config.retry_delay == -1

    def test_load_config_parameter_overrides_environment(self):
        """Test that provided API key overrides environment API key."""
        env_vars = {"VENICE_API_KEY": "env-key"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('venice_sdk.config.load_dotenv'):
                config = load_config(api_key="param-key")
                assert config.api_key == "param-key"

    def test_load_config_with_dotenv_file(self):
        """Test load_config with .env file loading."""
        with patch('venice_sdk.config.load_dotenv') as mock_load_dotenv:
            with patch.dict(os.environ, {"VENICE_API_KEY": "test-key"}, clear=True):
                config = load_config()
                mock_load_dotenv.assert_called_once()
                assert config.api_key == "test-key"
