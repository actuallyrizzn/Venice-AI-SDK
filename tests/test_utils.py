"""
Tests for the utils module.
"""

import pytest
from venice_sdk.utils import (
    count_tokens,
    validate_stop_sequences,
    format_messages,
    format_tools
)


def test_count_tokens():
    """Test token counting."""
    text = "Hello, how are you?"
    assert count_tokens(text) > 0

    # Test empty string
    assert count_tokens("") == 0

    # Test with special characters
    assert count_tokens("Hello, world! 😊") > 0


def test_validate_stop_sequences():
    """Test stop sequence validation."""
    # Test valid stop sequences
    assert validate_stop_sequences("\n") == ["\n"]
    assert validate_stop_sequences(["\n", "stop"]) == ["\n", "stop"]
    assert validate_stop_sequences(None) is None

    # Test invalid stop sequences
    with pytest.raises(ValueError):
        validate_stop_sequences(123)  # Not a string or list
    with pytest.raises(ValueError):
        validate_stop_sequences([123])  # List contains non-string


def test_format_messages():
    """Test message formatting."""
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]
    formatted = format_messages(messages)
    assert formatted == messages

    # Test invalid message format
    with pytest.raises(ValueError):
        format_messages([{"invalid": "format"}])
    with pytest.raises(ValueError):
        format_messages([{"role": "invalid", "content": "test"}])
    with pytest.raises(ValueError):
        format_messages([])


def test_format_tools():
    """Test tool formatting."""
    tools = [
        {
            "type": "function",
            "function": {
                "name": "test_tool",
                "description": "A test tool",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    ]
    formatted = format_tools(tools)
    assert formatted == tools

    # Test invalid tool format
    with pytest.raises(ValueError):
        format_tools([{"invalid": "format"}])
    with pytest.raises(ValueError):
        format_tools([{
            "type": "function",
            "function": {
                "name": "test_tool",
                "description": "A test tool",
                "parameters": "invalid"
            }
        }])
    with pytest.raises(ValueError):
        format_tools([]) 