"""
Tests for the chat module.
"""

from unittest.mock import MagicMock, patch
import pytest
from venice_sdk.chat import ChatAPI, Message
from venice_sdk.client import HTTPClient
from venice_sdk.errors import VeniceAPIError


@pytest.fixture
def mock_client():
    """Create a mock HTTP client."""
    client = MagicMock(spec=HTTPClient)
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
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Hello, how can I help you?"
                }
            }
        ]
    }
    mock_client.post.return_value = mock_response

    messages = [{"role": "user", "content": "Hello"}]
    response = chat_api.complete(messages)

    assert response["choices"][0]["message"]["content"] == "Hello, how can I help you?"
    mock_client.post.assert_called_once_with(
        "chat/completions",
        data={
            "messages": messages,
            "model": "llama-3.3-70b",
            "temperature": 0.7,
            "stream": False
        }
    )


def test_complete_with_custom_params(chat_api, mock_client):
    """Test chat completion with custom parameters."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Custom response"
                }
            }
        ]
    }
    mock_client.post.return_value = mock_response

    messages = [{"role": "user", "content": "Hello"}]
    response = chat_api.complete(
        messages,
        model="llama-3.3-13b",
        temperature=0.5
    )

    assert response["choices"][0]["message"]["content"] == "Custom response"
    mock_client.post.assert_called_once_with(
        "chat/completions",
        data={
            "messages": messages,
            "model": "llama-3.3-13b",
            "temperature": 0.5,
            "stream": False
        }
    )


def test_complete_with_tools(chat_api, mock_client):
    """Test chat completion with tools."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Tool response",
                    "tool_calls": [
                        {
                            "id": "call_1",
                            "type": "function",
                            "function": {
                                "name": "get_weather",
                                "arguments": {"location": "London"}
                            }
                        }
                    ]
                }
            }
        ]
    }
    mock_client.post.return_value = mock_response

    messages = [{"role": "user", "content": "What's the weather?"}]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"}
                    }
                }
            }
        }
    ]

    response = chat_api.complete(messages, tools=tools)
    assert response["choices"][0]["message"]["tool_calls"][0]["function"]["name"] == "get_weather"
    mock_client.post.assert_called_once_with(
        "chat/completions",
        data={
            "messages": messages,
            "model": "llama-3.3-70b",
            "temperature": 0.7,
            "stream": False,
            "tools": tools
        }
    )


def test_complete_streaming(chat_api, mock_client):
    """Test streaming chat completion."""
    mock_client.stream.return_value = [
        {"choices": [{"delta": {"content": "Hello"}}]},
        {"choices": [{"delta": {"content": " there"}}]}
    ]

    messages = [{"role": "user", "content": "Hi"}]
    chunks = list(chat_api.complete(messages, stream=True))

    assert chunks == ["Hello", " there"]
    mock_client.stream.assert_called_once_with(
        "chat/completions",
        data={
            "messages": messages,
            "model": "llama-3.3-70b",
            "temperature": 0.7,
            "stream": True
        }
    )


def test_complete_invalid_messages(chat_api):
    """Test chat completion with invalid messages."""
    with pytest.raises(ValueError, match="Messages must be a non-empty list"):
        chat_api.complete([])


def test_complete_invalid_temperature(chat_api):
    """Test chat completion with invalid temperature."""
    messages = [{"role": "user", "content": "Hello"}]
    with pytest.raises(ValueError, match="Temperature must be between 0 and 1"):
        chat_api.complete(messages, temperature=1.5)


def test_complete_api_error(chat_api, mock_client):
    """Test chat completion with API error."""
    mock_client.post.side_effect = VeniceAPIError("API error occurred")

    messages = [{"role": "user", "content": "Hello"}]
    with pytest.raises(VeniceAPIError) as exc_info:
        chat_api.complete(messages)
    assert "API error occurred" in str(exc_info.value) 