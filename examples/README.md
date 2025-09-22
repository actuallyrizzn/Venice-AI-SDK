# Venice AI SDK Examples

This directory contains comprehensive examples demonstrating how to use the Venice AI SDK for various use cases.

## 📁 Directory Structure

```
examples/
├── README.md                    # This file
├── basic_chat.py               # Basic chat completion example
├── complete_api_demo.py        # Complete API demonstration
├── quick_start.py              # Quick start guide
├── advanced/                   # Advanced examples
│   ├── streaming_chat.py       # Advanced streaming chat
│   ├── image_processing_pipeline.py  # Image processing pipeline
│   ├── ai_assistant.py         # Complete AI assistant
│   └── advanced_parameters.py  # Advanced parameter demonstrations
├── tutorials/                  # Step-by-step tutorials
│   ├── getting_started.py      # Getting started tutorial
│   └── function_calling.py     # Function calling tutorial
└── integrations/               # Integration examples
    └── web_app.py              # Flask web application
```

## 🚀 Quick Start

### Basic Chat
```python
from venice_sdk import VeniceClient

client = VeniceClient()
response = client.chat.complete(
    messages=[{"role": "user", "content": "Hello!"}],
    model="llama-3.3-70b"
)
print(response.choices[0].message.content)
```

### Image Generation
```python
image = client.images.generate(
    prompt="A beautiful sunset over mountains",
    model="dall-e-3"
)
image.save("sunset.png")
```

### Text-to-Speech
```python
audio = client.audio.speech(
    input_text="Hello from Venice AI!",
    voice="alloy"
)
audio.save("hello.mp3")
```

## 📚 Examples by Category

### 🎯 Advanced Parameters
```python
# Demonstrate all advanced parameters from Swagger spec
from examples.advanced.advanced_parameters import main

# Run comprehensive parameter demonstrations
main()
```

### 🤖 Basic Examples

#### `basic_chat.py`
Simple chat completion example showing the most basic usage.

**Features:**
- Basic chat completion
- Error handling
- Model selection

**Run:**
```bash
python examples/basic_chat.py
```

#### `complete_api_demo.py`
Comprehensive demonstration of all API features.

**Features:**
- Chat completions
- Image generation
- Audio synthesis
- Embeddings
- Character management
- Account management

**Run:**
```bash
python examples/complete_api_demo.py
```

#### `quick_start.py`
Quick start guide with essential examples.

**Features:**
- Installation check
- Authentication setup
- First API calls
- Common patterns

**Run:**
```bash
python examples/quick_start.py
```

### 🎓 Tutorials

#### `tutorials/getting_started.py`
Complete step-by-step tutorial for beginners.

**Features:**
- 10-step tutorial
- Interactive learning
- Error handling
- Best practices

**Run:**
```bash
python examples/tutorials/getting_started.py
```

#### `tutorials/function_calling.py`
Comprehensive function calling tutorial.

**Features:**
- Basic function calling
- Multiple functions
- Function execution
- Streaming with functions
- Advanced patterns
- Error handling

**Run:**
```bash
python examples/tutorials/function_calling.py
```

### 🚀 Advanced Examples

#### `advanced/streaming_chat.py`
Advanced streaming chat with real-time responses.

**Features:**
- Real-time streaming
- Function calling with streaming
- Error handling and recovery
- Custom streaming handlers
- Multi-model comparison

**Run:**
```bash
python examples/advanced/streaming_chat.py
```

#### `advanced/image_processing_pipeline.py`
Complete image processing pipeline with batch processing.

**Features:**
- Batch image generation
- Image editing and enhancement
- Style transfer
- Upscaling and optimization
- Error handling and recovery
- Progress tracking

**Run:**
```bash
python examples/advanced/image_processing_pipeline.py
```

#### `advanced/ai_assistant.py`
Complete AI assistant with multiple capabilities.

**Features:**
- Chat with function calling
- Image generation
- Audio synthesis
- Weather information
- Mathematical calculations
- Web search
- Conversation management

