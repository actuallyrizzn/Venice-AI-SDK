"""
Tests for the chat module.
"""

import json
from unittest.mock import patch, MagicMock
import pytest
from venice_sdk.chat import ChatAPI
from venice_sdk.errors import VeniceAPIError


@pytest.fixture
def mock_client():
    """Create a mock HTTP client."""
    client = MagicMock()
    return client


@pytest.fixture
def chat_api(mock_client):
    """Create a ChatAPI instance."""
    return ChatAPI(mock_client)


def test_chat_api_initialization(chat_api, mock_client):
    """Test ChatAPI initialization."""
    assert chat_api.client == mock_client


def test_complete_success(chat_api, mock_client):
    """Test successful chat completion."""
    mock_response = {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "Hello, how can I help you?"
            }
        }]
    }
    mock_client.post.return_value = mock_response

    messages = [{"role": "user", "content": "Hello"}]
    response = chat_api.complete(messages, model="test-model")

    assert response == mock_response
    mock_client.post.assert_called_once_with(
        "/chat/completions",
        {
            "messages": messages,
            "model": "test-model",
            "temperature": 0.15,
            "stream": False
        }
    )


def test_complete_with_custom_params(chat_api, mock_client):
    """Test chat completion with custom parameters."""
    mock_response = {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "Hello, how can I help you?"
            }
        }]
    }
    mock_client.post.return_value = mock_response

    messages = [{"role": "user", "content": "Hello"}]
    response = chat_api.complete(
        messages,
        model="test-model",
        temperature=0.7,
        max_tokens=100,
        stop=["\n"],
        venice_parameters={"test": "param"}
    )

    assert response == mock_response
    mock_client.post.assert_called_once_with(
        "/chat/completions",
        {
            "messages": messages,
            "model": "test-model",
            "temperature": 0.7,
            "max_tokens": 100,
            "stop": ["\n"],
            "venice_parameters": {"test": "param"},
            "stream": False
        }
    )


def test_complete_with_tools(chat_api, mock_client):
    """Test chat completion with tool definitions."""
    mock_response = {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "test_tool",
                        "arguments": "{}"
                    }
                }]
            }
        }]
    }
    mock_client.post.return_value = mock_response

    messages = [{"role": "user", "content": "Hello"}]
    tools = [{
        "type": "function",
        "function": {
            "name": "test_tool",
            "description": "A test tool",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }]
    response = chat_api.complete(messages, model="test-model", tools=tools)

    assert response == mock_response
    mock_client.post.assert_called_once_with(
        "/chat/completions",
        {
            "messages": messages,
            "model": "test-model",
            "temperature": 0.15,
            "tools": tools,
            "stream": False
        }
    )


def test_complete_streaming(chat_api, mock_client):
    """Test streaming chat completion."""
    mock_response = [
        b'data: {"choices": [{"delta": {"content": "Hello"}}]}\n\n',
        b'data: {"choices": [{"delta": {"content": " there"}}]}\n\n',
        b'data: [DONE]\n\n'
    ]
    mock_client.post.return_value = mock_response

    messages = [{"role": "user", "content": "Hello"}]
    response = chat_api.complete(messages, model="test-model", stream=True)

    # Convert generator to list for testing
    chunks = list(response)
    assert chunks == ["Hello", " there"]
    mock_client.post.assert_called_once_with(
        "/chat/completions",
        {
            "messages": messages,
            "model": "test-model",
            "temperature": 0.15,
            "stream": True
        }
    )


def test_complete_api_error(chat_api, mock_client):
    """Test chat completion with API error."""
    mock_client.post.side_effect = VeniceAPIError("API error occurred")

    messages = [{"role": "user", "content": "Hello"}]
    with pytest.raises(VeniceAPIError) as exc_info:
        chat_api.complete(messages, model="test-model")
    assert "API error occurred" in str(exc_info.value)


def test_complete_invalid_messages(chat_api):
    """Test chat completion with invalid messages."""
    with pytest.raises(ValueError) as exc_info:
        chat_api.complete([], model="test-model")
    assert "Messages list cannot be empty" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        chat_api.complete([{"role": "invalid", "content": "Hello"}], model="test-model")
    assert "Invalid message role" in str(exc_info.value)


def test_complete_invalid_temperature(chat_api):
    """Test chat completion with invalid temperature."""
    messages = [{"role": "user", "content": "Hello"}]
    with pytest.raises(ValueError) as exc_info:
        chat_api.complete(messages, model="test-model", temperature=2.0)
    assert "Temperature must be between 0 and 1" in str(exc_info.value) 