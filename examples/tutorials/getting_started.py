#!/usr/bin/env python3
"""
Getting Started Tutorial

This tutorial walks you through the basics of using the Venice AI SDK.
It covers installation, authentication, and your first API calls.
"""

import os
import time
from venice_sdk import VeniceClient, create_client
from venice_sdk.errors import VeniceAPIError, UnauthorizedError


def step_1_installation():
    """Step 1: Installation and Setup"""
    print("🚀 Step 1: Installation and Setup")
    print("=" * 40)
    
    print("""
To install the Venice AI SDK, run:

    pip install venice-sdk

Or for development with all dependencies:

    pip install venice-sdk[dev]

The SDK requires Python 3.8 or higher.
    """)
    
    # Check if SDK is installed
    try:
        import venice_sdk
        print(f"✅ Venice SDK is installed (version: {venice_sdk.__version__})")
    except ImportError:
        print("❌ Venice SDK is not installed. Please run: pip install venice-sdk")
        return False
    
    return True


def step_2_authentication():
    """Step 2: Authentication Setup"""
    print("\n🔑 Step 2: Authentication Setup")
    print("=" * 40)
    
    print("""
The Venice AI SDK supports multiple authentication methods:

1. Environment Variable (Recommended):
   export VENICE_API_KEY="your-api-key-here"

2. .env File:
   Create a .env file in your project root:
   VENICE_API_KEY=your-api-key-here

3. Direct Initialization:
   client = VeniceClient(api_key="your-api-key-here")
    """)
    
    # Check for API key
    api_key = os.getenv("VENICE_API_KEY")
    if api_key:
        print(f"✅ API key found in environment: {api_key[:8]}...")
        return True
    else:
        print("❌ No API key found. Please set VENICE_API_KEY environment variable.")
        print("   You can get an API key from: https://venice.ai")
        return False


def step_3_basic_client():
    """Step 3: Basic Client Initialization"""
    print("\n🤖 Step 3: Basic Client Initialization")
    print("=" * 40)
    
    try:
        # Method 1: Default client (uses environment variables)
        client = VeniceClient()
        print("✅ Client initialized with environment variables")
        
        # Method 2: Explicit API key
        api_key = os.getenv("VENICE_API_KEY")
        if api_key:
            client2 = create_client(api_key=api_key)
            print("✅ Client initialized with explicit API key")
        
        # Method 3: Custom configuration
        from venice_sdk.config import Config
        config = Config(api_key=api_key, timeout=30)
        client3 = VeniceClient(config)
        print("✅ Client initialized with custom configuration")
        
        return client
        
    except Exception as e:
        print(f"❌ Error initializing client: {e}")
        return None


