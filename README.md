# Venice Python SDK

A Python SDK for interacting with the Venice API, providing a simple and intuitive interface for LLM chat completions and other features.

## Installation

```bash
pip install venice-sdk
```

## Quick Start

```python
from venice_sdk import VeniceClient, ChatAPI, get_models
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the client
client = VeniceClient()

# List available models
models = get_models(client)
for model in models:
    print(f"{model.name} ({model.id})")
    print(f"  Supports function calling: {model.capabilities.supports_function_calling}")
    print(f"  Supports web search: {model.capabilities.supports_web_search}")
    print(f"  Context tokens: {model.capabilities.available_context_tokens}")

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

## Features

- Simple and intuitive interface
- Support for chat completions
- Streaming responses
- Function calling support
- Web search integration
- Character personas
- Error handling
- Type hints and documentation

## Development

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Set up your environment variables in `.env`
4. Run tests:
   ```bash
   pytest
   ```

## License

MIT 