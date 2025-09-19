# Venice AI Python SDK
http://venice.ai

A comprehensive Python SDK for the Venice AI API, providing complete access to all Venice AI services including chat completions, image generation, audio synthesis, character management, and more.

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

### 🎵 Audio Services
- 🔊 **Text-to-Speech** - Convert text to natural-sounding speech
- 🎤 **Multiple Voices** - Choose from various voice options
- 📁 **Audio Formats** - Support for MP3, WAV, AAC, and more

### 🔧 Account Management
- 🔑 **API Key Management** - Create and manage API keys
- 🌐 **Web3 Integration** - Generate Web3-compatible keys
- 📊 **Usage Tracking** - Monitor API usage and billing
- ⚡ **Rate Limiting** - Built-in rate limit management

### 🚀 Advanced Features
- 🌊 **Streaming** - Real-time response streaming
- 🛠️ **Function Calling** - Tool and function integration
- 🔍 **Web Search** - Integrated web search capabilities
- 📈 **Model Analytics** - Advanced model traits and compatibility
- ⚡ **Error Handling** - Comprehensive error handling with retries
- 📝 **Type Safety** - Full type hints and documentation
- 🔄 **OpenAI Compatibility** - Drop-in replacement for OpenAI SDK

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

CC-BY-SA

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 
