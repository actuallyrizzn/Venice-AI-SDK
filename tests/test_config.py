"""
Tests for the configuration module.
"""

import os
from unittest.mock import patch, mock_open
import pytest
from venice_sdk.config import Config, load_config


def test_config_initialization():
    """Test basic Config initialization."""
    config = Config(api_key="test_key")
    assert config.api_key == "test_key"
    assert config.base_url == "https://api.venice.ai/api/v1"
    assert config.headers["Authorization"] == "Bearer test_key"
    assert config.headers["Content-Type"] == "application/json"


def test_config_custom_base_url():
    """Test Config with custom base URL."""
    config = Config(api_key="test_key", base_url="https://custom.venice.ai/api/v1")
    assert config.base_url == "https://custom.venice.ai/api/v1"


@patch.dict(os.environ, {"VENICE_API_KEY": "env_key"})
def test_load_config_from_env():
    """Test loading config from environment variables."""
    config = load_config()
    assert config.api_key == "env_key"
    assert config.headers["Authorization"] == "Bearer env_key"


@patch.dict(os.environ, {}, clear=True)
def test_load_config_no_env():
    """Test load_config when no environment variables are set."""
    with pytest.raises(ValueError, match="API key must be provided"):
        load_config()


@patch.dict(os.environ, {"VENICE_API_KEY": "env_key", "VENICE_BASE_URL": "https://custom.venice.ai/api/v1"})
def test_load_config_with_custom_base_url():
    """Test loading config with custom base URL from environment."""
    config = load_config()
    assert config.api_key == "env_key"
    assert config.base_url == "https://custom.venice.ai/api/v1"


@patch("builtins.open", new_callable=mock_open, read_data="VENICE_API_KEY=file_key\nVENICE_BASE_URL=https://file.venice.ai/api/v1")
def test_load_config_from_dotenv(mock_file):
    """Test loading config from .env file."""
    config = load_config()
    assert config.api_key == "file_key"
    assert config.base_url == "https://file.venice.ai/api/v1"
    mock_file.assert_called_once_with(".env", "r")


@patch("builtins.open", new_callable=mock_open, read_data="INVALID_KEY=value")
def test_load_config_invalid_dotenv(mock_file):
    """Test loading config from invalid .env file."""
    with pytest.raises(ValueError, match="API key must be provided"):
        load_config() 