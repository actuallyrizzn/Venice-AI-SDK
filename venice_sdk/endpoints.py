"""
API endpoint constants for the Venice SDK.

This module contains centralized endpoint definitions to ensure consistency
across the SDK and make endpoint management easier.
"""


class ImageEndpoints:
    """Image-related API endpoints."""
    
    GENERATIONS = "/images/generations"
    EDIT = "/images/edit"
    UPSCALE = "/images/upscale"
    STYLES = "/images/styles"


class ChatEndpoints:
    """Chat-related API endpoints."""
    
    COMPLETIONS = "chat/completions"


class AccountEndpoints:
    """Account-related API endpoints."""
    
    API_KEYS = "/api_keys"
    API_KEYS_GENERATE_WEB3 = "/api_keys/generate_web3_key"
    API_KEYS_RATE_LIMITS = "/api_keys/rate_limits"
    API_KEYS_RATE_LIMITS_LOG = "/api_keys/rate_limits/log"
    BILLING_USAGE = "/billing/usage"
    BILLING_SUMMARY = "/billing/summary"


class AudioEndpoints:
    """Audio-related API endpoints."""
    
    SPEECH = "/audio/speech"


class CharactersEndpoints:
    """Character-related API endpoints."""
    
    CHARACTERS = "/characters"


class EmbeddingsEndpoints:
    """Embedding-related API endpoints."""
    
    EMBEDDINGS = "/embeddings"


class ModelsEndpoints:
    """Model-related API endpoints."""
    
    MODELS = "models"
    MODELS_COMPATIBILITY_MAPPING = "/models/compatibility_mapping"


class VideoEndpoints:
    """Video-related API endpoints."""
    
    QUEUE = "/video/queue"
    RETRIEVE = "/video/retrieve"
    QUOTE = "/video/quote"
    COMPLETE = "/video/complete"