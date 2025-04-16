"""
Live test for error handling and retry functionality.
This test demonstrates how the SDK handles various error conditions.
"""

import pytest
from venice_sdk.chat import ChatAPI
from venice_sdk.client import HTTPClient
from venice_sdk.config import Config, load_config
from venice_sdk.errors import VeniceAPIError, VeniceConnectionError


def test_invalid_api_key():
    """Test handling of invalid API key."""
    print("\nTesting invalid API key handling...")
    
    # Create config with invalid API key
    config = Config(api_key="invalid-key")
    client = HTTPClient(config)
    chat_api = ChatAPI(client)
    
    messages = [{"role": "user", "content": "Hello"}]
    
    with pytest.raises(VeniceAPIError) as exc_info:
        chat_api.complete(messages=messages)
    
    print(f"Expected error received: {exc_info.value}")
    assert "unauthorized" in str(exc_info.value).lower()


def test_invalid_model():
    """Test handling of invalid model name."""
    print("\nTesting invalid model handling...")
    
    config = load_config()
    client = HTTPClient(config)
    chat_api = ChatAPI(client)
    
    messages = [{"role": "user", "content": "Hello"}]
    
    with pytest.raises(VeniceAPIError) as exc_info:
        chat_api.complete(
            messages=messages,
            model="non-existent-model"
        )
    
    print(f"Expected error received: {exc_info.value}")
    assert "model" in str(exc_info.value).lower()


def test_invalid_messages():
    """Test handling of invalid message format."""
    print("\nTesting invalid message format handling...")
    
    config = load_config()
    client = HTTPClient(config)
    chat_api = ChatAPI(client)
    
    # Test empty messages
    with pytest.raises(ValueError) as exc_info:
        chat_api.complete(messages=[])
    
    print(f"Expected error received: {exc_info.value}")
    assert "empty" in str(exc_info.value).lower()
    
    # Test invalid message format
    with pytest.raises(ValueError) as exc_info:
        chat_api.complete(messages=[{"invalid": "format"}])
    
    print(f"Expected error received: {exc_info.value}")
    assert "role" in str(exc_info.value).lower()


def test_connection_retry():
    """Test connection retry handling."""
    print("\nTesting connection retry handling...")
    
    # Create config with invalid base URL to simulate connection issues
    config = Config(
        api_key=load_config().api_key,
        base_url="https://invalid-url.venice.ai/api/v1"
    )
    client = HTTPClient(config)
    chat_api = ChatAPI(client)
    
    messages = [{"role": "user", "content": "Hello"}]
    
    with pytest.raises(VeniceConnectionError) as exc_info:
        chat_api.complete(messages=messages)
    
    print(f"Expected error received: {exc_info.value}")
    assert "connection" in str(exc_info.value).lower()


if __name__ == "__main__":
    print("Running live error handling tests...")
    test_invalid_api_key()
    test_invalid_model()
    test_invalid_messages()
    test_connection_retry() 