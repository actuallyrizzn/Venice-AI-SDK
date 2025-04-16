"""
Live test for model discovery and validation functionality.
This test demonstrates how to list and validate models using the Venice API.
"""

from venice_sdk.models import get_models, get_model_by_id, get_text_models
from venice_sdk.client import HTTPClient
from venice_sdk.config import load_config
import json


def test_list_models():
    """Test listing all available models."""
    config = load_config()
    client = HTTPClient(config)
    
    print("\nGetting raw API response:")
    response = client.get("models")
    print(json.dumps(response.json(), indent=2))
    
    print("\nListing all available models:")
    models = get_models(client)
    
    for model in models:
        print(f"\nModel: {model.name} (ID: {model.id})")
        print(f"Type: {model.type}")
        print(f"Description: {model.description}")
        print("Capabilities:")
        print(f"  - Function Calling: {model.capabilities.supports_function_calling}")
        print(f"  - Web Search: {model.capabilities.supports_web_search}")
        print(f"  - Context Tokens: {model.capabilities.available_context_tokens}")


def test_get_specific_model():
    """Test retrieving a specific model by ID."""
    config = load_config()
    client = HTTPClient(config)
    
    # Get a list of models first to find a valid ID
    models = get_models(client)
    if not models:
        print("No models available to test with")
        return
    
    model_id = models[0].id
    print(f"\nGetting details for model: {model_id}")
    
    model = get_model_by_id(model_id, client)
    print(f"Model details:")
    print(f"Name: {model.name}")
    print(f"Type: {model.type}")
    print(f"Description: {model.description}")


def test_list_text_models():
    """Test listing only text models."""
    config = load_config()
    client = HTTPClient(config)
    
    print("\nListing text models only:")
    text_models = get_text_models(client)
    
    for model in text_models:
        print(f"\nText Model: {model.name} (ID: {model.id})")
        print(f"Description: {model.description}")


if __name__ == "__main__":
    print("Running live model tests...")
    test_list_models()
    test_get_specific_model()
    test_list_text_models() 