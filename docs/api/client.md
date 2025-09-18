# Client API Reference

The `HTTPClient` class is the core of the SDK, handling authentication, retries, and HTTP requests to the Venice API.

## HTTPClient

```python
class HTTPClient:
    def __init__(self, config: Optional[Config] = None)
```

### Parameters

- `config` (Optional[Config]): If not provided, configuration is loaded from environment via `load_config()`.

### Methods

#### get

```python
def get(self, endpoint: str, **kwargs) -> requests.Response
```

Performs a GET request to the given `endpoint` (joined with the configured `base_url`).

#### post

```python
def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response
```

Performs a POST request with JSON body `data`.

#### stream

```python
def stream(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Generator[str, None, None]
```

Performs a streaming POST request and yields string chunks.

### Error handling

All methods raise SDK exceptions on errors:
- `UnauthorizedError` for 401
- `RateLimitError` for 429 (includes optional `retry_after`)
- `InvalidRequestError` for other client errors (including certain 404s)
- `VeniceAPIError` for other API errors
- `VeniceConnectionError` for transport-level failures

## Examples

### Basic Usage

```python
from venice_sdk import HTTPClient

client = HTTPClient()  # Reads config from environment/.env

# List models
resp = client.get("models")
print(resp.json())
```

### Streaming Response

```python
from venice_sdk import HTTPClient

client = HTTPClient()

for chunk in client.stream(
    "chat/completions",
    data={
        "messages": [{"role": "user", "content": "Hello"}],
        "model": "llama-3.3-70b",
        "stream": True,
    },
):
    print(chunk, end="", flush=True)
```

### Error Handling

```python
from venice_sdk.errors import VeniceAPIError, RateLimitError

client = HTTPClient()

try:
    client.get("models")
except RateLimitError:
    print("Rate limit exceeded. Please try again later.")
except VeniceAPIError as e:
    print(f"API error: {e}")
```

## Related

- [Chat API](chat.md) - Chat completion functionality
- [Models API](models.md) - Model discovery and management
- [Errors](errors.md) - Error handling and exceptions