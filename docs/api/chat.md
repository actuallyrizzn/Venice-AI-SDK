# Chat API Reference

The `ChatAPI` class provides a high-level interface for interacting with Venice's chat completion endpoints.

## ChatAPI

```python
class ChatAPI:
    def __init__(self, client: VeniceClient)
```

### Parameters

- `client` (VeniceClient): An initialized VeniceClient instance

### Methods

#### complete

```python
def complete(
    self,
    messages: List[Dict[str, str]],
    model: str,
    *,
    temperature: float = 0.15,
    stream: bool = False,
    max_tokens: Optional[int] = None,
    tools: Optional[List[Dict]] = None,
    venice_parameters: Optional[Dict] = None,
    stop: Optional[Union[str, List[str]]] = None,
    **kwargs
) -> Union[Dict, Generator[str, None, None]]
```

Generate a chat completion.

##### Parameters

- `messages` (List[Dict[str, str]]): List of message dictionaries with 'role' and 'content' keys
- `model` (str): ID of the model to use
- `temperature` (float): Sampling temperature. Defaults to 0.15
- `stream` (bool): Whether to stream the response. Defaults to False
- `max_tokens` (Optional[int]): Maximum number of tokens to generate
- `tools` (Optional[List[Dict]]): List of tools available to the model
- `venice_parameters` (Optional[Dict]): Additional Venice-specific parameters
- `stop` (Optional[Union[str, List[str]]]): Stop sequences
- `**kwargs`: Additional parameters passed to the API

##### Returns

- Union[Dict, Generator[str, None, None]]: Completion response or generator for streaming responses

##### Raises

- `VeniceAPIError`: Base exception for API errors
- `UnauthorizedError`: Invalid or missing API key
- `RateLimitError`: Rate limit exceeded
- `InvalidRequestError`: Invalid request parameters

## Examples

### Basic Chat Completion

```python
from venice_sdk import VeniceClient, ChatAPI

client = VeniceClient()
chat = ChatAPI(client)

response = chat.complete(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    model="llama-3.3-70b"
)

print(response.choices[0].message.content)
```

### Streaming Response

```python
for chunk in chat.complete(
    messages=[{"role": "user", "content": "Tell me a story"}],
    model="llama-3.3-70b",
    stream=True
):
    if chunk:
        print(chunk, end="", flush=True)
```

### Function Calling

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

response = chat.complete(
    messages=[{"role": "user", "content": "What's the weather in San Francisco?"}],
    model="llama-3.3-70b",
    tools=tools
)
```

### Error Handling

```python
from venice_sdk.errors import VeniceAPIError, RateLimitError

try:
    response = chat.complete(...)
except RateLimitError:
    print("Rate limit exceeded. Please try again later.")
except VeniceAPIError as e:
    print(f"API error: {e}")
```

## Related

- [Client API](client.md) - Core HTTP client functionality
- [Models API](models.md) - Model discovery and management
- [Errors](errors.md) - Error handling and exceptions 