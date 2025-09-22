#!/usr/bin/env python3
"""
AI Assistant Example

This example demonstrates how to build a comprehensive AI assistant using the Venice AI SDK.
It includes chat, image generation, audio synthesis, and function calling capabilities.
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from venice_sdk import VeniceClient
from venice_sdk.errors import VeniceAPIError, UnauthorizedError


@dataclass
class AssistantMessage:
    """Represents a message in the conversation."""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: float
    message_type: str = "text"  # "text", "image", "audio", "function_call"
    metadata: Optional[Dict[str, Any]] = None


class AIAssistant:
    """Comprehensive AI Assistant using Venice AI SDK."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = VeniceClient(api_key=api_key) if api_key else VeniceClient()
        self.conversation_history: List[AssistantMessage] = []
        self.functions = self._setup_functions()
        
    def _setup_functions(self) -> List[Dict[str, Any]]:
        """Setup available functions for the assistant."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "generate_image",
                    "description": "Generate an image from a text description",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Description of the image to generate"
                            },
                            "style": {
                                "type": "string",
                                "description": "Artistic style for the image",
                                "enum": ["realistic", "cartoon", "anime", "painting", "sketch"]
                            }
                        },
                        "required": ["prompt"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "synthesize_speech",
                    "description": "Convert text to speech",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Text to convert to speech"
                            },
                            "voice": {
                                "type": "string",
                                "description": "Voice to use",
                                "enum": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
                            }
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get current weather information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City and state, e.g. San Francisco, CA"
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
    
    def add_message(self, role: str, content: str, message_type: str = "text", 
                   metadata: Optional[Dict[str, Any]] = None):
        """Add a message to the conversation history."""
        message = AssistantMessage(
            role=role,
            content=content,
            timestamp=time.time(),
            message_type=message_type,
            metadata=metadata
        )
        self.conversation_history.append(message)
    
    def get_conversation_context(self) -> List[Dict[str, str]]:
        """Get conversation context for API calls."""
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in self.conversation_history[-10:]  # Last 10 messages
        ]
    
    def chat(self, user_input: str, model: str = "llama-3.3-70b", 
             use_functions: bool = True, **advanced_params) -> str:
        """Process a chat message and return response with advanced parameter support."""
        # Add user message
        self.add_message("user", user_input)
        
        try:
            # Prepare messages for API
            messages = self.get_conversation_context()
            
            # Add system message
            system_message = {
                "role": "system",
                "content": """You are a helpful AI assistant with access to various tools including:
                - Image generation
                - Text-to-speech synthesis
                - Weather information
                - Mathematical calculations
                - Web search
                
                Use these tools when appropriate to help users. Be helpful, accurate, and engaging."""
            }
            messages.insert(0, system_message)
            
            # Set default advanced parameters if not provided
            default_params = {
                "temperature": 0.7,
                "max_completion_tokens": 1000,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1
            }
            default_params.update(advanced_params)
            
            # Make API call
            if use_functions:
                response = self.client.chat.complete(
                    messages=messages,
                    model=model,
                    tools=self.functions,
                    **default_params
                )
            else:
                response = self.client.chat.complete(
                    messages=messages,
                    model=model,
                    **default_params
                )
            
            # Process response
            assistant_message = response.choices[0].message.content
            tool_calls = response.choices[0].message.tool_calls if hasattr(response.choices[0].message, 'tool_calls') else []
            
            # Handle tool calls
            if tool_calls:
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"🔧 Calling function: {function_name}")
                    result = self._execute_function(function_name, function_args)
                    
                    # Add function result to conversation
                    self.add_message(
                        "assistant",
                        f"Executed {function_name}: {result}",
                        "function_call",
                        {"function": function_name, "result": result}
                    )
            
            # Add assistant response
            self.add_message("assistant", assistant_message)
            
            return assistant_message
            
        except VeniceAPIError as e:
            error_msg = f"API Error: {e}"
            self.add_message("assistant", error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            self.add_message("assistant", error_msg)
            return error_msg
    
    def _execute_function(self, function_name: str, args: Dict[str, Any]) -> str:
        """Execute a function call."""
        try:
            if function_name == "generate_image":
                return self._generate_image(args)
            elif function_name == "synthesize_speech":
                return self._synthesize_speech(args)
            elif function_name == "get_weather":
                return self._get_weather(args)
            elif function_name == "calculate":
                return self._calculate(args)
            elif function_name == "search_web":
                return self._search_web(args)
            else:
                return f"Unknown function: {function_name}"
        except Exception as e:
            return f"Error executing {function_name}: {e}"
    
    def _generate_image(self, args: Dict[str, Any]) -> str:
        """Generate an image."""
        prompt = args.get("prompt", "")
        style = args.get("style", "realistic")
        
        if not prompt:
            return "Error: No prompt provided"
        
        # Enhance prompt with style
        enhanced_prompt = f"{prompt}, {style} style"
        
        try:
            result = self.client.images.generate(
                prompt=enhanced_prompt,
                model="dall-e-3",
                size="1024x1024"
            )
            
            # Save image
            filename = f"generated_image_{int(time.time())}.png"
            result.save(filename)
            
            return f"Generated image: {filename}"
        except Exception as e:
            return f"Image generation failed: {e}"
    
    def _synthesize_speech(self, args: Dict[str, Any]) -> str:
        """Synthesize speech."""
        text = args.get("text", "")
        voice = args.get("voice", "alloy")
        
        if not text:
            return "Error: No text provided"
        
        try:
            result = self.client.audio.speech(
                input_text=text,
                voice=voice,
                model="tts-kokoro"
            )
            
            # Save audio
            filename = f"speech_{int(time.time())}.mp3"
            result.save(filename)
            
            return f"Generated speech: {filename}"
        except Exception as e:
            return f"Speech synthesis failed: {e}"
    
    def _get_weather(self, args: Dict[str, Any]) -> str:
        """Get weather information (mock implementation)."""
        location = args.get("location", "")
        
        if not location:
            return "Error: No location provided"
        
        # Mock weather data
        weather_data = {
            "location": location,
            "temperature": "72°F",
            "condition": "Sunny",
            "humidity": "45%",
            "wind": "5 mph"
        }
        
        return f"Weather in {location}: {weather_data['temperature']}, {weather_data['condition']}"
    
    def _calculate(self, args: Dict[str, Any]) -> str:
        """Perform mathematical calculation."""
        expression = args.get("expression", "")
        
        if not expression:
            return "Error: No expression provided"
        
        try:
            # Simple evaluation (in production, use a safer method)
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Calculation error: {e}"
    
    def _search_web(self, args: Dict[str, Any]) -> str:
        """Search the web (mock implementation)."""
        query = args.get("query", "")
        
        if not query:
            return "Error: No query provided"
        
        # Mock search results
        return f"Search results for '{query}': [Mock results would appear here]"
    
    def stream_chat(self, user_input: str, model: str = "llama-3.3-70b") -> str:
        """Process a chat message with streaming response."""
        self.add_message("user", user_input)
        
        try:
            messages = self.get_conversation_context()
            messages.insert(0, {
                "role": "system",
                "content": "You are a helpful AI assistant. Be concise and engaging."
            })
            
            print("🤖 Assistant: ", end="", flush=True)
            response_content = ""
            
            for chunk in self.client.chat.complete_stream(
                messages=messages,
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
            
            print()  # New line after streaming
            self.add_message("assistant", response_content)
            return response_content
            
        except Exception as e:
            error_msg = f"Streaming error: {e}"
            self.add_message("assistant", error_msg)
            return error_msg
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the conversation."""
        total_messages = len(self.conversation_history)
        user_messages = len([m for m in self.conversation_history if m.role == "user"])
        assistant_messages = len([m for m in self.conversation_history if m.role == "assistant"])
        function_calls = len([m for m in self.conversation_history if m.message_type == "function_call"])
        
        return {
            "total_messages": total_messages,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "function_calls": function_calls,
            "conversation_duration": time.time() - self.conversation_history[0].timestamp if self.conversation_history else 0
        }
    
    def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation_history.clear()
        print("🗑️  Conversation cleared")


