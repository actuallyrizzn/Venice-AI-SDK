"""
Unit tests for the endpoints module.
"""

import pytest
from venice_sdk.endpoints import (
    ImageEndpoints,
    ChatEndpoints,
    AccountEndpoints,
    AudioEndpoints,
    CharactersEndpoints,
    EmbeddingsEndpoints,
    ModelsEndpoints
)


class TestImageEndpoints:
    """Test ImageEndpoints constants."""
    
    def test_image_endpoints_constants(self):
        """Test that all image endpoint constants are defined correctly."""
        assert ImageEndpoints.GENERATIONS == "/images/generations"
        assert ImageEndpoints.EDIT == "/images/edit"
        assert ImageEndpoints.UPSCALE == "/images/upscale"
        assert ImageEndpoints.STYLES == "/images/styles"
    
    def test_image_endpoints_consistency(self):
        """Test that all image endpoints use consistent /images/ prefix."""
        endpoints = [
            ImageEndpoints.GENERATIONS,
            ImageEndpoints.EDIT,
            ImageEndpoints.UPSCALE,
            ImageEndpoints.STYLES
        ]
        
        for endpoint in endpoints:
            assert endpoint.startswith("/images/"), f"Endpoint {endpoint} should start with /images/"


class TestOtherEndpoints:
    """Test other endpoint constants."""
    
    def test_chat_endpoints(self):
        """Test chat endpoint constants."""
        assert ChatEndpoints.COMPLETIONS == "chat/completions"
    
    def test_account_endpoints(self):
        """Test account endpoint constants."""
        assert AccountEndpoints.API_KEYS == "/api_keys"
        assert AccountEndpoints.API_KEYS_GENERATE_WEB3 == "/api_keys/generate_web3_key"
        assert AccountEndpoints.API_KEYS_RATE_LIMITS == "/api_keys/rate_limits"
        assert AccountEndpoints.API_KEYS_RATE_LIMITS_LOG == "/api_keys/rate_limits/log"
        assert AccountEndpoints.BILLING_USAGE == "/billing/usage"
        assert AccountEndpoints.BILLING_SUMMARY == "/billing/summary"
    
    def test_audio_endpoints(self):
        """Test audio endpoint constants."""
        assert AudioEndpoints.SPEECH == "/audio/speech"
    
    def test_characters_endpoints(self):
        """Test characters endpoint constants."""
        assert CharactersEndpoints.CHARACTERS == "/characters"
    
    def test_embeddings_endpoints(self):
        """Test embeddings endpoint constants."""
        assert EmbeddingsEndpoints.EMBEDDINGS == "/embeddings"
    
    def test_models_endpoints(self):
        """Test models endpoint constants."""
        assert ModelsEndpoints.MODELS == "models"
        assert ModelsEndpoints.MODELS_COMPATIBILITY_MAPPING == "/models/compatibility_mapping"
