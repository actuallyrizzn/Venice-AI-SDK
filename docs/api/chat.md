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
    model: str = "llama-3.3-70b",
    *,
    temperature: float = 0.7,
    stream: bool = False,
    tools: Optional[List[Dict]] = None,
    venice_parameters: Optional[Dict] = None,
    # New parameters from Swagger specification
    frequency_penalty: Optional[float] = None,
    logprobs: Optional[bool] = None,
    top_logprobs: Optional[int] = None,
    max_completion_tokens: Optional[int] = None,
    max_temp: Optional[float] = None,
    min_p: Optional[float] = None,
    min_temp: Optional[float] = None,
    n: int = 1,
    presence_penalty: Optional[float] = None,
    repetition_penalty: Optional[float] = None,
    seed: Optional[int] = None,
    stop: Optional[Union[str, List[str]]] = None,
    stop_token_ids: Optional[List[int]] = None,
    stream_options: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Union[Dict, Generator[str, None, None]]
```

Generate a chat completion with comprehensive parameter support.

##### Parameters

- `messages` (List[Dict[str, str]]): List of message dictionaries with 'role' and 'content' keys
- `model` (str): ID of the model to use. Defaults to "llama-3.3-70b"
- `temperature` (float): Sampling temperature (0-2). Defaults to 0.7
- `stream` (bool): Whether to stream the response. Defaults to False
- `tools` (Optional[List[Dict]]): List of tools available to the model
- `venice_parameters` (Optional[Dict]): Additional Venice-specific parameters

**Advanced Parameters:**
- `frequency_penalty` (Optional[float]): Number between -2.0 and 2.0. Positive values penalize new tokens based on frequency
- `presence_penalty` (Optional[float]): Number between -2.0 and 2.0. Positive values penalize tokens based on presence
- `repetition_penalty` (Optional[float]): Parameter for repetition penalty. 1.0 means no penalty, >1.0 discourages repetition
- `logprobs` (Optional[bool]): Whether to include log probabilities in the response
- `top_logprobs` (Optional[int]): Number of highest probability tokens to return for each token position
- `max_completion_tokens` (Optional[int]): Upper bound for tokens that can be generated
- `max_temp` (Optional[float]): Maximum temperature value for dynamic temperature scaling (0-2)
- `min_p` (Optional[float]): Minimum probability threshold for token selection (0-1)
- `min_temp` (Optional[float]): Minimum temperature value for dynamic temperature scaling (0-2)
- `n` (int): Number of chat completion choices to generate. Defaults to 1
- `seed` (Optional[int]): Random seed for reproducible responses
- `stop` (Optional[Union[str, List[str]]]): Up to 4 sequences where the API will stop generating
- `stop_token_ids` (Optional[List[int]]): Array of token IDs where the API will stop generating
- `stream_options` (Optional[Dict[str, Any]]): Options for streaming (e.g., include_usage)
- `**kwargs`: Additional parameters passed to the API

##### Returns

- Union[Dict, Generator[str, None, None]]: Completion response or generator for streaming responses

##### Examples

**Basic Usage:**
```python
from venice_sdk import VeniceClient

client = VeniceClient(api_key="your-api-key")
response = client.chat.complete(
    messages=[{"role": "user", "content": "Hello, how are you?"}],
    model="llama-3.3-70b"
)
print(response["choices"][0]["message"]["content"])
```

**Advanced Parameters:**
```python
response = client.chat.complete(
    messages=[{"role": "user", "content": "Write a creative story"}],
    model="llama-3.3-70b",
    temperature=1.2,
    frequency_penalty=0.3,
    presence_penalty=-0.1,
    repetition_penalty=1.1,
    max_completion_tokens=500,
    n=3,  # Generate 3 different responses
    seed=42  # For reproducible results
)
```

**Dynamic Temperature Scaling:**
```python
response = client.chat.complete(
    messages=[{"role": "user", "content": "Write a poem"}],
    model="llama-3.3-70b",
    min_temp=0.5,
    max_temp=1.5,
    logprobs=True,
    top_logprobs=3
)
```

**Stop Sequences:**
```python
response = client.chat.complete(
    messages=[{"role": "user", "content": "Count from 1 to 10"}],
    model="llama-3.3-70b",
    stop=["5", "6"],  # Stop when reaching 5 or 6
    max_completion_tokens=100
)
```

**Streaming with Options:**
```python
response = client.chat.complete(
    messages=[{"role": "user", "content": "Explain quantum computing"}],
    model="llama-3.3-70b",
    stream=True,
    stream_options={"include_usage": True},
    max_completion_tokens=200
)

for chunk in response:
    print(chunk, end="")
```

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