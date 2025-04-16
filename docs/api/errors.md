# Errors API Reference

The `errors` module defines the exception hierarchy for the Venice SDK.

## Exception Hierarchy

```python
class VeniceAPIError(Exception)
    ├── UnauthorizedError
    ├── RateLimitError
    ├── InvalidRequestError
    └── APIError
```

## Exceptions

### VeniceAPIError

Base exception for all Venice API errors.

```python
class VeniceAPIError(Exception):
    def __init__(self, message: str, code: Optional[str] = None)
```

#### Parameters

- `message` (str): Error message
- `code` (Optional[str]): Error code from the API

### UnauthorizedError

Raised when authentication fails.

```python
class UnauthorizedError(VeniceAPIError):
    def __init__(self, message: str = "Authentication failed")
```

### RateLimitError

Raised when rate limits are exceeded.

```python
class RateLimitError(VeniceAPIError):
    def __init__(self, message: str = "Rate limit exceeded")
```

### InvalidRequestError

Raised when the request is invalid.

```python
class InvalidRequestError(VeniceAPIError):
    def __init__(self, message: str, code: Optional[str] = None)
```

### APIError

Raised for other API errors.

```python
class APIError(VeniceAPIError):
    def __init__(self, message: str, code: Optional[str] = None)
```

## Examples

### Basic Error Handling

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

### Specific Error Handling

```python
from venice_sdk.errors import UnauthorizedError, InvalidRequestError

try:
    response = client.request(...)
except UnauthorizedError:
    print("Authentication failed. Please check your API key.")
except InvalidRequestError as e:
    print(f"Invalid request: {e}")
except VeniceAPIError as e:
    print(f"Other API error: {e}")
```

### Error Codes

The SDK maps common error codes to specific exceptions:

| Error Code | Exception |
|------------|------------|
| `UNAUTHORIZED` | `UnauthorizedError` |
| `RATE_LIMIT_EXCEEDED` | `RateLimitError` |
| `INVALID_MODEL` | `InvalidRequestError` |
| `INVALID_REQUEST` | `InvalidRequestError` |
| Others | `APIError` |

## Related

- [Client API](client.md) - Core HTTP client functionality
- [Chat API](chat.md) - Chat completion functionality
- [Models API](models.md) - Model discovery and management 