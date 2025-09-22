#!/usr/bin/env python3
"""
Advanced Streaming Chat Example

This example demonstrates advanced streaming chat capabilities including:
- Real-time streaming responses
- Function calling with streaming
- Error handling and recovery
- Custom streaming handlers
- Multiple model support
"""

import asyncio
import json
import time
from typing import AsyncGenerator, Dict, Any, List
from venice_sdk import VeniceClient
from venice_sdk.errors import VeniceAPIError, RateLimitError


class StreamingChatHandler:
    """Custom handler for streaming chat responses."""
    
    def __init__(self, show_tokens: bool = False, show_timing: bool = False):
        self.show_tokens = show_tokens
        self.show_timing = show_timing
        self.start_time = None
        self.token_count = 0
        
    def on_start(self):
        """Called when streaming starts."""
        self.start_time = time.time()
        self.token_count = 0
        print("🚀 Starting stream...")
        
    def on_chunk(self, chunk: str):
        """Called for each streaming chunk."""
        if self.show_tokens:
            print(f"📦 Chunk: {repr(chunk)}")
        
        # Parse SSE format
        if chunk.startswith("data: "):
            data_content = chunk[6:].strip()
            if data_content == "[DONE]":
                self.on_end()
                return
                
            try:
                data = json.loads(data_content)
                if "choices" in data and data["choices"]:
                    delta = data["choices"][0].get("delta", {})
                    if "content" in delta:
                        content = delta["content"]
                        print(content, end="", flush=True)
                        self.token_count += len(content.split())
            except json.JSONDecodeError:
                pass
                
    def on_end(self):
        """Called when streaming ends."""
        if self.show_timing and self.start_time:
            duration = time.time() - self.start_time
            print(f"\n\n⏱️  Stream completed in {duration:.2f}s")
            print(f"📊 Tokens: {self.token_count}")
            print(f"⚡ Speed: {self.token_count/duration:.1f} tokens/sec")


def basic_streaming_example():
    """Basic streaming chat example."""
    print("=== Basic Streaming Chat ===")
    
    client = VeniceClient()
    handler = StreamingChatHandler(show_timing=True)
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Be concise but informative."},
        {"role": "user", "content": "Tell me about the history of artificial intelligence in 3 paragraphs."}
    ]
    
    try:
        handler.on_start()
        
        # Use the streaming method
        for chunk in client.chat.complete_stream(
            messages=messages,
            model="llama-3.3-70b",
            temperature=0.7
        ):
            handler.on_chunk(chunk)
            
    except VeniceAPIError as e:
        print(f"\n❌ API Error: {e}")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")


