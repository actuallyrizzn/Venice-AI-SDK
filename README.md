# Venice AI Python SDK
http://venice.ai

A comprehensive Python SDK for the Venice AI API, providing complete access to all Venice AI services including chat completions, image generation, audio synthesis, character management, and more.

[![PyPI version](https://badge.fury.io/py/venice-sdk.svg)](https://badge.fury.io/py/venice-sdk)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: AGPLv3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![Tests](https://img.shields.io/badge/tests-350%2B%20passing-brightgreen.svg)](https://github.com/venice-ai/venice-sdk)

## ✨ Features

### 🤖 Core AI Services
- 💬 **Chat Completions** - Advanced LLM text generation with streaming
- 🧠 **Models** - Complete model management and discovery
- 🔗 **Embeddings** - Vector generation and semantic search
- 🎭 **Characters** - AI persona and character management

### 🎨 Image Processing
- 🖼️ **Image Generation** - Create images from text descriptions
- ✏️ **Image Editing** - Edit existing images with AI
- 🔍 **Image Upscaling** - Enhance image resolution and quality
- 🎨 **Image Styles** - Access to artistic style presets
- 📱 **Data URL Support** - Handle base64-encoded images seamlessly

### 🎵 Audio Services
- 🔊 **Text-to-Speech** - Convert text to natural-sounding speech
- 🎤 **Multiple Voices** - Choose from various voice options
- 📁 **Audio Formats** - Support for MP3, WAV, AAC, and more

### 🔧 Account Management
- 🔑 **API Key Management** - Create, list, and delete API keys
- 🌐 **Web3 Integration** - Generate Web3-compatible keys
- 📊 **Usage Tracking** - Monitor API usage and billing
- ⚡ **Rate Limiting** - Built-in rate limit management
- 👑 **Admin Features** - Full administrative access with admin API keys

### 🚀 Advanced Features
- 🌊 **Streaming** - Real-time response streaming with SSE support
- 🛠️ **Function Calling** - Tool and function integration
- 🔍 **Web Search** - Integrated web search capabilities
- 📈 **Model Analytics** - Advanced model traits and compatibility
- ⚡ **Error Handling** - Comprehensive error handling with retries
- 📝 **Type Safety** - Full type hints and documentation
- 🔄 **OpenAI Compatibility** - Drop-in replacement for OpenAI SDK
- ✅ **Robust Testing** - 350+ tests with 90%+ pass rate

## Installation

```bash
pip install venice-sdk
```

## Quick Start

```python
from venice_sdk import VeniceClient, create_client

# Initialize the client (loads from VENICE_API_KEY env var)
client = VeniceClient()

# Or create with explicit API key
# client = create_client(api_key="your-api-key")

# Chat completions
response = client.chat.complete(
    messages=[
        {"role": "user", "content": "Hello! What can you help me with?"}
    ],
    model="llama-3.3-70b"
)
print(response.choices[0].message.content)

# Image generation
image = client.images.generate(
    prompt="A serene mountain landscape at sunset",
    model="dall-e-3"
)
image.save("mountain.png")

# Text-to-speech
audio = client.audio.speech(
    input_text="Hello from Venice AI!",
    voice="alloy"
)
audio.save("hello.mp3")

# Generate embeddings
embeddings = client.embeddings.generate([
    "The quick brown fox jumps over the lazy dog",
    "A fast brown fox leaps over a sleepy dog"
])
similarity = embeddings[0].cosine_similarity(embeddings[1])
print(f"Similarity: {similarity}")

# List available characters
characters = client.characters.list()
for char in characters[:3]:
    print(f"- {char.name}: {char.description}")

# Check account usage
usage = client.billing.get_usage()
print(f"Credits remaining: {usage.credits_remaining}")
```

## 📚 Examples

### Image Processing
```python
# Generate an image
image = client.images.generate(
    prompt="A futuristic cityscape at night",
    model="dall-e-3",
    size="1024x1024",
    quality="hd"
)

# Edit an existing image
edited = client.image_edit.edit(
    image="path/to/image.png",
    prompt="Add a rainbow in the sky",
    model="dall-e-2-edit"
)

# Upscale an image
upscaled = client.image_upscale.upscale(
    image="path/to/small_image.png",
    scale=2
)

# List available styles
styles = client.image_styles.list_styles()
for style in styles:
    print(f"{style.name}: {style.description}")
```

### Audio Synthesis
```python
# Convert text to speech
audio = client.audio.speech(
    input_text="Hello, this is a test of the Venice AI text-to-speech system.",
    voice="alloy",
    response_format="mp3",
    speed=1.0
)

# Save to file
audio.save("speech.mp3")

# List available voices
voices = client.audio.get_voices()
for voice in voices:
    print(f"{voice.name}: {voice.description}")

# Batch processing
from venice_sdk import AudioBatchProcessor
processor = AudioBatchProcessor(client.audio)
texts = ["Hello", "World", "Venice AI"]
saved_files = processor.process_batch(texts, "output_dir/")
```

### Character Management
```python
# List all characters
characters = client.characters.list()

# Search for specific characters
assistants = client.characters.search("assistant")

# Get a specific character
venice_char = client.characters.get("venice")

# Use character in chat
response = client.chat.complete(
    messages=[{"role": "user", "content": "Tell me about yourself"}],
    model="llama-3.3-70b",
    venice_parameters={"character_slug": "venice"}
)
```

### Embeddings and Semantic Search
```python
# Generate embeddings
embeddings = client.embeddings.generate([
    "Machine learning is fascinating",
    "AI will change the world",
    "The weather is nice today"
])

# Calculate similarity
similarity = embeddings[0].cosine_similarity(embeddings[1])
print(f"Similarity: {similarity}")

# Semantic search
from venice_sdk import SemanticSearch
search = SemanticSearch(client.embeddings)
search.add_documents([
    "Python is a programming language",
    "Machine learning uses algorithms",
    "The sky is blue"
])

results = search.search("programming", top_k=2)
for result in results:
    print(f"{result['similarity']:.3f}: {result['document']}")
```

### Account Management
```python
# Get account usage
usage = client.billing.get_usage()
print(f"Total usage: {usage.total_usage}")
print(f"Credits remaining: {usage.credits_remaining}")

# Check rate limits
limits = client.api_keys.get_rate_limits()
print(f"Requests per minute: {limits.requests_per_minute}")

# Generate Web3 API key
web3_key = client.api_keys.generate_web3_key(
    name="Web3 Integration",
    description="For blockchain applications"
)
print(f"Web3 Key: {web3_key.api_key}")

# Get account summary
summary = client.get_account_summary()
print(f"Account Summary: {summary}")
```

### Admin API Key Management
```python
# List all API keys
api_keys = client.api_keys.list()
for key in api_keys:
    print(f"Key: {key.name} ({key.id})")
    print(f"  Type: {key.permissions.get('type', 'Unknown')}")
    print(f"  Created: {key.created_at}")

# Create a new API key
new_key = client.api_keys.create(
    name="My New Key",
    permissions=["read", "write"]
)
print(f"Created key: {new_key.id}")

# Get specific API key details
key_details = client.api_keys.get(new_key.id)
print(f"Key details: {key_details}")

# Delete an API key
success = client.api_keys.delete(new_key.id)
print(f"Key deleted: {success}")

# Get comprehensive billing information
billing_summary = client.billing.get_billing_summary()
print(f"Billing Summary: {billing_summary}")

# Get detailed usage by model
model_usage = client.billing.get_usage_by_model()
for model, usage in model_usage.items():
    print(f"{model}: {usage.requests} requests, {usage.tokens} tokens")
```

### Advanced Model Features
```python
# Get model traits
traits = client.models_traits.get_traits()
for model_id, model_traits in traits.items():
    print(f"{model_id}:")
    print(f"  Function calling: {model_traits.supports_function_calling()}")
    print(f"  Web search: {model_traits.supports_web_search()}")

# Get compatibility mapping
mapping = client.models_compatibility.get_mapping()
venice_model = mapping.get_venice_model("gpt-3.5-turbo")
print(f"OpenAI gpt-3.5-turbo maps to: {venice_model}")

# Find models by capability
function_models = client.models_traits.find_models_by_capability("function_calling")
print(f"Models with function calling: {function_models}")
```

## CLI Usage

The SDK includes a command-line interface for managing your API credentials:

```bash
# Set your API key
venice auth your-api-key-here

# Check authentication status
venice status
```

### Streaming Chat

```python
# Stream chat responses in real-time
for chunk in client.chat.complete_stream(
    messages=[{"role": "user", "content": "Tell me a story about a robot"}],
    model="llama-3.3-70b"
):
    print(chunk, end="", flush=True)

# Or use the streaming method directly
response = client.chat.complete(
    messages=[{"role": "user", "content": "Hello!"}],
    model="llama-3.3-70b",
    stream=True
)

for chunk in response:
    if chunk.get("choices") and chunk["choices"][0].get("delta", {}).get("content"):
        print(chunk["choices"][0]["delta"]["content"], end="", flush=True)
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
from venice_sdk.errors import VeniceAPIError, RateLimitError, UnauthorizedError

try:
    response = chat.complete(...)
except RateLimitError:
    print("Rate limit exceeded. Please try again later.")
except UnauthorizedError:
    print("Authentication failed. Please check your API key.")
except VeniceAPIError as e:
    print(f"API error: {e}")
```

## 🆕 What's New in v0.2.0

### Major Improvements
- **🔑 Admin API Key Management**: Full support for creating, listing, and deleting API keys
- **📊 Enhanced Billing**: Comprehensive usage tracking and rate limiting
- **🌊 Improved Streaming**: Better Server-Sent Events (SSE) support for real-time responses
- **🖼️ Image Enhancements**: Data URL support and improved file handling
- **✅ Robust Testing**: 350+ tests with 90%+ pass rate
- **🛡️ Better Error Handling**: More descriptive error messages and validation

### API Response Alignment
- Fixed all data structure mismatches with the actual Venice AI API
- Updated capability mapping to use correct API names
- Aligned all data classes with real API response formats

### Performance & Reliability
- Improved timeout handling and retry logic
- Enhanced test isolation to prevent interference
- Better environment variable management
- Comprehensive input validation

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
3. Set up your environment variables in `.env`:
   ```env
   VENICE_API_KEY=your-api-key-here
   ```
4. Run tests:
   ```bash
   # Run all tests
   pytest
   
   # Run only live tests (requires API key)
   pytest tests/live/
   
   # Run specific test categories
   pytest tests/unit/
   pytest tests/integration/
   pytest tests/e2e/
   ```

### Test Coverage

The SDK includes a comprehensive test suite with:
- **350+ tests** covering all functionality
- **90%+ pass rate** with robust error handling
- **Live API tests** for real-world validation
- **Unit tests** for isolated component testing
- **Integration tests** for cross-module functionality
- **E2E tests** for complete workflow validation

### Documentation

To build the documentation:

```bash
pip install -e ".[docs]"
mkdocs serve
```

## License

This project uses a dual license structure:

- **Code/Software**: GNU Affero General Public License v3.0 (AGPLv3) - Strong copyleft protection, requires source code availability for network services
- **Documentation/Examples**: Creative Commons Attribution-ShareAlike 4.0 International (CC-BY-SA) - Attribution required, derivative works must use same license

The Python SDK code is licensed under AGPLv3, while all documentation and examples are licensed under CC-BY-SA 4.0.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 