def step_4_first_chat():
    """Step 4: Your First Chat Completion"""
    print("\n💬 Step 4: Your First Chat Completion")
    print("=" * 40)
    
    client = VeniceClient()
    
    try:
        print("Sending your first message...")
        
        response = client.chat.complete(
            messages=[
                {"role": "user", "content": "Hello! Can you tell me a short joke?"}
            ],
            model="llama-3.3-70b",
            max_tokens=100
        )
        
        print("✅ Chat completion successful!")
        print(f"Response: {response.choices[0].message.content}")
        
        return True
        
    except UnauthorizedError:
        print("❌ Authentication failed. Please check your API key.")
        return False
    except VeniceAPIError as e:
        print(f"❌ API error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def step_5_image_generation():
    """Step 5: Image Generation"""
    print("\n🎨 Step 5: Image Generation")
    print("=" * 40)
    
    client = VeniceClient()
    
    try:
        print("Generating your first image...")
        
        result = client.images.generate(
            prompt="A cute robot reading a book",
            model="dall-e-3",
            size="1024x1024"
        )
        
        print("✅ Image generation successful!")
        
        # Save the image
        output_path = "tutorial_robot.png"
        result.save(output_path)
        print(f"Image saved to: {output_path}")
        
        return True
        
    except VeniceAPIError as e:
        print(f"❌ API error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def step_6_audio_synthesis():
    """Step 6: Text-to-Speech"""
    print("\n🎵 Step 6: Text-to-Speech")
    print("=" * 40)
    
    client = VeniceClient()
    
    try:
        print("Converting text to speech...")
        
        audio = client.audio.speech(
            input_text="Hello from Venice AI! This is a test of text-to-speech.",
            voice="alloy",
            response_format="mp3"
        )
        
        print("✅ Audio synthesis successful!")
        
        # Save the audio
        output_path = "tutorial_audio.mp3"
        audio.save(output_path)
        print(f"Audio saved to: {output_path}")
        
        return True
        
    except VeniceAPIError as e:
        print(f"❌ API error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def step_7_embeddings():
    """Step 7: Text Embeddings"""
    print("\n🔗 Step 7: Text Embeddings")
    print("=" * 40)
    
    client = VeniceClient()
    
    try:
        print("Generating embeddings...")
        
        texts = [
            "The quick brown fox jumps over the lazy dog",
            "A fast brown fox leaps over a sleepy dog"
        ]
        
        embeddings = client.embeddings.generate(texts)
        
        print("✅ Embeddings generated successfully!")
        print(f"Number of embeddings: {len(embeddings)}")
        print(f"Embedding dimension: {len(embeddings[0])}")
        
        # Calculate similarity
        similarity = embeddings[0].cosine_similarity(embeddings[1])
        print(f"Similarity between texts: {similarity:.3f}")
        
        return True
        
    except VeniceAPIError as e:
        print(f"❌ API error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def step_8_streaming():
    """Step 8: Streaming Responses"""
    print("\n🌊 Step 8: Streaming Responses")
    print("=" * 40)
    
    client = VeniceClient()
    
    try:
        print("Streaming a response...")
        
        messages = [
            {"role": "user", "content": "Tell me a short story about a space explorer."}
        ]
        
        print("Response: ", end="", flush=True)
        
        for chunk in client.chat.complete_stream(
            messages=messages,
            model="llama-3.3-70b",
            max_tokens=200
        ):
            if chunk.startswith("data: "):
                data_content = chunk[6:].strip()
                if data_content == "[DONE]":
                    break
                
                try:
                    import json
                    data = json.loads(data_content)
                    if "choices" in data and data["choices"]:
                        delta = data["choices"][0].get("delta", {})
                        if "content" in delta:
                            print(delta["content"], end="", flush=True)
                except json.JSONDecodeError:
                    pass
        
        print("\n✅ Streaming completed!")
        return True
        
    except VeniceAPIError as e:
        print(f"❌ API error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def step_9_error_handling():
    """Step 9: Error Handling"""
    print("\n🛡️ Step 9: Error Handling")
    print("=" * 40)
    
    client = VeniceClient()
    
    print("Demonstrating error handling...")
    
    # Test with invalid model
    try:
        response = client.chat.complete(
            messages=[{"role": "user", "content": "Hello"}],
            model="invalid-model"
        )
    except VeniceAPIError as e:
        print(f"✅ Caught expected error: {e}")
    
    # Test with invalid parameters
    try:
        response = client.chat.complete(
            messages=[],  # Empty messages
            model="llama-3.3-70b"
        )
    except ValueError as e:
        print(f"✅ Caught validation error: {e}")
    
    print("✅ Error handling demonstration complete!")


def step_10_next_steps():
    """Step 10: Next Steps"""
    print("\n🎯 Step 10: Next Steps")
    print("=" * 40)
    
    print("""
Congratulations! You've completed the getting started tutorial.

Next steps:

1. 📚 Explore the Documentation:
   - API Reference: docs/api/
   - Advanced Guides: docs/advanced/
   - Examples: examples/

2. 🚀 Try Advanced Features:
   - Function calling
   - Batch processing
   - Custom models
   - Account management

3. 🔧 Integration Examples:
   - Web applications
   - Mobile apps
   - Data processing pipelines
   - AI assistants

4. 🤝 Get Help:
   - GitHub Issues: https://github.com/venice-ai/venice-sdk/issues
   - Documentation: https://docs.venice.ai
   - Discord: https://discord.gg/venice-ai

5. 📖 Learn More:
   - Check out the examples/ directory
   - Read the advanced guides
   - Explore the API reference

Happy coding with Venice AI! 🎉
    """)


def run_tutorial():
    """Run the complete getting started tutorial."""
    print("🎓 Venice AI SDK - Getting Started Tutorial")
    print("=" * 50)
    
    steps = [
        ("Installation", step_1_installation),
        ("Authentication", step_2_authentication),
        ("Client Setup", step_3_basic_client),
        ("First Chat", step_4_first_chat),
        ("Image Generation", step_5_image_generation),
        ("Audio Synthesis", step_6_audio_synthesis),
        ("Embeddings", step_7_embeddings),
        ("Streaming", step_8_streaming),
        ("Error Handling", step_9_error_handling),
        ("Next Steps", step_10_next_steps)
    ]
    
    completed_steps = 0
    
    for step_name, step_func in steps:
        try:
            print(f"\n{'='*60}")
            print(f"Step {completed_steps + 1}: {step_name}")
            print('='*60)
            
            result = step_func()
            if result is not False:  # None or True both count as success
                completed_steps += 1
                print(f"✅ {step_name} completed!")
            else:
                print(f"❌ {step_name} failed!")
                break
                
        except KeyboardInterrupt:
            print(f"\n\n⏹️  Tutorial interrupted by user")
            break
        except Exception as e:
            print(f"💥 Unexpected error in {step_name}: {e}")
            break
    
    print(f"\n🎉 Tutorial completed! {completed_steps}/{len(steps)} steps successful.")
    
    if completed_steps == len(steps):
        print("🎊 Perfect! You're ready to build amazing AI applications!")
    else:
        print("🔧 Some steps failed. Please check the errors above and try again.")


if __name__ == "__main__":
    run_tutorial()
