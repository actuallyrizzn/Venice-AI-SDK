# Client API Reference

The `VeniceClient` class is the core of the SDK, handling authentication and HTTP requests to the Venice API.

## VeniceClient

```python
class VeniceClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.venice.ai/api/v1",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 1
    )
```

### Parameters

- `api_key` (Optional[str]): Your Venice API key. If not provided, will be loaded from environment variables.
- `base_url` (str): The base URL for the Venice API. Defaults to "https://api.venice.ai/api/v1".
- `timeout` (int): Request timeout in seconds. Defaults to 30.
- `max_retries` (int): Maximum number of retries for failed requests. Defaults to 3.
- `retry_delay` (int): Initial delay between retries in seconds. Defaults to 1.

### Methods

#### request

```python
def request(
    self,
    method: str,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    stream: bool = False
) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]
```

Make a request to the Venice API.

##### Parameters

- `method` (str): HTTP method (GET, POST, etc.)
- `endpoint` (str): API endpoint path
- `params` (Optional[Dict[str, Any]]): Query parameters
- `json` (Optional[Dict[str, Any]]): JSON request body
- `stream` (bool): Whether to stream the response. Defaults to False.

##### Returns

- Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]: Response data or generator for streaming responses

##### Raises

- `VeniceAPIError`: Base exception for API errors
- `UnauthorizedError`: Invalid or missing API key
- `RateLimitError`: Rate limit exceeded
- `InvalidRequestError`: Invalid request parameters

## Examples

### Basic Usage

```python
from venice_sdk import VeniceClient

# Initialize client
client = VeniceClient(api_key="your-api-key")

# Make a request
response = client.request(
    method="GET",
    endpoint="/models"
)
```

### Streaming Response

```python
# Get streaming response
for chunk in client.request(
    method="POST",
    endpoint="/chat/completions",
    json={
        "messages": [{"role": "user", "content": "Hello"}],
        "model": "llama-3.3-70b",
        "stream": True
    },
    stream=True
):
    print(chunk)
```

### Error Handling

```python
from venice_sdk.errors import VeniceAPIError, RateLimitError

try:
    response = client.request(...)
except RateLimitError:
    print("Rate limit exceeded. Please try again later.")
except VeniceAPIError as e:
    print(f"API error: {e}")
```

## Related

- [Chat API](chat.md) - Chat completion functionality
- [Models API](models.md) - Model discovery and management
- [Errors](errors.md) - Error handling and exceptions 