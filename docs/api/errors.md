# Errors API Reference

The `errors` module defines the exception hierarchy for the Venice SDK.

## Exception Hierarchy

```python
class VeniceError(Exception)
    └── VeniceAPIError
        ├── UnauthorizedError
        ├── RateLimitError
        ├── InvalidRequestError
        ├── ModelNotFoundError
        ├── CharacterNotFoundError
```

## Exceptions

### VeniceAPIError

Base exception for all Venice API errors.

```python
class VeniceAPIError(VeniceError):
    def __init__(self, message: str, status_code: int = None)
```

#### Parameters

- `message` (str): Error message
- `code` (Optional[str]): Error code from the API

### UnauthorizedError

Raised when authentication fails.

```python
class UnauthorizedError(VeniceAPIError):
    pass
```

### RateLimitError

Raised when rate limits are exceeded.

```python
class RateLimitError(VeniceAPIError):
    def __init__(self, message: str, retry_after: int = None)
```

### InvalidRequestError

Raised when the request is invalid.

```python
class InvalidRequestError(VeniceAPIError):
    pass
```

### ModelNotFoundError and CharacterNotFoundError

Raised for specific 404 error codes.

```python
class ModelNotFoundError(VeniceAPIError):
    pass

class CharacterNotFoundError(VeniceAPIError):
    pass
```

## Examples

### Basic Error Handling

```python
from venice_sdk import HTTPClient
from venice_sdk.errors import VeniceAPIError, RateLimitError

client = HTTPClient()

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
| `MODEL_NOT_FOUND` | `ModelNotFoundError` |
| `CHARACTER_NOT_FOUND` | `CharacterNotFoundError` |
| (401) | `UnauthorizedError` |
| (429) | `RateLimitError` |
| Other 4xx | `InvalidRequestError` |
| Other >=400 | `VeniceAPIError` |

## Related

- [Client API](client.md) - Core HTTP client functionality
- [Chat API](chat.md) - Chat completion functionality
- [Models API](models.md) - Model discovery and management 