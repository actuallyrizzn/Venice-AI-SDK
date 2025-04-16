# Quick Start Guide

This guide will help you get started with the Venice SDK quickly.

## Installation

```bash
pip install venice-sdk
```

## Authentication

Set up your API key using either environment variables or the CLI:

```bash
# Using environment variables
export VENICE_API_KEY=your-api-key

# Or using the CLI
venice auth your-api-key
```

## Basic Usage

Here's a simple example of using the SDK for chat completion:

```python
from venice_sdk import VeniceClient, ChatAPI

# Initialize the client
client = VeniceClient()

# Create a chat API instance
chat = ChatAPI(client)

# Send a message
response = chat.complete(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    model="llama-3.3-70b"
)

print(response.choices[0].message.content)
```

## Streaming Responses

For streaming responses:

```python
for chunk in chat.complete(
    messages=[{"role": "user", "content": "Tell me a story"}],
    model="llama-3.3-70b",
    stream=True
):
    if chunk:
        print(chunk, end="", flush=True)
```

## Function Calling

Using tools/function calling:

```python
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
    messages=[{"role": "user", "content": "What's the weather in San Francisco?"}],
    model="llama-3.3-70b",
    tools=tools
)

if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        print(f"Function: {tool_call.function.name}")
        print(f"Arguments: {tool_call.function.arguments}")
```

## Model Discovery

List available models:

```python
from venice_sdk import get_models

models = get_models(client)
for model in models:
    print(f"{model.name} ({model.id})")
    print(f"  Supports function calling: {model.capabilities.supports_function_calling}")
    print(f"  Supports web search: {model.capabilities.supports_web_search}")
    print(f"  Context tokens: {model.capabilities.available_context_tokens}")
```

## Error Handling

Handle errors gracefully:

```python
from venice_sdk.errors import VeniceAPIError, RateLimitError

try:
    response = chat.complete(...)
except RateLimitError:
    print("Rate limit exceeded. Please try again later.")
except VeniceAPIError as e:
    print(f"API error: {e}")
```

## Next Steps

- Check out the [API Reference](api/client.md) for detailed documentation
- See [Advanced Usage](advanced/streaming.md) for more features
- View [Examples](https://github.com/yourusername/venice-sdk/tree/main/examples) for more code samples 