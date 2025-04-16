# Installation

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installing the SDK

You can install the Venice SDK using pip:

```bash
pip install venice-sdk
```

## Development Installation

If you want to contribute to the SDK or run the tests, you'll need to install it in development mode:

```bash
# Clone the repository
git clone https://github.com/yourusername/venice-sdk.git
cd venice-sdk

# Install in development mode with all dependencies
pip install -e ".[dev]"
```

## Optional Dependencies

The SDK has several optional dependencies that you can install based on your needs:

```bash
# For testing
pip install -e ".[test]"

# For documentation
pip install -e ".[docs]"

# For all optional dependencies
pip install -e ".[all]"
```

## Verifying the Installation

You can verify that the SDK is installed correctly by running:

```python
import venice_sdk
print(venice_sdk.__version__)
```

## Configuration

After installation, you'll need to configure your API key. You can do this in several ways:

1. Environment variables:
   ```bash
   export VENICE_API_KEY="your-api-key"
   ```

2. `.env` file:
   ```env
   VENICE_API_KEY=your-api-key
   ```

3. Direct initialization:
   ```python
   from venice_sdk import VeniceClient
   client = VeniceClient(api_key="your-api-key")
   ```

## Next Steps

- [Quick Start](quickstart.md) - Get started with the SDK
- [Configuration](configuration.md) - Learn more about configuration options
- [API Reference](api/client.md) - Explore the SDK's API 