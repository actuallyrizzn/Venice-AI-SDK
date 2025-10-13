#!/usr/bin/env python3
"""
Venice AI SDK - Quick Start Example

This example shows how to get started with the Venice AI SDK quickly.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import venice_sdk
sys.path.insert(0, str(Path(__file__).parent.parent))

from venice_sdk import VeniceClient, create_client


def main():
    """Quick start example."""
    print("Venice AI SDK - Quick Start")
    print("=" * 30)
    
    # Method 1: Using environment variable
    print("\n1. Using environment variable (VENICE_API_KEY):")
    try:
        client = VeniceClient()  # Will load from VENICE_API_KEY env var
        print("[OK] Client created successfully")
    except Exception as e:
        print(f"[ERROR] Failed: {e}")
        print("Make sure to set VENICE_API_KEY environment variable")
        return
    
    # Method 2: Using explicit API key
    print("\n2. Using explicit API key:")
    api_key = os.getenv("VENICE_API_KEY")
    if api_key:
        try:
            client = create_client(api_key=api_key)
            print("[OK] Client created with explicit API key")
        except Exception as e:
            print(f"[ERROR] Failed: {e}")
            return
    else:
        print("No API key available for explicit creation")
        return
    
    # Basic chat completion
    print("\n3. Basic Chat Completion:")
    try:
        response = client.chat.complete(
            messages=[
                {"role": "user", "content": "Hello! What can you help me with?"}
            ],
            model="llama-3.3-70b"
        )
        print(f"AI Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"Chat completion failed: {e}")
    
    # List available models
    print("\n4. Available Models:")
    try:
        models = client.models.list()
        print(f"Found {len(models)} models")
        for model in models[:3]:  # Show first 3 models
            print(f"- {model.id}: {model.type}")
    except Exception as e:
        print(f"Failed to list models: {e}")
    
    # Get account info
    print("\n5. Account Information:")
    try:
        summary = client.get_account_summary()
        print(f"Account Summary: {summary}")
    except Exception as e:
        print(f"Failed to get account info: {e}")
    
    print("\n[OK] Quick start completed!")


if __name__ == "__main__":
    main()
