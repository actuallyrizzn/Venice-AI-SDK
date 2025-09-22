#!/usr/bin/env python3
"""
Advanced Parameters Example

This example demonstrates all the advanced parameters available in the Venice AI SDK
for chat completions, including the new parameters from the Swagger specification.
"""

import json
from typing import List, Dict, Any
from venice_sdk import VeniceClient
from venice_sdk.errors import VeniceAPIError


def demonstrate_basic_parameters():
    """Demonstrate basic parameter usage."""
    print("🔧 Basic Parameters")
    print("=" * 30)
    
    client = VeniceClient()
    
    messages = [
        {"role": "user", "content": "Write a short poem about technology."}
    ]
    
    try:
        response = client.chat.complete(
            messages=messages,
            model="llama-3.3-70b",
            temperature=0.8,
            max_completion_tokens=200
        )
        
        print("✅ Basic parameters work!")
        print(f"Response: {response['choices'][0]['message']['content'][:100]}...")
        
    except VeniceAPIError as e:
        print(f"❌ Error: {e}")


def demonstrate_penalty_parameters():
    """Demonstrate frequency and presence penalty parameters."""
    print("\n🎯 Penalty Parameters")
    print("=" * 30)
    
    client = VeniceClient()
    
    messages = [
        {"role": "user", "content": "Write a creative story about a robot learning to paint."}
    ]
    
    try:
        # With penalties to reduce repetition
        response = client.chat.complete(
            messages=messages,
            model="llama-3.3-70b",
            temperature=1.2,
            frequency_penalty=0.5,  # Reduce repetition
            presence_penalty=0.3,   # Encourage new topics
            repetition_penalty=1.2, # Additional repetition control
            max_completion_tokens=300
        )
        
        print("✅ Penalty parameters work!")
        print(f"Response: {response['choices'][0]['message']['content'][:100]}...")
        
    except VeniceAPIError as e:
        print(f"❌ Error: {e}")


def demonstrate_dynamic_temperature():
    """Demonstrate dynamic temperature scaling."""
    print("\n🌡️ Dynamic Temperature Scaling")
    print("=" * 30)
    
    client = VeniceClient()
    
    messages = [
        {"role": "user", "content": "Write a creative poem about the ocean."}
    ]
    
    try:
        response = client.chat.complete(
            messages=messages,
            model="llama-3.3-70b",
            min_temp=0.5,  # Minimum temperature
            max_temp=1.5,  # Maximum temperature
            max_completion_tokens=250
        )
        
        print("✅ Dynamic temperature scaling works!")
        print(f"Response: {response['choices'][0]['message']['content'][:100]}...")
        
    except VeniceAPIError as e:
        print(f"❌ Error: {e}")


def demonstrate_multiple_choices():
    """Demonstrate generating multiple response choices."""
    print("\n🎲 Multiple Choices")
    print("=" * 30)
    
    client = VeniceClient()
    
    messages = [
        {"role": "user", "content": "What are three different ways to solve a problem?"}
    ]
    
    try:
        response = client.chat.complete(
            messages=messages,
            model="llama-3.3-70b",
            n=3,  # Generate 3 different responses
            temperature=0.9,
            max_completion_tokens=200
        )
        
        print("✅ Multiple choices work!")
        for i, choice in enumerate(response['choices'], 1):
            print(f"Choice {i}: {choice['message']['content'][:80]}...")
        
    except VeniceAPIError as e:
        print(f"❌ Error: {e}")


def demonstrate_stop_sequences():
    """Demonstrate stop sequences."""
    print("\n🛑 Stop Sequences")
    print("=" * 30)
    
    client = VeniceClient()
    
    messages = [
        {"role": "user", "content": "Count from 1 to 10, then explain why counting is important."}
    ]
    
    try:
        response = client.chat.complete(
            messages=messages,
            model="llama-3.3-70b",
            stop=["5", "6"],  # Stop when reaching 5 or 6
            max_completion_tokens=100
        )
        
        print("✅ Stop sequences work!")
        print(f"Response: {response['choices'][0]['message']['content']}")
        
    except VeniceAPIError as e:
        print(f"❌ Error: {e}")


