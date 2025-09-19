#!/usr/bin/env python3
"""
Script to get available models from the Venice AI API.
This helps us understand what models are actually available for testing.
"""

import os
import sys
from venice_sdk.client import HTTPClient
from venice_sdk.config import Config

def get_available_models():
    """Get available models from the API."""
    api_key = os.getenv("VENICE_API_KEY")
    if not api_key:
        print("Error: VENICE_API_KEY environment variable not set")
        return
    
    config = Config(api_key=api_key)
    client = HTTPClient(config)
    
    try:
        response = client.get("models")
        models = response.json()
        
        print("Available models:")
        print("=" * 50)
        
        if "data" in models:
            for model in models["data"]:
                model_id = model.get("id", "unknown")
                model_name = model.get("model_spec", {}).get("name", "unknown")
                model_type = model.get("type", "unknown")
                print(f"ID: {model_id}")
                print(f"Name: {model_name}")
                print(f"Type: {model_type}")
                print("-" * 30)
        else:
            print("No models found in response")
            print("Response:", models)
            
    except Exception as e:
        print(f"Error getting models: {e}")

if __name__ == "__main__":
    get_available_models()
