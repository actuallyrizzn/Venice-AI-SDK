# Models API Reference

The `ModelsAPI` class provides functionality for discovering and managing available models via the `models` endpoint.

## ModelsAPI

```python
class ModelsAPI:
    def __init__(self, client: HTTPClient)
```

### Parameters

- `client` (HTTPClient): An initialized HTTPClient instance

### Methods

#### list

```python
def list(self) -> List[Dict]
```

List all available models. Internally calls `GET models` and returns the `data` field.

##### Returns

- List[Dict[str, Any]]: List of model dictionaries with their properties

##### Raises

- `VeniceAPIError`: Base exception for API errors
- `UnauthorizedError`: Invalid or missing API key
- `RateLimitError`: Rate limit exceeded

#### get

```python
def get(self, model_id: str) -> Dict
```

Get details for a specific model by first listing models and selecting the match.

##### Parameters

- `model_id` (str): ID of the model to retrieve

##### Returns

- Dict[str, Any]: Model details

##### Raises

- `VeniceAPIError`: Base exception for API errors (includes not found)
- `UnauthorizedError`: Invalid or missing API key
- `RateLimitError`: Rate limit exceeded

## Examples

### Listing All Models

```python
from venice_sdk import HTTPClient
from venice_sdk.models import ModelsAPI

client = HTTPClient()
models = ModelsAPI(client)

# List all models
all_models = models.list()
for model in all_models:
    print(f"Model: {model['id']}")
    print(f"Type: {model['type']}")
    print(f"Description: {model['model_spec']['modelSource']}")
    print("Capabilities:")
    print(f"  - Function Calling: {model['model_spec']['capabilities']['supportsFunctionCalling']}")
    print(f"  - Web Search: {model['model_spec']['capabilities']['supportsWebSearch']}")
    print(f"  - Context Tokens: {model['model_spec']['availableContextTokens']}")
    print()
```

### Getting Model Details

```python
# Get specific model details
model_details = models.get("llama-3.3-70b")
print(f"Model: {model_details['id']}")
print(f"Type: {model_details['type']}")
```

### Filtering Models

```python
# Filter for text models only
text_models = [m for m in models.list() if m['type'] == 'text']
for model in text_models:
    print(f"Text Model: {model['id']}")
```

### Error Handling

```python
from venice_sdk.errors import VeniceAPIError

try:
    model = models.get("nonexistent-model")
except VeniceAPIError as e:
    print(f"Error retrieving model: {e}")
```

## Model Properties (typical)

Common fields returned by the `models` endpoint include:

- `id` (str): Unique identifier for the model
- `type` (str): Type of model (e.g., "text")
- `model_spec` (Dict): Specifications, including:
  - `availableContextTokens` (int)
  - `capabilities.supportsFunctionCalling` (bool)
  - `capabilities.supportsWebSearch` (bool)

## Related

- [Client API](client.md) - Core HTTP client functionality
- [Chat API](chat.md) - Chat completion functionality
- [Errors](errors.md) - Error handling and exceptions 