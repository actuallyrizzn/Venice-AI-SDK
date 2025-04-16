"""
Tests for the configuration module.
"""

import os
from unittest.mock import patch, mock_open
import pytest
from venice_sdk.config import Config, load_config


def test_config_initialization():
    """Test basic initialization of Config class."""
    config = Config(api_key="test_key")
    assert config.api_key == "test_key"
    assert config.base_url == "https://api.venice.ai/api/v1"
    assert config.timeout == 30
    assert config.max_retries == 3
    assert config.retry_delay == 1


def test_config_custom_base_url():
    """Test initialization with custom base URL."""
    config = Config(
        api_key="test_key",
        base_url="https://custom.venice.ai/api/v1"
    )
    assert config.api_key == "test_key"
    assert config.base_url == "https://custom.venice.ai/api/v1"


@patch.dict(os.environ, {"VENICE_API_KEY": "env_key"}, clear=True)
def test_load_config_from_env():
    """Test loading config from environment variables."""
    config = load_config()
    assert config.api_key == "env_key"
    assert config.base_url == "https://api.venice.ai/api/v1"


@patch.dict(os.environ, {}, clear=True)
def test_load_config_no_env():
    """Test load_config when no environment variables are set."""
    with pytest.raises(ValueError, match="API key must be provided"):
        load_config()


@patch.dict(os.environ, {
    "VENICE_API_KEY": "env_key",
    "VENICE_BASE_URL": "https://custom.venice.ai/api/v1"
}, clear=True)
def test_load_config_with_custom_base_url():
    """Test loading config with custom base URL from environment."""
    config = load_config()
    assert config.api_key == "env_key"
    assert config.base_url == "https://custom.venice.ai/api/v1"


@patch("builtins.open", new_callable=mock_open, read_data="VENICE_API_KEY=file_key\nVENICE_BASE_URL=https://file.venice.ai/api/v1")
@patch.dict(os.environ, {}, clear=True)
def test_load_config_from_dotenv(mock_file):
    """Test loading config from .env file."""
    config = load_config()
    assert config.api_key == "file_key"
    assert config.base_url == "https://file.venice.ai/api/v1"


@patch("builtins.open", new_callable=mock_open, read_data="INVALID_KEY=value")
@patch.dict(os.environ, {}, clear=True)
def test_load_config_invalid_dotenv(mock_file):
    """Test loading config from invalid .env file."""
    with pytest.raises(ValueError, match="API key must be provided"):
        load_config()


@patch.dict(os.environ, {
    "VENICE_API_KEY": "env_key",
    "VENICE_TIMEOUT": "60",
    "VENICE_MAX_RETRIES": "5",
    "VENICE_RETRY_DELAY": "2"
}, clear=True)
def test_load_config_with_custom_params():
    """Test loading config with custom parameters."""
    config = load_config()
    assert config.api_key == "env_key"
    assert config.timeout == 60
    assert config.max_retries == 5
    assert config.retry_delay == 2 