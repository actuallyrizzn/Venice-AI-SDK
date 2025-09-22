#!/usr/bin/env python3
"""
Function Calling Tutorial

This tutorial demonstrates how to use function calling with the Venice AI SDK.
It covers basic function calling, advanced patterns, and real-world examples.
"""

import json
import time
from typing import Dict, List, Any, Optional
from venice_sdk import VeniceClient
from venice_sdk.errors import VeniceAPIError


def basic_function_calling():
    """Basic function calling example."""
    print("🔧 Basic Function Calling")
    print("=" * 30)
    
    client = VeniceClient()
    
    # Define a simple function
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
    
    # Chat with function calling
    messages = [
        {"role": "user", "content": "What's the weather like in Tokyo?"}
    ]
    
    try:
        response = client.chat.complete(
            messages=messages,
            model="llama-3.3-70b",
            tools=tools
        )
        
        print("Response:", response.choices[0].message.content)
        
        # Check for tool calls
        if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            print("\nTool calls made:")
            for tool_call in response.choices[0].message.tool_calls:
                print(f"- Function: {tool_call.function.name}")
                print(f"- Arguments: {tool_call.function.arguments}")
        
    except VeniceAPIError as e:
        print(f"Error: {e}")


def multiple_functions_example():
    """Example with multiple functions."""
    print("\n🔧 Multiple Functions Example")
    print("=" * 35)
    
    client = VeniceClient()
    
    # Define multiple functions
    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Perform mathematical calculations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate"
                        }
                    },
                    "required": ["expression"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_time",
                "description": "Get the current time",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "timezone": {
                            "type": "string",
                            "description": "Timezone (e.g., 'UTC', 'America/New_York')"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_web",
                "description": "Search the web for information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]
    
    # Test different queries
    test_queries = [
        "What's 15 * 23 + 7?",
        "What time is it in New York?",
        "Search for information about artificial intelligence",
        "Calculate the square root of 144 and tell me the current time"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 40)
        
        try:
            response = client.chat.complete(
                messages=[{"role": "user", "content": query}],
                model="llama-3.3-70b",
                tools=tools
            )
            
            print("Response:", response.choices[0].message.content)
            
            # Show tool calls
            if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
                print("Tool calls:")
                for tool_call in response.choices[0].message.tool_calls:
                    print(f"  - {tool_call.function.name}({tool_call.function.arguments})")
            
        except VeniceAPIError as e:
            print(f"Error: {e}")


def function_calling_with_execution():
    """Function calling with actual function execution."""
    print("\n🔧 Function Calling with Execution")
    print("=" * 40)
    
    client = VeniceClient()
    
    # Define functions that we can actually execute
    def get_weather(location: str) -> str:
        """Mock weather function."""
        # In a real app, this would call a weather API
        weather_data = {
            "Tokyo": "Sunny, 22°C",
            "New York": "Cloudy, 18°C",
            "London": "Rainy, 15°C",
            "Paris": "Partly cloudy, 20°C"
        }
        return weather_data.get(location, f"Weather data not available for {location}")
    
    def calculate(expression: str) -> str:
        """Safe calculation function."""
        try:
            # In production, use a safer evaluation method
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Error: {e}"
    
    def get_time(timezone: str = "UTC") -> str:
        """Get current time."""
        import datetime
        if timezone == "UTC":
            return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        else:
            return f"Time in {timezone}: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Function registry
    functions = {
        "get_weather": get_weather,
        "calculate": calculate,
        "get_time": get_time
    }
    
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
                            "description": "The city name"
                        }
                    },
                    "required": ["location"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Perform mathematical calculations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression"
                        }
                    },
                    "required": ["expression"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_time",
                "description": "Get the current time",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "timezone": {
                            "type": "string",
                            "description": "Timezone (optional)"
                        }
                    },
                    "required": []
                }
            }
        }
    ]
    
    # Test conversation
    messages = [
        {"role": "user", "content": "What's the weather in Tokyo and what's 25 * 4?"}
    ]
    
    try:
        response = client.chat.complete(
            messages=messages,
            model="llama-3.3-70b",
            tools=tools
        )
        
        print("Initial response:", response.choices[0].message.content)
        
        # Execute function calls
        if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            print("\nExecuting function calls...")
            
            for tool_call in response.choices[0].message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"Calling {function_name} with args: {function_args}")
                
                if function_name in functions:
                    result = functions[function_name](**function_args)
                    print(f"Result: {result}")
                    
                    # Add function result to conversation
                    messages.append({
                        "role": "assistant",
                        "content": response.choices[0].message.content
                    })
                    messages.append({
                        "role": "tool",
                        "content": result,
                        "tool_call_id": tool_call.id
                    })
                    
                    # Get final response
                    final_response = client.chat.complete(
                        messages=messages,
                        model="llama-3.3-70b",
                        tools=tools
                    )
                    
                    print(f"Final response: {final_response.choices[0].message.content}")
                else:
                    print(f"Unknown function: {function_name}")
        
    except VeniceAPIError as e:
        print(f"Error: {e}")


