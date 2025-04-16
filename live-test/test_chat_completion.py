"""
Live test for chat completion functionality.
This test demonstrates the core chat completion features of the Venice SDK.
"""

from venice_sdk.chat import ChatAPI
from venice_sdk.client import HTTPClient
from venice_sdk.config import load_config
import json
import time


def test_basic_chat():
    """Test basic chat completion."""
    config = load_config()
    client = HTTPClient(config)
    chat = ChatAPI(client)
    
    print("\nBasic Chat Completion Test:")
    messages = [
        {"role": "user", "content": "How are you doing today?"}
    ]
    
    response = chat.complete(
        messages=messages,
        model="llama-3.2-3b",  # Using the fastest model for testing
        temperature=0.7
    )
    
    print(f"Response: {response['content']}\n")


def test_streaming_chat():
    """Test streaming chat completion."""
    config = load_config()
    client = HTTPClient(config)
    chat = ChatAPI(client)
    
    print("\nStreaming Chat Completion Test:")
    messages = [
        {"role": "user", "content": "Count from 1 to 5 slowly."}
    ]
    
    print("Response chunks:")
    for chunk in chat.complete(
        messages=messages,
        model="llama-3.2-3b",
        stream=True,
        temperature=0.7
    ):
        if chunk and chunk.get('content'):
            print(chunk['content'], end='', flush=True)
    print("\n")


def test_chat_with_tools():
    """Test chat completion with tool calling."""
    config = load_config()
    client = HTTPClient(config)
    chat = ChatAPI(client)
    
    print("\nChat with Tools Test:")
    messages = [
        {"role": "user", "content": "What's the weather like in San Francisco?"}
    ]
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather in a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]
    
    response = chat.complete(
        messages=messages,
        model="llama-3.3-70b",  # Using a model that supports function calling
        tools=tools,
        temperature=0.7
    )
    
    print(f"Response: {response}\n")


def test_chat_with_system():
    """Test chat completion with system message."""
    config = load_config()
    client = HTTPClient(config)
    chat = ChatAPI(client)
    
    print("\nChat with System Message Test:")
    messages = [
        {"role": "system", "content": "You are a helpful assistant that always responds in rhyme."},
        {"role": "user", "content": "Tell me about Python programming."}
    ]
    
    response = chat.complete(
        messages=messages,
        model="llama-3.2-3b",
        temperature=0.7
    )
    
    print(f"Response: {response['content']}\n")


def test_chat_with_stop():
    """Test chat completion with stop sequence."""
    config = load_config()
    client = HTTPClient(config)
    chat = ChatAPI(client)
    
    print("\nChat with Stop Sequence Test:")
    messages = [
        {"role": "user", "content": "Write a story about a dog named Max"}
    ]
    
    response = chat.complete(
        messages=messages,
        model="llama-3.2-3b",
        temperature=0.7,
        stop=["The End"],
        max_tokens=100
    )
    
    print(f"Response: {response['content']}\n")


if __name__ == "__main__":
    print("Running live chat completion tests...")
    test_basic_chat()
    test_streaming_chat()
    test_chat_with_tools()
    test_chat_with_system()
    test_chat_with_stop() 