def demonstrate_logprobs():
    """Demonstrate log probabilities."""
    print("\n📊 Log Probabilities")
    print("=" * 30)
    
    client = VeniceClient()
    
    messages = [
        {"role": "user", "content": "What is the capital of France?"}
    ]
    
    try:
        response = client.chat.complete(
            messages=messages,
            model="llama-3.3-70b",
            logprobs=True,
            top_logprobs=3,  # Top 3 log probabilities
            max_completion_tokens=50
        )
        
        print("✅ Log probabilities work!")
        print(f"Response: {response['choices'][0]['message']['content']}")
        
        # Check if logprobs are in the response
        if 'logprobs' in response['choices'][0]:
            print("✅ Log probabilities included in response!")
        
    except VeniceAPIError as e:
        print(f"❌ Error: {e}")


def demonstrate_seed_reproducibility():
    """Demonstrate seed for reproducible responses."""
    print("\n🎲 Seed Reproducibility")
    print("=" * 30)
    
    client = VeniceClient()
    
    messages = [
        {"role": "user", "content": "Tell me a random story."}
    ]
    
    try:
        # First response with seed
        response1 = client.chat.complete(
            messages=messages,
            model="llama-3.3-70b",
            seed=42,
            temperature=0.8,
            max_completion_tokens=100
        )
        
        # Second response with same seed
        response2 = client.chat.complete(
            messages=messages,
            model="llama-3.3-70b",
            seed=42,
            temperature=0.8,
            max_completion_tokens=100
        )
        
        print("✅ Seed reproducibility works!")
        print(f"Response 1: {response1['choices'][0]['message']['content'][:50]}...")
        print(f"Response 2: {response2['choices'][0]['message']['content'][:50]}...")
        
        # Check if responses are identical (they should be with same seed)
        if response1['choices'][0]['message']['content'] == response2['choices'][0]['message']['content']:
            print("✅ Responses are identical (reproducible)!")
        else:
            print("⚠️ Responses differ (may be due to model behavior)")
        
    except VeniceAPIError as e:
        print(f"❌ Error: {e}")


def demonstrate_streaming_options():
    """Demonstrate streaming with options."""
    print("\n🌊 Streaming with Options")
    print("=" * 30)
    
    client = VeniceClient()
    
    messages = [
        {"role": "user", "content": "Explain quantum computing in simple terms."}
    ]
    
    try:
        print("Streaming response: ", end="", flush=True)
        
        for chunk in client.chat.complete_stream(
            messages=messages,
            model="llama-3.3-70b",
            temperature=0.7,
            max_completion_tokens=200,
            stream_options={"include_usage": True}
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
                except json.JSONDecodeError:
                    continue
        
        print("\n✅ Streaming with options works!")
        
    except VeniceAPIError as e:
        print(f"❌ Error: {e}")


def demonstrate_all_parameters():
    """Demonstrate all parameters together."""
    print("\n🚀 All Parameters Together")
    print("=" * 30)
    
    client = VeniceClient()
    
    messages = [
        {"role": "user", "content": "Write a creative story about a time traveler."}
    ]
    
    try:
        response = client.chat.complete(
            messages=messages,
            model="llama-3.3-70b",
            # Basic parameters
            temperature=1.0,
            max_completion_tokens=300,
            # Penalty parameters
            frequency_penalty=0.2,
            presence_penalty=0.1,
            repetition_penalty=1.1,
            # Dynamic temperature
            min_temp=0.3,
            max_temp=1.2,
            # Multiple choices
            n=2,
            # Log probabilities
            logprobs=True,
            top_logprobs=2,
            # Seed for reproducibility
            seed=123,
            # Stop sequences
            stop=["THE END", "FINISHED"]
        )
        
        print("✅ All parameters work together!")
        print(f"Generated {len(response['choices'])} choices")
        for i, choice in enumerate(response['choices'], 1):
            print(f"Choice {i}: {choice['message']['content'][:80]}...")
        
    except VeniceAPIError as e:
        print(f"❌ Error: {e}")


def main():
    """Run all demonstrations."""
    print("🎯 Venice AI SDK - Advanced Parameters Demo")
    print("=" * 50)
    
    try:
        demonstrate_basic_parameters()
        demonstrate_penalty_parameters()
        demonstrate_dynamic_temperature()
        demonstrate_multiple_choices()
        demonstrate_stop_sequences()
        demonstrate_logprobs()
        demonstrate_seed_reproducibility()
        demonstrate_streaming_options()
        demonstrate_all_parameters()
        
        print("\n🎉 All demonstrations completed!")
        print("\nFor more information about these parameters, see:")
        print("- API Documentation: docs/api/chat.md")
        print("- README: README.md")
        print("- Tutorials: examples/tutorials/")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
