"""
Shared fixtures for all test modules.
"""

import os
from unittest.mock import MagicMock
import pytest
from venice_sdk.config import Config
from venice_sdk.client import HTTPClient


@pytest.fixture
def mock_config():
    """Create a mock configuration object."""
    config = MagicMock()
    config.base_url = "https://api.venice.is"
    config.api_key = "test-api-key"
    config.headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json"
    }
    config.timeout = 30
    config.max_retries = 3
    config.retry_delay = 1
    return config


@pytest.fixture
def mock_client(mock_config):
    """Create a mock HTTP client."""
    client = HTTPClient(config=mock_config)
    client.session = MagicMock()
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