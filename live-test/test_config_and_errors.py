"""
Live test for configuration and error handling functionality.
This test demonstrates configuration loading and error handling in the Venice SDK.
"""

import os
from venice_sdk.config import Config, load_config
from venice_sdk.client import HTTPClient
from venice_sdk.chat import ChatAPI
from venice_sdk.errors import VeniceAPIError


def test_config_loading():
    """Test different ways of loading configuration."""
    print("\nConfiguration Loading Test:")
    
    # Test direct initialization
    config = Config(api_key="test_key", base_url="https://custom.api.venice.is")
    print(f"Direct config: API Key masked: {'*' * 8}, Base URL: {config.base_url}")
    
    # Test env var loading
    original_api_key = os.environ.get('VENICE_API_KEY')
    os.environ['VENICE_API_KEY'] = 'test_env_key'
    config = load_config()
    print(f"Env var config: API Key masked: {'*' * 8}")
    if original_api_key:
        os.environ['VENICE_API_KEY'] = original_api_key
    else:
        del os.environ['VENICE_API_KEY']


def test_error_handling():
    """Test error handling scenarios."""
    print("\nError Handling Test:")
    
    # Test invalid API key
    try:
        config = Config(api_key="invalid_key")
        client = HTTPClient(config)
        chat = ChatAPI(client)
        
        messages = [{"role": "user", "content": "Hello"}]
        chat.complete(messages=messages, model="llama-3.2-3b")
    except VeniceAPIError as e:
        print(f"Invalid API key error (expected): {e}")
    
    # Test invalid model ID
    config = load_config()  # Load valid config
    client = HTTPClient(config)
    chat = ChatAPI(client)
    
    try:
        messages = [{"role": "user", "content": "Hello"}]
        chat.complete(messages=messages, model="nonexistent-model")
    except VeniceAPIError as e:
        print(f"Invalid model error (expected): {e}")
    
    # Test retry logic
    config = Config(
        api_key=load_config().api_key,
        max_retries=3,
        retry_delay=1
    )
    client = HTTPClient(config)
    chat = ChatAPI(client)
    
    print("\nTesting retry logic (this may take a few seconds)...")
    try:
        messages = [{"role": "user", "content": "Hello"}]
        response = chat.complete(messages=messages, model="llama-3.2-3b")
        print("Request succeeded after potential retries")
    except VeniceAPIError as e:
        print(f"Request failed after retries: {e}")


if __name__ == "__main__":
    print("Running configuration and error handling tests...")
    test_config_loading()
    test_error_handling() 