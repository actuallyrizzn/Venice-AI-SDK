"""
Shared fixtures for all test modules.
"""

import os
import json
import tempfile
from unittest.mock import MagicMock, patch
from pathlib import Path
import socket
from urllib.parse import urlparse
from typing import Optional, Tuple
import pytest

# Ensure global config lookups are isolated from any real user config files.
# This must run before importing venice_sdk modules that cache config paths.
os.environ.setdefault("XDG_CONFIG_HOME", tempfile.mkdtemp(prefix="venice-tests-xdg-"))

from venice_sdk.config import Config, try_load_config
from venice_sdk.client import HTTPClient
from venice_sdk.models import Model, ModelCapabilities


def _is_truthy_env(value: Optional[str]) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


_LIVE_ENV_CHECK: Optional[Tuple[bool, str]] = None


def _live_environment_ok() -> Tuple[bool, str]:
    """
    Determine if live tests should run, with a stable reason when they shouldn't.
    """
    global _LIVE_ENV_CHECK
    if _LIVE_ENV_CHECK is not None:
        return _LIVE_ENV_CHECK

    if not _is_truthy_env(os.getenv("VENICE_LIVE_TESTS")):
        _LIVE_ENV_CHECK = (
            False,
            "Live tests are disabled by default. Set VENICE_LIVE_TESTS=1 to enable.",
        )
        return _LIVE_ENV_CHECK

    cfg = try_load_config()
    if cfg is None:
        _LIVE_ENV_CHECK = (
            False,
            "Live tests require VENICE_API_KEY (or a configured .env).",
        )
        return _LIVE_ENV_CHECK

    host = urlparse(cfg.base_url).hostname
    if not host:
        _LIVE_ENV_CHECK = (
            False,
            f"Live tests: could not parse host from base_url={cfg.base_url!r}",
        )
        return _LIVE_ENV_CHECK

    if host.endswith("example.com") or host == "api.example.com":
        _LIVE_ENV_CHECK = (
            False,
            f"Live tests: base_url host {host!r} looks like a placeholder; set VENICE_BASE_URL.",
        )
        return _LIVE_ENV_CHECK

    try:
        socket.getaddrinfo(host, None)
    except OSError as e:
        _LIVE_ENV_CHECK = (
            False,
            f"Live tests: base_url host {host!r} is not resolvable from this environment: {e}",
        )
        return _LIVE_ENV_CHECK

    _LIVE_ENV_CHECK = (True, "")
    return _LIVE_ENV_CHECK


def pytest_ignore_collect(path, config):  # type: ignore[no-untyped-def]
    # Avoid importing live test modules (and their extra deps) unless explicitly enabled.
    if "tests/live" in str(path):
        ok, _reason = _live_environment_ok()
        return not ok
    return False


def pytest_runtest_setup(item):  # type: ignore[no-untyped-def]
    if "live" in item.keywords:
        ok, reason = _live_environment_ok()
        if not ok:
            pytest.skip(reason)


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
    config.pool_connections = 10
    config.pool_maxsize = 20
    config.retry_backoff_factor = 0.5
    config.retry_status_codes = [429, 500, 502, 503, 504]
    return config


@pytest.fixture
def mock_client(mock_config):
    """Create a mock HTTP client."""
    client = MagicMock()
    client.config = mock_config
    client.get = MagicMock()
    client.post = MagicMock()
    client.stream = MagicMock()
    client._make_request = MagicMock()
    return client


@pytest.fixture
def client(mock_config):
    """Create a real HTTP client for integration tests."""
    return HTTPClient(config=mock_config)


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


@pytest.fixture
def mock_response():
    """Create a mock successful response."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"data": "test"}
    return response


@pytest.fixture
def mock_error_response():
    """Create a mock error response."""
    response = MagicMock()
    response.status_code = 404
    response.json.return_value = {"error": {"message": "Not found"}}
    return response


@pytest.fixture
def mock_models_response():
    """Create a mock models list response."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "data": [
            {
                "id": "llama-3.3-70b",
                "name": "Llama 3.3 70B",
                "type": "text",
                "model_spec": {
                    "capabilities": {
                        "supportsFunctionCalling": True,
                        "supportsWebSearch": True
                    },
                    "availableContextTokens": 4096
                },
                "description": "A powerful language model"
            }
        ]
    }
    return response