def interactive_demo():
    """Interactive demo of the AI Assistant."""
    print("🤖 Venice AI Assistant Demo")
    print("=" * 40)
    print("Type 'quit' to exit, 'clear' to clear conversation, 'help' for commands")
    print()
    
    assistant = AIAssistant()
    
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'clear':
                assistant.clear_conversation()
                continue
            elif user_input.lower() == 'help':
                print("""
Available commands:
- quit: Exit the assistant
- clear: Clear conversation history
- help: Show this help message
- stream: Toggle streaming mode
- summary: Show conversation summary

You can also ask the assistant to:
- Generate images: "Create an image of a sunset"
- Synthesize speech: "Say hello in a friendly voice"
- Get weather: "What's the weather in San Francisco?"
- Calculate: "What's 15 * 23 + 7?"
- Search: "Search for information about AI"
                """)
                continue
            elif user_input.lower() == 'summary':
                summary = assistant.get_conversation_summary()
                print(f"📊 Conversation Summary:")
                print(f"  Total messages: {summary['total_messages']}")
                print(f"  User messages: {summary['user_messages']}")
                print(f"  Assistant messages: {summary['assistant_messages']}")
                print(f"  Function calls: {summary['function_calls']}")
                print(f"  Duration: {summary['conversation_duration']:.1f} seconds")
                continue
            
            if not user_input:
                continue
            
            # Process the message
            response = assistant.chat(user_input)
            print(f"🤖 Assistant: {response}")
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"💥 Error: {e}")