def streaming_with_functions():
    """Function calling with streaming responses."""
    print("\n🔧 Streaming with Functions")
    print("=" * 30)
    
    client = VeniceClient()
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_image",
                "description": "Generate an image from a description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Image description"
                        }
                    },
                    "required": ["prompt"]
                }
            }
        }
    ]
    
    messages = [
        {"role": "user", "content": "Create an image of a sunset over mountains and tell me about it"}
    ]
    
    try:
        print("Streaming response: ", end="", flush=True)
        
        for chunk in client.chat.complete_stream(
            messages=messages,
            model="llama-3.3-70b",
            tools=tools
        ):
            if chunk.startswith("data: "):
                data_content = chunk[6:].strip()
                if data_content == "[DONE]":
                    break
                
                try:
                    data = json.loads(data_content)
                    if "choices" in data and data["choices"]:
                        delta = data["choices"][0].get("delta", {})
                        if "content" in delta:
                            print(delta["content"], end="", flush=True)
                        elif "tool_calls" in delta:
                            print(f"\n[Function call detected: {delta['tool_calls']}]")
                except json.JSONDecodeError:
                    pass
        
        print("\n")
        
    except VeniceAPIError as e:
        print(f"Error: {e}")


def advanced_function_patterns():
    """Advanced function calling patterns."""
    print("\n🔧 Advanced Function Patterns")
    print("=" * 35)
    
    client = VeniceClient()
    
    # Complex function with multiple parameters
    tools = [
        {
            "type": "function",
            "function": {
                "name": "book_flight",
                "description": "Book a flight between two cities",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "origin": {
                            "type": "string",
                            "description": "Departure city"
                        },
                        "destination": {
                            "type": "string",
                            "description": "Arrival city"
                        },
                        "date": {
                            "type": "string",
                            "description": "Departure date (YYYY-MM-DD)"
                        },
                        "passengers": {
                            "type": "integer",
                            "description": "Number of passengers",
                            "minimum": 1,
                            "maximum": 9
                        },
                        "class": {
                            "type": "string",
                            "enum": ["economy", "business", "first"],
                            "description": "Seat class"
                        }
                    },
                    "required": ["origin", "destination", "date"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_hotels",
                "description": "Search for hotels in a city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "City name"
                        },
                        "check_in": {
                            "type": "string",
                            "description": "Check-in date (YYYY-MM-DD)"
                        },
                        "check_out": {
                            "type": "string",
                            "description": "Check-out date (YYYY-MM-DD)"
                        },
                        "guests": {
                            "type": "integer",
                            "description": "Number of guests",
                            "minimum": 1,
                            "maximum": 8
                        },
                        "max_price": {
                            "type": "number",
                            "description": "Maximum price per night"
                        }
                    },
                    "required": ["city", "check_in", "check_out"]
                }
            }
        }
    ]
    
    # Test complex queries
    complex_queries = [
        "I want to book a flight from New York to London on 2024-06-15 for 2 passengers in business class",
        "Search for hotels in Paris from 2024-06-15 to 2024-06-20 for 2 guests, maximum $200 per night",
        "Plan a trip: book a flight from San Francisco to Tokyo on 2024-07-01 for 1 passenger, then find hotels in Tokyo from 2024-07-01 to 2024-07-05 for 1 guest under $150 per night"
    ]
    
    for query in complex_queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        
        try:
            response = client.chat.complete(
                messages=[{"role": "user", "content": query}],
                model="llama-3.3-70b",
                tools=tools
            )
            
            print("Response:", response.choices[0].message.content)
            
            # Show tool calls with detailed parameters
            if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
                print("\nTool calls:")
                for tool_call in response.choices[0].message.tool_calls:
                    args = json.loads(tool_call.function.arguments)
                    print(f"  - {tool_call.function.name}:")
                    for key, value in args.items():
                        print(f"    {key}: {value}")
            
        except VeniceAPIError as e:
            print(f"Error: {e}")


def error_handling_in_functions():
    """Error handling in function calling."""
    print("\n🔧 Error Handling in Functions")
    print("=" * 35)
    
    client = VeniceClient()
    
    # Function that might fail
    tools = [
        {
            "type": "function",
            "function": {
                "name": "divide_numbers",
                "description": "Divide two numbers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "numerator": {
                            "type": "number",
                            "description": "The numerator"
                        },
                        "denominator": {
                            "type": "number",
                            "description": "The denominator"
                        }
                    },
                    "required": ["numerator", "denominator"]
                }
            }
        }
    ]
    
    # Test cases including error cases
    test_cases = [
        "What's 10 divided by 2?",
        "What's 5 divided by 0?",
        "What's 100 divided by 4?",
        "What's 7 divided by 3?"
    ]
    
    for query in test_cases:
        print(f"\nQuery: {query}")
        print("-" * 30)
        
        try:
            response = client.chat.complete(
                messages=[{"role": "user", "content": query}],
                model="llama-3.3-70b",
                tools=tools
            )
            
            print("Response:", response.choices[0].message.content)
            
            # Show tool calls
            if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:
                    args = json.loads(tool_call.function.arguments)
                    print(f"Tool call: {tool_call.function.name}({args})")
                    
                    # Simulate function execution
                    try:
                        result = args["numerator"] / args["denominator"]
                        print(f"Result: {result}")
                    except ZeroDivisionError:
                        print("Error: Division by zero!")
                    except Exception as e:
                        print(f"Error: {e}")
            
        except VeniceAPIError as e:
            print(f"API Error: {e}")


def main():
    """Run all function calling examples."""
    print("🎯 Function Calling Tutorial")
    print("=" * 50)
    
    try:
        # Basic examples
        basic_function_calling()
        multiple_functions_example()
        
        # Advanced examples
        function_calling_with_execution()
        streaming_with_functions()
        advanced_function_patterns()
        error_handling_in_functions()
        
        print("\n✅ Function calling tutorial completed!")
        print("\nKey takeaways:")
        print("- Function calling allows AI to use external tools")
        print("- Define clear function schemas with proper parameters")
        print("- Handle function execution and errors gracefully")
        print("- Use streaming for real-time function calling")
        print("- Complex functions can have multiple parameters and validation")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Tutorial interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")


if __name__ == "__main__":
    main()
