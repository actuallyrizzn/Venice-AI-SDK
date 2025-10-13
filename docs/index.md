# Venice AI Python SDK

A comprehensive Python SDK for the Venice AI API, providing complete access to all Venice AI services including chat completions, image generation, audio synthesis, character management, and more.

[![PyPI version](https://badge.fury.io/py/venice-sdk.svg)](https://badge.fury.io/py/venice-sdk)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: AGPLv3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![Tests](https://img.shields.io/badge/tests-1069%20passing-brightgreen.svg)](https://github.com/venice-ai/venice-sdk)

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

## 🚀 Quick Start

```python
from venice_sdk import VeniceClient

# Initialize the client (loads from VENICE_API_KEY env var)
client = VeniceClient()

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
```

## 📚 Documentation

### Getting Started
- [Installation Guide](installation.md) - Set up the SDK
- [Quick Start](quickstart.md) - Your first API call
- [Configuration](configuration.md) - Customize the SDK

### Core APIs
- [Chat API](api/chat.md) - Text generation and conversations
- [Models API](api/models.md) - Model discovery and management
- [Images API](api/images.md) - Image generation and editing
- [Audio API](api/audio.md) - Text-to-speech synthesis
- [Embeddings API](api/embeddings.md) - Vector embeddings
- [Characters API](api/characters.md) - AI character management

### Advanced Topics
- [Streaming](advanced/streaming.md) - Real-time response streaming
- [Function Calling](advanced/function_calling.md) - Tool integration
- [Error Handling](advanced/error_handling.md) - Robust error management
- [Account Management](api/account.md) - API keys and billing
- [Web3 Integration](advanced/web3.md) - Blockchain integration

### Examples & Tutorials
- [Basic Examples](examples/) - Simple usage examples
- [Advanced Examples](examples/advanced/) - Complex integrations
- [Tutorials](tutorials/) - Step-by-step guides
- [Best Practices](best_practices.md) - Production recommendations

## 🎯 Why Venice SDK?

The Venice AI Python SDK is designed to be:

- **🚀 Easy to Use**: Simple, intuitive API that follows Python best practices
- **🔧 Comprehensive**: Complete access to all Venice AI services
- **⚡ High Performance**: Optimized for speed and efficiency
- **🛡️ Reliable**: Built-in error handling, retries, and rate limiting
- **📝 Well Documented**: Extensive documentation and examples
- **🧪 Thoroughly Tested**: 350+ tests with 90%+ pass rate
- **🔄 Compatible**: Drop-in replacement for OpenAI SDK
- **🌐 Flexible**: Support for both admin and inference-only API keys

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

## 📖 License

This project uses a dual license structure:

- **Code/Software**: GNU Affero General Public License v3.0 (AGPLv3) - Strong copyleft protection, requires source code availability for network services
- **Documentation/Examples**: Creative Commons Attribution-ShareAlike 4.0 International (CC-BY-SA) - Attribution required, derivative works must use same license

The Python SDK code is licensed under AGPLv3, while all documentation and examples are licensed under CC-BY-SA 4.0.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](contributing.md) for details.

## 📞 Support

- 📧 **Email**: support@venice.ai
- 💬 **Discord**: [Join our community](https://discord.gg/venice-ai)
- 📖 **Documentation**: [docs.venice.ai](https://docs.venice.ai)
- 🐛 **Issues**: [GitHub Issues](https://github.com/venice-ai/venice-sdk/issues)

---

**Ready to get started?** Check out our [Quick Start Guide](quickstart.md) or explore the [Examples](examples/)!