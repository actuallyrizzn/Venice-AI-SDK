"""
Test utilities for live tests.
Provides helper functions to get available models and other dynamic test data.
"""

import os
from typing import List, Dict, Any, Optional
from venice_sdk.client import HTTPClient
from venice_sdk.config import Config


class LiveTestUtils:
    """Utilities for live tests."""
    
    _cached_models: Optional[List[Dict[str, Any]]] = None
    _cached_text_models: Optional[List[str]] = None
    _cached_embedding_models: Optional[List[str]] = None
    
    @classmethod
    def get_client(cls) -> HTTPClient:
        """Get a configured HTTP client for live tests."""
        api_key = os.getenv("VENICE_API_KEY")
        if not api_key:
            raise ValueError("VENICE_API_KEY environment variable not set")
        
        config = Config(api_key=api_key)
        return HTTPClient(config)
    
    @classmethod
    def get_available_models(cls) -> List[Dict[str, Any]]:
        """Get all available models from the API."""
        if cls._cached_models is None:
            client = cls.get_client()
            response = client.get("models")
            models_data = response.json()
            
            if "data" in models_data:
                cls._cached_models = models_data["data"]
            else:
                cls._cached_models = []
        
        return cls._cached_models
    
    @classmethod
    def get_text_models(cls) -> List[str]:
        """Get available text models."""
        if cls._cached_text_models is None:
            models = cls.get_available_models()
            cls._cached_text_models = [
                model["id"] for model in models 
                if model.get("type") == "text"
            ]
        
        return cls._cached_text_models
    
    @classmethod
    def get_embedding_models(cls) -> List[str]:
        """Get available embedding models."""
        if cls._cached_embedding_models is None:
            # Check if we have any embedding models in the models list
            models = cls.get_available_models()
            embedding_models = [
                model["id"] for model in models 
                if model.get("type") == "embedding"
            ]
            
            # If no embedding models found in the models list, check known working models
            if not embedding_models:
                # Test known embedding models
                known_embedding_models = ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"]
                client = cls.get_client()
                
                for model in known_embedding_models:
                    try:
                        response = client.post('embeddings', data={
                            'input': 'test',
                            'model': model
                        })
                        if response.status_code == 200:
                            embedding_models.append(model)
                    except:
                        pass  # Model doesn't work for embeddings
            
            cls._cached_embedding_models = embedding_models
        
        return cls._cached_embedding_models
    
    @classmethod
    def get_default_text_model(cls) -> str:
        """Get a default text model for testing."""
        text_models = cls.get_text_models()
        if not text_models:
            raise ValueError("No text models available")
        
        # Prefer smaller/faster models for testing
        preferred_models = ["qwen3-4b", "llama-3.2-3b", "venice-uncensored"]
        for preferred in preferred_models:
            if preferred in text_models:
                return preferred
        
        return text_models[0]
    
    @classmethod
    def get_default_embedding_model(cls) -> Optional[str]:
        """Get a default embedding model for testing."""
        embedding_models = cls.get_embedding_models()
        if not embedding_models:
            return None
        return embedding_models[0]
    
    @classmethod
    def clear_cache(cls):
        """Clear cached model data."""
        cls._cached_models = None
        cls._cached_text_models = None
        cls._cached_embedding_models = None