@pytest.fixture
def mock_model_response():
    """Create a mock single model response."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "id": "llama-3.3-70b",
        "name": "Llama 3.3 70B",
        "type": "text",
        "model_spec": {
            "capabilities": {
                "supportsFunctionCalling": True,
                "supportsWebSearch": True
            },
            "availableContextTokens": 4096
        },
        "description": "A powerful language model"
    }
    return response


@pytest.fixture
def mock_chat_response():
    """Create a mock chat completion response."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "llama-3.3-70b",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Hello! How can I help you today?"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15
        }
    }
    return response


@pytest.fixture
def mock_streaming_response():
    """Create a mock streaming response."""
    def stream_generator():
        chunks = [
            'data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"llama-3.3-70b","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}\n\n',
            'data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"llama-3.3-70b","choices":[{"index":0,"delta":{"content":" there"},"finish_reason":null}]}\n\n',
            'data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"llama-3.3-70b","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}\n\n',
            'data: [DONE]\n\n'
        ]
        for chunk in chunks:
            yield chunk.encode('utf-8')
    
    response = MagicMock()
    response.status_code = 200
    response.iter_lines.return_value = stream_generator()
    return response


@pytest.fixture
def sample_model():
    """Create a sample Model instance for testing."""
    capabilities = ModelCapabilities(
        supports_function_calling=True,
        supports_web_search=True,
        available_context_tokens=4096
    )
    return Model(
        id="test-model",
        name="Test Model",
        description="A test model",
        capabilities=capabilities
    )


@pytest.fixture
def sample_model_capabilities():
    """Create sample ModelCapabilities for testing."""
    return ModelCapabilities(
        supports_function_calling=True,
        supports_web_search=True,
        available_context_tokens=4096
    )


# API-specific fixtures
@pytest.fixture
def models_api(mock_client):
    """Create a ModelsAPI instance for testing."""
    from venice_sdk.models import ModelsAPI
    return ModelsAPI(mock_client)


@pytest.fixture
def chat_api(mock_client):
    """Create a ChatAPI instance for testing."""
    from venice_sdk.chat import ChatAPI
    return ChatAPI(mock_client)


@pytest.fixture
def characters_api(mock_client):
    """Create a CharactersAPI instance for testing."""
    from venice_sdk.characters import CharactersAPI
    return CharactersAPI(mock_client)


@pytest.fixture
def audio_api(mock_client):
    """Create an AudioAPI instance for testing."""
    from venice_sdk.audio import AudioAPI
    return AudioAPI(mock_client)


@pytest.fixture
def images_api(mock_client):
    """Create an ImagesAPI instance for testing."""
    from venice_sdk.images import ImagesAPI
    return ImagesAPI(mock_client)


@pytest.fixture
def embeddings_api(mock_client):
    """Create an EmbeddingsAPI instance for testing."""
    from venice_sdk.embeddings import EmbeddingsAPI
    return EmbeddingsAPI(mock_client)


@pytest.fixture
def video_api(mock_client):
    """Create a VideoAPI instance for testing."""
    from venice_sdk.video import VideoAPI
    return VideoAPI(mock_client)


@pytest.fixture
def account_api(mock_client):
    """Create an AccountAPI instance for testing."""
    from venice_sdk.account import AccountAPI
    return AccountAPI(mock_client)


# Test data fixtures
@pytest.fixture
def sample_messages():
    """Sample chat messages for testing."""
    return [
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you!"}
    ]


@pytest.fixture
def sample_tools():
    """Sample tools for function calling tests."""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]


@pytest.fixture
def sample_character():
    """Sample character data for testing."""
    return {
        "id": "test-character",
        "name": "Test Character",
        "slug": "test-character",
        "description": "A test character",
        "system_prompt": "You are a helpful test character.",
        "capabilities": {
            "supports_function_calling": True,
            "supports_web_search": True
        }
    }


@pytest.fixture
def sample_embedding():
    """Sample embedding data for testing."""
    return {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "index": 0,
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
            }
        ],
        "model": "text-embedding-ada-002",
        "usage": {
            "prompt_tokens": 10,
            "total_tokens": 10
        }
    }


@pytest.fixture
def sample_image_generation():
    """Sample image generation response for testing."""
    return {
        "created": 1677652288,
        "data": [
            {
                "url": "https://example.com/image1.png",
                "b64_json": None
            }
        ]
    }


@pytest.fixture
def sample_audio_response():
    """Sample audio response for testing."""
    return b"fake audio data"


# Utility fixtures for file operations
@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file for testing."""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("test content")
    return file_path


@pytest.fixture
def temp_image_file(tmp_path):
    """Create a temporary image file for testing."""
    file_path = tmp_path / "test_image.png"
    # Create a minimal PNG file
    file_path.write_bytes(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82')
    return file_path