def function_calling_streaming_example():
    """Streaming chat with function calling."""
    print("\n=== Function Calling with Streaming ===")
    
    client = VeniceClient()
    
    # Define tools for function calling
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
        }
    ]
    
    messages = [
        {"role": "user", "content": "What's the weather like in Tokyo and calculate 15 * 23 + 7?"}
    ]
    
    try:
        print("🤖 Assistant: ", end="", flush=True)
        
        for chunk in client.chat.complete_stream(
            messages=messages,
            model="llama-3.3-70b",
            tools=tools,
            temperature=0.3
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
                            # Handle function calls
                            for tool_call in delta["tool_calls"]:
                                if tool_call.get("type") == "function":
                                    function_name = tool_call["function"]["name"]
                                    print(f"\n🔧 Calling function: {function_name}")
                except json.JSONDecodeError:
                    pass
                    
        print("\n")
        
    except VeniceAPIError as e:
        print(f"\n❌ API Error: {e}")


def multi_model_comparison():
    """Compare streaming responses across different models."""
    print("\n=== Multi-Model Comparison ===")
    
    client = VeniceClient()
    models = ["llama-3.3-70b", "llama-3.3-8b", "gpt-4o-mini"]
    
    prompt = "Explain quantum computing in simple terms."
    
    for model in models:
        print(f"\n🤖 {model}:")
        print("-" * 50)
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            start_time = time.time()
            token_count = 0
            
            for chunk in client.chat.complete_stream(
                messages=messages,
                model=model,
                temperature=0.7,
                max_tokens=200
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
                                content = delta["content"]
                                print(content, end="", flush=True)
                                token_count += len(content.split())
                    except json.JSONDecodeError:
                        pass
            
            duration = time.time() - start_time
            print(f"\n\n📊 {model}: {token_count} tokens in {duration:.2f}s ({token_count/duration:.1f} tok/s)")
            
        except VeniceAPIError as e:
            print(f"❌ Error with {model}: {e}")
        except Exception as e:
            print(f"💥 Unexpected error with {model}: {e}")


def error_handling_streaming():
    """Demonstrate error handling in streaming."""
    print("\n=== Error Handling in Streaming ===")
    
    client = VeniceClient()
    
    # Test with invalid model
    try:
        print("Testing with invalid model...")
        for chunk in client.chat.complete_stream(
            messages=[{"role": "user", "content": "Hello"}],
            model="invalid-model"
        ):
            print(chunk)
    except VeniceAPIError as e:
        print(f"✅ Caught expected error: {e}")
    
    # Test with rate limiting (simulate)
    try:
        print("\nTesting rate limit handling...")
        for i in range(5):  # Rapid requests
            try:
                for chunk in client.chat.complete_stream(
                    messages=[{"role": "user", "content": f"Request {i+1}"}],
                    model="llama-3.3-70b"
                ):
                    if chunk.startswith("data: "):
                        data_content = chunk[6:].strip()
                        if data_content == "[DONE]":
                            break
            except RateLimitError as e:
                print(f"⏳ Rate limited: {e}")
                time.sleep(1)  # Wait before retry
            except VeniceAPIError as e:
                print(f"❌ API Error: {e}")
                break
    except Exception as e:
        print(f"💥 Unexpected error: {e}")


def custom_streaming_processor():
    """Custom streaming processor with advanced features."""
    print("\n=== Custom Streaming Processor ===")
    
    class AdvancedStreamingProcessor:
        def __init__(self, client: VeniceClient):
            self.client = client
            self.conversation_history = []
            
        def stream_conversation(self, user_input: str, model: str = "llama-3.3-70b") -> str:
            """Stream a conversation with history."""
            self.conversation_history.append({"role": "user", "content": user_input})
            
            print(f"👤 User: {user_input}")
            print("🤖 Assistant: ", end="", flush=True)
            
            response_content = ""
            
            try:
                for chunk in self.client.chat.complete_stream(
                    messages=self.conversation_history,
                    model=model,
                    temperature=0.7
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
                                    content = delta["content"]
                                    print(content, end="", flush=True)
                                    response_content += content
                        except json.JSONDecodeError:
                            pass
                
                # Add assistant response to history
                self.conversation_history.append({"role": "assistant", "content": response_content})
                print("\n")
                
                return response_content
                
            except VeniceAPIError as e:
                print(f"\n❌ API Error: {e}")
                return ""
    
    # Use the processor
    client = VeniceClient()
    processor = AdvancedStreamingProcessor(client)
    
    # Simulate a conversation
    conversation = [
        "Hello! I'm interested in learning about machine learning.",
        "What are the main types of machine learning?",
        "Can you give me a simple example of supervised learning?",
        "Thank you! That was very helpful."
    ]
    
    for user_input in conversation:
        processor.stream_conversation(user_input)
        time.sleep(1)  # Pause between messages


def main():
    """Run all streaming examples."""
    print("🎯 Advanced Streaming Chat Examples")
    print("=" * 50)
    
    try:
        # Basic streaming
        basic_streaming_example()
        
        # Function calling with streaming
        function_calling_streaming_example()
        
        # Multi-model comparison
        multi_model_comparison()
        
        # Error handling
        error_handling_streaming()
        
        # Custom processor
        custom_streaming_processor()
        
        print("\n✅ All examples completed!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Examples interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")


if __name__ == "__main__":
    main()
