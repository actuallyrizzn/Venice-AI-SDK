# Welcome to Venice Python SDK

A lightweight and extensible Python SDK for interacting with Venice's LLM endpoints.

## Features

- 🚀 Simple and intuitive interface
- 💬 Support for chat completions
- 🌊 Streaming responses
- 🛠️ Function calling support
- 🔍 Web search integration
- 🎭 Character personas
- ⚡ Error handling with retries
- 📝 Type hints and documentation
- 🔄 OpenAI API compatibility (optional)

## Quick Links

- [Installation](installation.md)
- [Quick Start](quickstart.md)
- [API Reference](api/client.md)
- [Advanced Usage](advanced/streaming.md)
- [Configuration](configuration.md)

## Getting Started

```python
from venice_sdk import HTTPClient, ChatAPI

# Initialize the client
client = HTTPClient()

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

print(response["choices"][0]["message"]["content"]) 
```

## Why Venice SDK?

The Venice Python SDK provides a simple and intuitive interface for interacting with Venice's LLM endpoints. It's designed to be:

- **Easy to use**: Simple API that follows Python best practices
- **Extensible**: Built with future endpoints in mind
- **Type-safe**: Full type hints and documentation
- **Reliable**: Built-in error handling and retries
- **Compatible**: Optional OpenAI API compatibility layer

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/yourusername/venice-sdk/blob/main/LICENSE) file for details. 