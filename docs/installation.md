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

## Dependency version policy

To guarantee reproducible installs, every dependency listed in `pyproject.toml` now has both a minimum and an upper bound. We only permit automatic upgrades within the major versions that we test in CI. For example:

- Runtime: `requests>=2.31.0,<3.0.0`, `python-dotenv>=1.0.0,<2.0.0`, `tiktoken>=0.5.0,<1.0.0`, `psutil>=5.9.0,<6.0.0`, `typing-extensions>=4.5.0,<5.0.0`
- Dev tooling: `pytest>=7.0.0,<8.0.0`, `pytest-cov>=4.0.0,<5.0.0`, `black>=23.0.0,<24.0.0`, `ruff>=0.1.0,<1.0.0`, `mypy>=1.0.0,<2.0.0`
- Documentation/publishing: `mkdocs>=1.4.0,<2.0.0`, `mkdocs-material>=9.0.0,<10.0.0`, `twine>=4.0.0,<5.0.0`, `build>=0.10.0,<2.0.0`

When upstreams release a new major series, we deliberately test against it before expanding the upper bound. This keeps local and CI environments in sync and prevents silent breaking changes from surprise dependency bumps.

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