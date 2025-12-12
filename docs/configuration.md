# Configuration

The Venice SDK can be configured in several ways to suit your needs.

## API Key Configuration

There are three ways to configure your API key:

### 1. Environment Variables

Set the `VENICE_API_KEY` environment variable:

```bash
export VENICE_API_KEY=your-api-key
```

### 2. Command Line Interface

Use the CLI to set your API key:

```bash
venice auth your-api-key
```

This will create or update a `.env` file in your current directory.

### 3. Direct Initialization

Pass your API key directly when initializing the client:

```python
from venice_sdk import VeniceClient

client = VeniceClient(api_key="your-api-key")
```

## Client Configuration

The `VeniceClient` can be configured with several options:

```python
client = VeniceClient(
    api_key="your-api-key",              # Optional if set via env or .env
    base_url="https://api.venice.ai/api/v1", # Optional, defaults to production API
    timeout=30,                          # Request timeout in seconds
    max_retries=3,                       # Maximum number of retries
    retry_delay=1                        # Initial delay between retries
)
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `api_key` | str | None | Your Venice API key |
| `base_url` | str | "https://api.venice.ai/api/v1" | Base URL for API requests |
| `timeout` | int | 30 | Request timeout in seconds |
| `max_retries` | int | 3 | Maximum number of retry attempts |
| `retry_delay` | int | 1 | Initial delay between retries (seconds) |

## Environment Variables

All available environment variables:

| Variable | Description |
|----------|-------------|
| `VENICE_API_KEY` | Your Venice API key |
| `VENICE_BASE_URL` | Base URL for API requests |
| `VENICE_TIMEOUT` | Request timeout in seconds |
| `VENICE_MAX_RETRIES` | Maximum number of retries |
| `VENICE_RETRY_DELAY` | Initial delay between retries |
| `VENICE_POOL_CONNECTIONS` | HTTP connection pool connections |
| `VENICE_POOL_MAXSIZE` | HTTP connection pool max size |
| `VENICE_RETRY_BACKOFF_FACTOR` | Retry backoff factor |
| `VENICE_RETRY_STATUS_CODES` | Comma-separated HTTP status codes to retry |

## Using .env Files

Create a `.env` file in your project root:

```env
VENICE_API_KEY=your-api-key
VENICE_BASE_URL=https://api.venice.ai/api/v1
VENICE_TIMEOUT=30
VENICE_MAX_RETRIES=3
VENICE_RETRY_DELAY=1
```

Then load it in your code:

```python
from dotenv import load_dotenv
from venice_sdk import VeniceClient

load_dotenv()  # Load environment variables from .env
client = VeniceClient()  # Will use values from .env
```

## Global Configuration (optional)

The SDK can also read a **global** config file from your user config directory (for example, `~/.config/venice/.env`).

- The CLI can write to this file via `venice auth --global` / `venice configure --global`.
- Reading the global config from the CLI is **opt-in** via `VENICE_USE_GLOBAL_CONFIG=1` (to avoid surprising behavior across environments).

## Configuration Precedence

The SDK uses the following precedence order for configuration (highest to lowest):

1. Direct initialization arguments
2. Environment variables
3. `.env` file values
4. Default values

## Best Practices

1. **Development**: Use `.env` files for local development
2. **Production**: Use environment variables
3. **Testing**: Use direct initialization
4. **CI/CD**: Use environment variables or secrets management

## Running Live Tests

The repository includes `tests/live/` which make real API calls.

- Live tests are **disabled by default**. Enable them by setting `VENICE_LIVE_TESTS=1`.
- Provide credentials via `VENICE_API_KEY` (and optionally `VENICE_BASE_URL`).

## Related

- [Quick Start](quickstart.md)
- [API Reference](api/client.md)
- [Advanced Usage](advanced/streaming.md) 