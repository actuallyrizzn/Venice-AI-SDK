# Function Calling

The Venice SDK supports function calling, allowing models to request the execution of specific functions based on user input.

## Basic Function Calling

```python
from venice_sdk import HTTPClient, ChatAPI

client = HTTPClient()
chat = ChatAPI(client)

# Define tools
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

# Use tools in chat
response = chat.complete(
    messages=[{"role": "user", "content": "What's the weather in San Francisco?"}],
    model="llama-3.3-70b",
    tools=tools
)

# Check for tool calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        print(f"Function: {tool_call.function.name}")
        print(f"Arguments: {tool_call.function.arguments}")
```

## Multiple Tools

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
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Get the current stock price for a symbol",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "The stock symbol, e.g. AAPL"
                    }
                },
                "required": ["symbol"]
            }
        }
    }
]

response = chat.complete(
    messages=[{"role": "user", "content": "What's the weather in SF and the price of AAPL?"}],
    model="llama-3.3-70b",
    tools=tools
)
```

## Tool Response Handling

```python
def handle_tool_call(tool_call):
    if tool_call.function.name == "get_weather":
        # Parse arguments
        args = json.loads(tool_call.function.arguments)
        location = args["location"]
        
        # Call weather API
        weather = get_weather_api(location)
        
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": json.dumps(weather)
        }
    elif tool_call.function.name == "get_stock_price":
        # Handle stock price request
        pass

# Process tool calls
if response.choices[0].message.tool_calls:
    tool_responses = []
    for tool_call in response.choices[0].message.tool_calls:
        tool_response = handle_tool_call(tool_call)
        tool_responses.append(tool_response)
    
    # Continue conversation with tool responses
    messages = response.choices[0].message.content + tool_responses
    response = chat.complete(
        messages=messages,
        model="llama-3.3-70b",
        tools=tools
    )
```

## Error Handling

```python
from venice_sdk.errors import VeniceAPIError, InvalidRequestError

try:
    response = chat.complete(
        messages=[{"role": "user", "content": "What's the weather?"}],
        model="llama-3.3-70b",
        tools=tools
    )
except InvalidRequestError as e:
    print(f"Invalid tool configuration: {e}")
except VeniceAPIError as e:
    print(f"API error: {e}")
```

## Best Practices

1. **Tool Descriptions**: Write clear, concise descriptions for each tool.
2. **Parameter Validation**: Validate tool parameters before execution.
3. **Error Handling**: Implement robust error handling for tool execution.
4. **Response Formatting**: Format tool responses consistently.
5. **Tool Selection**: Choose appropriate models that support function calling.

## Example: Complete Tool Integration

```python
class ToolHandler:
    def __init__(self, chat: ChatAPI, tools: List[Dict]):
        self.chat = chat
        self.tools = tools

    def process_message(self, message: str) -> str:
        # Initial completion
        response = self.chat.complete(
            messages=[{"role": "user", "content": message}],
            model="llama-3.3-70b",
            tools=self.tools
        )

        # Handle tool calls
        if response.choices[0].message.tool_calls:
            tool_responses = []
            for tool_call in response.choices[0].message.tool_calls:
                tool_response = self.handle_tool_call(tool_call)
                tool_responses.append(tool_response)
            
            # Get final response
            messages = response.choices[0].message.content + tool_responses
            final_response = self.chat.complete(
                messages=messages,
                model="llama-3.3-70b",
                tools=self.tools
            )
            return final_response.choices[0].message.content
        
        return response.choices[0].message.content

    def handle_tool_call(self, tool_call):
        # Implement tool-specific logic
        pass

# Usage
handler = ToolHandler(chat, tools)
response = handler.process_message("What's the weather in SF and the price of AAPL?")
print(response)
```

## Related

- [Chat API](../api/chat.md) - Chat completion functionality
- [Error Handling](../advanced/error_handling.md) - Error handling best practices
- [Streaming](../advanced/streaming.md) - Using streaming with function calls 