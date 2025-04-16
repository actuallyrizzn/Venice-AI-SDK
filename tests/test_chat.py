"""
Tests for the chat module.
"""

import pytest
from unittest.mock import Mock, patch

from venice_sdk import VeniceClient, ChatAPI
from venice_sdk.chat import ChatCompletion, Choice, Message, Usage


@pytest.fixture
def mock_client():
    """Create a mock VeniceClient."""
    return Mock(spec=VeniceClient)


@pytest.fixture
def chat_api(mock_client):
    """Create a ChatAPI instance with a mock client."""
    return ChatAPI(mock_client)


def test_complete(chat_api, mock_client):
    """Test the complete method."""
    # Mock response data
    mock_response = Mock()
    mock_response.json.return_value = {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "llama-3.3-70b",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Hello!"
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
    mock_client.post.return_value = mock_response
    
    # Call the method
    response = chat_api.complete(
        messages=[
            {"role": "user", "content": "Hello"}
        ],
        model="llama-3.3-70b"
    )
    
    # Check the response
    assert isinstance(response, ChatCompletion)
    assert response.id == "chatcmpl-123"
    assert response.model == "llama-3.3-70b"
    assert len(response.choices) == 1
    assert response.choices[0].message.content == "Hello!"
    assert response.usage.total_tokens == 15
    
    # Check the request
    mock_client.post.assert_called_once_with(
        "chat/completions",
        data={
            "model": "llama-3.3-70b",
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": 0.15,
            "stream": False
        }
    )


def test_stream_complete(chat_api, mock_client):
    """Test streaming completions."""
    # Mock streaming response
    mock_client.stream.return_value = [
        {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": 1677652288,
            "model": "llama-3.3-70b",
            "choices": [
                {
                    "index": 0,
                    "delta": {
                        "content": "Hello"
                    }
                }
            ]
        },
        {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": 1677652288,
            "model": "llama-3.3-70b",
            "choices": [
                {
                    "index": 0,
                    "delta": {
                        "content": "!"
                    },
                    "finish_reason": "stop"
                }
            ]
        }
    ]
    
    # Call the method
    chunks = list(chat_api.complete(
        messages=[
            {"role": "user", "content": "Hello"}
        ],
        model="llama-3.3-70b",
        stream=True
    ))
    
    # Check the response
    assert len(chunks) == 2
    assert chunks[0].choices[0].message.content == "Hello"
    assert chunks[1].choices[0].message.content == "!"
    
    # Check the request
    mock_client.stream.assert_called_once_with(
        "chat/completions",
        data={
            "model": "llama-3.3-70b",
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": 0.15,
            "stream": True
        }
    ) 