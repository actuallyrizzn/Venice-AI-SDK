# Models API Reference

The `ModelsAPI` class provides functionality for discovering and managing available models.

## ModelsAPI

```python
class ModelsAPI:
    def __init__(self, client: VeniceClient)
```

### Parameters

- `client` (VeniceClient): An initialized VeniceClient instance

### Methods

#### list

```python
def list(self) -> List[Dict[str, Any]]
```

List all available models.

##### Returns

- List[Dict[str, Any]]: List of model dictionaries with their properties

##### Raises

- `VeniceAPIError`: Base exception for API errors
- `UnauthorizedError`: Invalid or missing API key
- `RateLimitError`: Rate limit exceeded

#### get

```python
def get(self, model_id: str) -> Dict[str, Any]
```

Get details for a specific model.

##### Parameters

- `model_id` (str): ID of the model to retrieve

##### Returns

- Dict[str, Any]: Model details

##### Raises

- `VeniceAPIError`: Base exception for API errors
- `UnauthorizedError`: Invalid or missing API key
- `RateLimitError`: Rate limit exceeded
- `InvalidRequestError`: Model not found

## Examples

### Listing All Models

```python
from venice_sdk import VeniceClient, ModelsAPI

client = VeniceClient()
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
print(f"Description: {model_details['model_spec']['modelSource']}")
```

### Filtering Models

```python
# Filter for text models only
text_models = [m for m in models.list() if m['type'] == 'text']
for model in text_models:
    print(f"Text Model: {model['id']}")
    print(f"Description: {model['model_spec']['modelSource']}")
```

### Error Handling

```python
from venice_sdk.errors import VeniceAPIError, RateLimitError

try:
    model = models.get("nonexistent-model")
except VeniceAPIError as e:
    print(f"Error retrieving model: {e}")
```

## Model Properties

Each model has the following properties:

- `id` (str): Unique identifier for the model
- `type` (str): Type of model (e.g., "text")
- `object` (str): Always "model"
- `created` (int): Unix timestamp of creation
- `owned_by` (str): Owner of the model
- `model_spec` (Dict): Model specifications including:
  - `availableContextTokens` (int): Maximum context length
  - `capabilities` (Dict): Model capabilities
  - `constraints` (Dict): Model constraints
  - `offline` (bool): Whether the model is offline
  - `traits` (List[str]): Model traits
  - `modelSource` (str): Source URL of the model

## Related

- [Client API](client.md) - Core HTTP client functionality
- [Chat API](chat.md) - Chat completion functionality
- [Errors](errors.md) - Error handling and exceptions 