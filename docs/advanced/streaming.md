# Streaming Responses

The Venice SDK supports streaming responses for chat completions, allowing you to receive and process tokens as they are generated.

## Basic Streaming

```python
from venice_sdk import VeniceClient, ChatAPI

client = VeniceClient()
chat = ChatAPI(client)

# Get streaming response
for chunk in chat.complete(
    messages=[{"role": "user", "content": "Tell me a story"}],
    model="llama-3.3-70b",
    stream=True
):
    if chunk:
        print(chunk, end="", flush=True)
```

## Streaming with System Message

```python
for chunk in chat.complete(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a story"}
    ],
    model="llama-3.3-70b",
    stream=True
):
    if chunk:
        print(chunk, end="", flush=True)
```

## Streaming with Tools

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

for chunk in chat.complete(
    messages=[{"role": "user", "content": "What's the weather in San Francisco?"}],
    model="llama-3.3-70b",
    tools=tools,
    stream=True
):
    if chunk:
        print(chunk, end="", flush=True)
```

## Error Handling with Streaming

```python
from venice_sdk.errors import VeniceAPIError, RateLimitError

try:
    for chunk in chat.complete(
        messages=[{"role": "user", "content": "Tell me a story"}],
        model="llama-3.3-70b",
        stream=True
    ):
        if chunk:
            print(chunk, end="", flush=True)
except RateLimitError:
    print("\nRate limit exceeded. Please try again later.")
except VeniceAPIError as e:
    print(f"\nAPI error: {e}")
```

## Best Practices

1. **Flush Output**: Always use `flush=True` when printing chunks to ensure immediate display.
2. **Error Handling**: Wrap streaming code in try-except blocks to handle errors gracefully.
3. **Resource Management**: Consider using context managers for long-running streams.
4. **Buffer Management**: For large responses, consider implementing a buffer to manage memory usage.

## Example: Streaming with Context Manager

```python
class StreamingContext:
    def __init__(self, chat: ChatAPI, messages: List[Dict[str, str]], model: str):
        self.chat = chat
        self.messages = messages
        self.model = model

    def __enter__(self):
        return self.chat.complete(
            messages=self.messages,
            model=self.model,
            stream=True
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

# Usage
with StreamingContext(chat, messages, "llama-3.3-70b") as stream:
    for chunk in stream:
        if chunk:
            print(chunk, end="", flush=True)
```

## Related

- [Chat API](../api/chat.md) - Chat completion functionality
- [Error Handling](../advanced/error_handling.md) - Error handling best practices
- [Function Calling](../advanced/function_calling.md) - Using tools with streaming 