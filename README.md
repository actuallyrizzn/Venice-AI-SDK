# Venice Python SDK

A Python SDK for interacting with the Venice API, providing a simple and intuitive interface for LLM chat completions and other features.

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
- 🔑 CLI-based credential management

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

## CLI Usage

The SDK includes a command-line interface for managing your API credentials:

```bash
# Set your API key
venice auth your-api-key-here

# Check authentication status
venice status
```

```python
# Get streaming response
for chunk in chat.complete(
    messages=[{"role": "user", "content": "Tell me a story"}],
    model="llama-3.3-70b",
    stream=True
):
    if chunk:
        print(chunk, end="", flush=True)
```

### Function Calling

```python
# Define tools
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

# Use tools in chat
response = chat.complete(
    messages=[{"role": "user", "content": "What's the weather in San Francisco?"}],
    model="llama-3.3-70b",
    tools=tools
)
```

### Error Handling

```python
from venice_sdk.errors import VeniceAPIError, RateLimitError

try:
    response = chat.complete(...)
except RateLimitError:
    print("Rate limit exceeded. Please try again later.")
except VeniceAPIError as e:
    print(f"API error: {e}")
```

## Configuration

The SDK can be configured in several ways:

1. Environment variables:
   ```bash
   export VENICE_API_KEY="your-api-key"
   export VENICE_BASE_URL="https://api.venice.ai/api/v1"
   ```

2. `.env` file:
   ```env
   VENICE_API_KEY=your-api-key
   VENICE_BASE_URL=https://api.venice.ai/api/v1
   ```

3. Direct initialization:
   ```python
   client = VeniceClient(
       api_key="your-api-key",
       base_url="https://api.venice.ai/api/v1"
   )
   ```

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

### Documentation

To build the documentation:

```bash
pip install -e ".[docs]"
mkdocs serve
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 