def batch_demo():
    """Demo with predefined interactions."""
    print("🤖 Venice AI Assistant - Batch Demo")
    print("=" * 40)
    
    assistant = AIAssistant()
    
    # Predefined interactions
    interactions = [
        "Hello! I'm your AI assistant. What can you help me with?",
        "Can you generate an image of a cute robot?",
        "Please say 'Hello from Venice AI' in a friendly voice",
        "What's the weather like in Tokyo?",
        "Calculate 25 * 4 + 10",
        "Search for information about machine learning",
        "Thank you for your help!"
    ]
    
    for i, interaction in enumerate(interactions, 1):
        print(f"\n--- Interaction {i} ---")
        print(f"👤 User: {interaction}")
        
        response = assistant.chat(interaction)
        print(f"🤖 Assistant: {response}")
        
        # Small delay between interactions
        time.sleep(1)
    
    # Show final summary
    summary = assistant.get_conversation_summary()
    print(f"\n📊 Final Summary:")
    print(f"  Total interactions: {summary['total_messages']}")
    print(f"  Function calls made: {summary['function_calls']}")
    print(f"  Total duration: {summary['conversation_duration']:.1f} seconds")


def main():
    """Main function to run the AI Assistant demo."""
    print("🎯 Venice AI Assistant Examples")
    print("=" * 50)
    
    try:
        # Check for API key
        import os
        if not os.getenv("VENICE_API_KEY"):
            print("❌ Error: VENICE_API_KEY environment variable not set")
            print("Please set your API key: export VENICE_API_KEY='your-key-here'")
            return
        
        print("Choose demo mode:")
        print("1. Interactive demo")
        print("2. Batch demo")
        
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            interactive_demo()
        elif choice == "2":
            batch_demo()
        else:
            print("Invalid choice. Running interactive demo...")
            interactive_demo()
        
        print("\n🎉 Demo completed!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")


if __name__ == "__main__":
    main()