**Run:**
```bash
python examples/advanced/ai_assistant.py
```

### 🌐 Integration Examples

#### `integrations/web_app.py`
Flask web application with full AI capabilities.

**Features:**
- Web interface for all AI features
- Chat with streaming
- Image generation
- Audio synthesis
- Embeddings
- Model selection
- Account management

**Run:**
```bash
python examples/integrations/web_app.py
```

Then open: http://localhost:5000

## 🛠️ Setup Requirements

### Prerequisites
- Python 3.8 or higher
- Venice AI API key
- Required dependencies (see main README)

### Environment Setup
```bash
# Set your API key
export VENICE_API_KEY="your-api-key-here"

# Or create a .env file
echo "VENICE_API_KEY=your-api-key-here" > .env
```

### Install Dependencies
```bash
# Install the SDK
pip install venice-sdk

# For development with all dependencies
pip install venice-sdk[dev]

# For web app integration
pip install venice-sdk flask
```

## 📖 How to Use Examples

### 1. Choose Your Example
Browse the examples above and choose one that matches your use case.

### 2. Set Up Environment
Make sure you have your API key set up and dependencies installed.

### 3. Run the Example
```bash
python examples/path/to/example.py
```

### 4. Modify and Experiment
Copy the example code and modify it for your specific needs.

## 🎯 Example Use Cases

### For Beginners
- Start with `tutorials/getting_started.py`
- Try `basic_chat.py` for simple chat
- Explore `quick_start.py` for essential patterns

### For Developers
- Use `complete_api_demo.py` to see all features
- Try `advanced/ai_assistant.py` for complex applications
- Check `integrations/web_app.py` for web integration

### For Advanced Users
- Explore `advanced/streaming_chat.py` for real-time features
- Use `advanced/image_processing_pipeline.py` for batch processing
- Try `tutorials/function_calling.py` for tool integration

## 🔧 Customization

### Modifying Examples
All examples are designed to be easily customizable:

1. **Change Models**: Update the `model` parameter
2. **Add Functions**: Extend the function calling examples
3. **Custom UI**: Modify the web app for your needs
4. **Error Handling**: Add your own error handling logic

### Creating New Examples
When creating new examples:

1. Follow the existing structure
2. Add comprehensive error handling
3. Include clear documentation
4. Test with different API keys
5. Add to this README

## 🐛 Troubleshooting

### Common Issues

**"API key not found"**
- Set the `VENICE_API_KEY` environment variable
- Check your `.env` file
- Verify the key is valid

**"Model not available"**
- Check available models with `client.models.list()`
- Try a different model
- Verify your account has access

**"Rate limit exceeded"**
- Wait for the rate limit to reset
- Implement exponential backoff
- Consider upgrading your plan

**"Import errors"**
- Install required dependencies
- Check Python version (3.8+)
- Verify SDK installation

### Getting Help
- Check the main documentation
- Look at error messages carefully
- Try simpler examples first
- Ask for help on GitHub or Discord

## 📝 Contributing

We welcome contributions to the examples! Please:

1. Follow the existing code style
2. Add comprehensive error handling
3. Include clear documentation
4. Test thoroughly
5. Update this README

## 📄 License

These examples are provided under the same dual license structure as the main SDK:
- **Code/Software**: GNU Affero General Public License v3.0 (AGPLv3)
- **Documentation/Examples**: Creative Commons Attribution-ShareAlike 4.0 International (CC-BY-SA)

The Python SDK code is licensed under AGPLv3, while all documentation and examples are licensed under CC-BY-SA 4.0.

## 🎉 Happy Coding!

These examples should give you everything you need to build amazing AI applications with the Venice AI SDK. Start with the basics and work your way up to the advanced examples.

For more information, check out:
- [Main Documentation](../docs/)
- [API Reference](../docs/api/)
- [GitHub Repository](https://github.com/venice-ai/venice-sdk)
- [Discord Community](https://discord.gg/venice-ai)
