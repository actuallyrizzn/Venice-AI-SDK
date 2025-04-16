"""
Shared fixtures for all test modules.
"""

import os
from unittest.mock import MagicMock
import pytest
from venice_sdk.config import Config
from venice_sdk.client import VeniceClient


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = MagicMock(spec=Config)
    config.api_key = "test_key"
    config.base_url = "https://api.venice.ai/api/v1"
    config.headers = {
        "Authorization": "Bearer test_key",
        "Content-Type": "application/json"
    }
    return config


@pytest.fixture
def mock_client(mock_config):
    """Create a mock HTTP client."""
    client = MagicMock(spec=VeniceClient)
    client.config = mock_config
    return client


@pytest.fixture
def env_vars():
    """Fixture to manage environment variables."""
    original_env = dict(os.environ)
    
    def set_env(**kwargs):
        for key, value in kwargs.items():
            os.environ[key] = value
    
    yield set_env
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env) 