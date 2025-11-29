# Error Handling

The Venice SDK provides a comprehensive error handling system to help you manage and respond to various types of errors that may occur during API interactions.

## Error Types

The SDK defines several exception types:

```python
from venice_sdk.errors import (
    VeniceAPIError,        # Base API exception
    VeniceConnectionError, # Network / transport errors
    UnauthorizedError,     # Authentication errors
    RateLimitError,        # Rate limit exceeded
    InvalidRequestError,   # Invalid request parameters
    ModelNotFoundError,    # Missing resources
)
```

## Basic Error Handling

```python
from venice_sdk import VeniceClient
from venice_sdk.errors import VeniceAPIError, RateLimitError

client = VeniceClient()

try:
    response = client.request(...)
except RateLimitError:
    print("Rate limit exceeded. Please try again later.")
except VeniceAPIError as e:
    print(f"API error: {e}")
```

## Error Metadata & Formatting

Every `VeniceError` exposes consistent metadata:

- `error_code`: Canonical code (e.g., `MODEL_NOT_FOUND`)
- `status_code`: HTTP status (if available)
- `context`: Normalized dictionary containing request identifiers, retry hints, etc.
- `cause`: The original exception when raised via `raise ... from ...`

The default string representation automatically formats these pieces:

```python
from venice_sdk.errors import VeniceAPIError

try:
    ...
except VeniceAPIError as err:
    # Example: "[RATE_LIMIT] Too many requests (HTTP 429; Context: method='POST', retry_after=5)"
    print(str(err))
    print("code:", err.error_code)
    print("request id:", err.context.get("request_id"))
    if err.__cause__:
        print("root cause:", repr(err.__cause__))
```

## Specific Error Handling

```python
from venice_sdk.errors import UnauthorizedError, InvalidRequestError

try:
    response = client.request(...)
except UnauthorizedError:
    print("Authentication failed. Please check your API key.")
except InvalidRequestError as e:
    print(f"Invalid request: {e}")
    if e.error_code == "INVALID_MODEL":
        print("Please check the model ID and try again.")
except VeniceAPIError as e:
    print(f"Other API error: {e}")
```

## Retry Logic

The SDK includes built-in retry logic for certain types of errors:

```python
from venice_sdk import VeniceClient

# Configure retry behavior
client = VeniceClient(
    max_retries=3,      # Maximum number of retries
    retry_delay=1       # Initial delay between retries in seconds
)

try:
    response = client.request(...)
except VeniceAPIError as e:
    print(f"Request failed after retries: {e}")
```

## Custom Retry Strategy

You can implement a custom retry strategy:

```python
import time
from venice_sdk.errors import VeniceAPIError

def custom_retry(func, max_retries=3, initial_delay=1):
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            return func()
        except VeniceAPIError as e:
            if attempt == max_retries - 1:
                raise
            print(f"Attempt {attempt + 1} failed. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff

# Usage
response = custom_retry(lambda: client.request(...))
```

## Error Codes

The SDK maps common error codes to specific exceptions:

| Error Code | Exception | Description |
|------------|-----------|-------------|
| `UNAUTHORIZED` | `UnauthorizedError` | Invalid or missing API key |
| `RATE_LIMIT_EXCEEDED` | `RateLimitError` | Too many requests sent in a short window |
| `MODEL_NOT_FOUND` | `ModelNotFoundError` | Requested model does not exist |
| `CHARACTER_NOT_FOUND` | `CharacterNotFoundError` | Character slug is missing or deleted |
| `INVALID_MODEL` | `InvalidRequestError` | Invalid model identifier supplied by client |
| `INVALID_REQUEST` | `InvalidRequestError` | Malformed payload or parameters |
| `INVALID_MODEL_PAYLOAD` | `VeniceAPIError` | Upstream response used an unexpected schema |
| `MODEL_PAYLOAD_MISSING_FIELDS` | `VeniceAPIError` | Upstream payload missed required keys |
| _anything else_ | `VeniceAPIError` | Fallback for unmapped API issues |

## Best Practices

1. **Always Handle Errors**: Wrap API calls in try-except blocks.
2. **Specific Error Types**: Catch specific error types when possible.
3. **Retry Strategy**: Implement appropriate retry logic for transient errors.
4. **Error Logging**: Log errors for debugging and monitoring.
5. **User Feedback**: Provide clear error messages to users.

## Example: Comprehensive Error Handling

```python
import logging
from venice_sdk.errors import (
    VeniceAPIError,
    UnauthorizedError,
    RateLimitError,
    InvalidRequestError
)

class APIHandler:
    def __init__(self, client: VeniceClient):
        self.client = client
        self.logger = logging.getLogger(__name__)

    def make_request(self, endpoint: str, **kwargs):
        try:
            return self.client.request(endpoint, **kwargs)
        except UnauthorizedError:
            self.logger.error("Authentication failed")
            raise
        except RateLimitError:
            self.logger.warning("Rate limit exceeded")
            # Implement retry logic
            return self._retry_request(endpoint, **kwargs)
        except InvalidRequestError as e:
            self.logger.error(f"Invalid request: {e}")
            if e.code == "INVALID_MODEL":
                return self._handle_invalid_model(e)
            raise
        except VeniceAPIError as e:
            self.logger.error(f"API error: {e}")
            raise

    def _retry_request(self, endpoint: str, **kwargs):
        max_retries = 3
        delay = 1
        for attempt in range(max_retries):
            try:
                return self.client.request(endpoint, **kwargs)
            except RateLimitError:
                if attempt == max_retries - 1:
                    raise
                self.logger.warning(f"Retry {attempt + 1} failed")
                time.sleep(delay)
                delay *= 2

    def _handle_invalid_model(self, error: InvalidRequestError):
        # Implement model fallback logic
        pass

# Usage
handler = APIHandler(client)
try:
    response = handler.make_request("/chat/completions", ...)
except VeniceAPIError as e:
    print(f"Request failed: {e}")
```

## Related

- [Client API](../api/client.md) - Core HTTP client functionality
- [Chat API](../api/chat.md) - Chat completion functionality
- [Models API](../api/models.md) - Model discovery and management 