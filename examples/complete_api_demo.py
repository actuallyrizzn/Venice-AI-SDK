#!/usr/bin/env python3
"""
Complete Venice AI SDK Demo

This script demonstrates all the major features of the Venice AI SDK,
including chat completions, image generation, audio synthesis, character management,
account management, and embeddings.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import venice_sdk
sys.path.insert(0, str(Path(__file__).parent.parent))

from venice_sdk import (
    VeniceClient, create_client,
    # Image processing
    generate_image, edit_image, upscale_image,
    # Audio
    text_to_speech, text_to_speech_file,
    # Characters
    get_character, list_characters, search_characters,
    # Account management
    get_account_usage, get_rate_limits, list_api_keys,
    # Advanced models
    get_model_traits, get_compatibility_mapping, find_models_by_capability,
    # Embeddings
    generate_embedding, calculate_similarity, generate_embeddings,
    # Embedding utilities
    EmbeddingSimilarity, SemanticSearch
)


def demo_chat_completions(client: VeniceClient):
    """Demonstrate chat completions with different features."""
    print("=== Chat Completions Demo ===")
    
    # Basic chat completion
    print("\n1. Basic Chat Completion:")
    response = client.chat.complete(
        messages=[
            {"role": "user", "content": "Hello! Can you tell me about Venice AI?"}
        ],
        model="llama-3.3-70b"
    )
    print(f"Response: {response.choices[0].message.content}")
    
    # Chat with function calling
    print("\n2. Chat with Function Calling:")
    tools = [
        {
            "function": {
                "name": "get_weather",
                "description": "Get current weather for a city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "City name"},
                        "units": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                    },
                    "required": ["location"]
                }
            }
        }
    ]
    
    response = client.chat.complete(
        messages=[
            {"role": "user", "content": "What's the weather like in Paris?"}
        ],
        model="llama-3.3-70b",
        tools=tools
    )
    print(f"Response: {response.choices[0].message.content}")
    
    # Streaming chat
    print("\n3. Streaming Chat:")
    print("Response (streaming): ", end="", flush=True)
    for chunk in client.chat.complete(
        messages=[
            {"role": "user", "content": "Write a short poem about AI."}
        ],
        model="llama-3.3-70b",
        stream=True
    ):
        print(chunk.choices[0].message.content, end="", flush=True)
    print()


def demo_image_processing(client: VeniceClient):
    """Demonstrate image generation and processing."""
    print("\n=== Image Processing Demo ===")
    
    # Generate an image
    print("\n1. Image Generation:")
    try:
        image = client.images.generate(
            prompt="A serene mountain landscape at sunset with a lake in the foreground",
            model="dall-e-3",
            size="1024x1024"
        )
        print(f"Generated image: {image.url or 'Base64 data available'}")
        
        # Save the image
        if image.b64_json:
            image.save("generated_mountain.png")
            print("Image saved as 'generated_mountain.png'")
    except Exception as e:
        print(f"Image generation failed: {e}")
    
    # List available styles
    print("\n2. Available Image Styles:")
    try:
        styles = client.image_styles.list_styles()
        for style in styles[:3]:  # Show first 3 styles
            print(f"- {style.name}: {style.description}")
    except Exception as e:
        print(f"Failed to get styles: {e}")


def demo_audio_synthesis(client: VeniceClient):
    """Demonstrate text-to-speech capabilities."""
    print("\n=== Audio Synthesis Demo ===")
    
    # Generate speech
    print("\n1. Text-to-Speech:")
    try:
        audio_result = client.audio.speech(
            input_text="Hello! This is a test of the Venice AI text-to-speech system.",
            voice="alloy",
            response_format="mp3"
        )
        
        # Save to file
        audio_result.save("test_speech.mp3")
        print("Audio saved as 'test_speech.mp3'")
        
        # List available voices
        print("\n2. Available Voices:")
        voices = client.audio.get_voices()
        for voice in voices[:3]:  # Show first 3 voices
            print(f"- {voice.name}: {voice.description}")
            
    except Exception as e:
        print(f"Audio synthesis failed: {e}")


def demo_character_management(client: VeniceClient):
    """Demonstrate character management features."""
    print("\n=== Character Management Demo ===")
    
    # List characters
    print("\n1. Available Characters:")
    try:
        characters = client.characters.list()
        for char in characters[:3]:  # Show first 3 characters
            print(f"- {char.name} ({char.slug}): {char.description}")
    except Exception as e:
        print(f"Failed to list characters: {e}")
    
    # Search characters
    print("\n2. Character Search:")
    try:
        search_results = client.characters.search("assistant")
        for char in search_results[:2]:  # Show first 2 results
            print(f"- {char.name}: {char.description}")
    except Exception as e:
        print(f"Character search failed: {e}")


def demo_account_management(client: VeniceClient):
    """Demonstrate account management features."""
    print("\n=== Account Management Demo ===")
    
    # Get account summary
    print("\n1. Account Summary:")
    try:
        summary = client.get_account_summary()
        print(f"Usage: {summary.get('usage', {})}")
        print(f"Rate Limits: {summary.get('rate_limits', {})}")
        print(f"API Keys: {summary.get('api_keys', {})}")
    except Exception as e:
        print(f"Failed to get account summary: {e}")
    
    # Get rate limit status
    print("\n2. Rate Limit Status:")
    try:
        rate_status = client.get_rate_limit_status()
        print(f"Status: {rate_status.get('status', 'unknown')}")
        print(f"Current Usage: {rate_status.get('current_usage', {})}")
    except Exception as e:
        print(f"Failed to get rate limits: {e}")


def demo_advanced_models(client: VeniceClient):
    """Demonstrate advanced model features."""
    print("\n=== Advanced Models Demo ===")
    
    # Get model traits
    print("\n1. Model Traits:")
    try:
        traits = client.models_traits.get_traits()
        for model_id, model_traits in list(traits.items())[:2]:  # Show first 2 models
            print(f"- {model_id}:")
            print(f"  Capabilities: {list(model_traits.capabilities.keys())[:3]}...")
            print(f"  Supports function calling: {model_traits.supports_function_calling()}")
    except Exception as e:
        print(f"Failed to get model traits: {e}")
    
    # Get compatibility mapping
    print("\n2. Model Compatibility:")
    try:
        mapping = client.models_compatibility.get_mapping()
        openai_models = list(mapping.openai_to_venice.keys())[:3]
        print(f"OpenAI to Venice mapping (sample): {openai_models}")
    except Exception as e:
        print(f"Failed to get compatibility mapping: {e}")


def demo_embeddings(client: VeniceClient):
    """Demonstrate embedding capabilities."""
    print("\n=== Embeddings Demo ===")
    
    # Generate embeddings
    print("\n1. Generate Embeddings:")
    try:
        texts = [
            "The quick brown fox jumps over the lazy dog",
            "A fast brown fox leaps over a sleepy dog",
            "Machine learning is a subset of artificial intelligence"
        ]
        
        result = client.embeddings.generate(texts)
        print(f"Generated {len(result)} embeddings")
        print(f"Embedding dimension: {len(result[0])}")
        
        # Calculate similarity
        print("\n2. Text Similarity:")
        similarity = EmbeddingSimilarity.cosine_similarity(
            result[0].embedding,
            result[1].embedding
        )
        print(f"Similarity between texts 1 and 2: {similarity:.3f}")
        
        # Semantic search
        print("\n3. Semantic Search:")
        search = SemanticSearch(client.embeddings)
        search.add_documents(texts)
        
        results = search.search("fox and dog", top_k=2)
        for i, result in enumerate(results):
            print(f"Result {i+1}: {result['similarity']:.3f} - {result['document'][:50]}...")
            
    except Exception as e:
        print(f"Embeddings demo failed: {e}")


def main():
    """Run the complete demo."""
    print("Venice AI SDK - Complete API Demo")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv("VENICE_API_KEY")
    if not api_key:
        print("Please set the VENICE_API_KEY environment variable")
        return
    
    # Create client
    try:
        client = create_client(api_key=api_key)
        print("✓ Connected to Venice AI API")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        return
    
    # Run demos
    try:
        demo_chat_completions(client)
        demo_image_processing(client)
        demo_audio_synthesis(client)
        demo_character_management(client)
        demo_account_management(client)
        demo_advanced_models(client)
        demo_embeddings(client)
        
        print("\n" + "=" * 50)
        print("✓ Demo completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
