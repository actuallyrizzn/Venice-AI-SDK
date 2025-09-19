"""
Venice AI SDK - Unified Client

This module provides a unified client interface for all Venice AI API endpoints.
"""

from __future__ import annotations

from typing import Optional

from .client import HTTPClient
from .config import Config, load_config
from .chat import ChatAPI
from .models import ModelsAPI
from .images import ImageAPI, ImageEditAPI, ImageUpscaleAPI, ImageStylesAPI
from .audio import AudioAPI
from .characters import CharactersAPI
from .account import APIKeysAPI, BillingAPI, AccountManager
from .models_advanced import ModelsTraitsAPI, ModelsCompatibilityAPI
from .embeddings import EmbeddingsAPI


class VeniceClient:
    """
    Unified client for all Venice AI API endpoints.
    
    This client provides access to all Venice AI services through a single interface.
    Each service is available as an attribute of the client.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the Venice client.
        
        Args:
            config: Optional configuration. If not provided, will be loaded from environment.
        """
        self.config = config or load_config()
        self._http_client = HTTPClient(self.config)
        
        # Initialize all API modules
        self.chat = ChatAPI(self._http_client)
        self.models = ModelsAPI(self._http_client)
        
        # Image processing suite
        self.images = ImageAPI(self._http_client)
        self.image_edit = ImageEditAPI(self._http_client)
        self.image_upscale = ImageUpscaleAPI(self._http_client)
        self.image_styles = ImageStylesAPI(self._http_client)
        
        # Audio services
        self.audio = AudioAPI(self._http_client)
        
        # Character management
        self.characters = CharactersAPI(self._http_client)
        
        # Account management
        self.api_keys = APIKeysAPI(self._http_client)
        self.billing = BillingAPI(self._http_client)
        
        # Advanced models
        self.models_traits = ModelsTraitsAPI(self._http_client)
        self.models_compatibility = ModelsCompatibilityAPI(self._http_client)
        
        # Embeddings
        self.embeddings = EmbeddingsAPI(self._http_client)
    
    @property
    def http_client(self) -> HTTPClient:
        """Get the underlying HTTP client."""
        return self._http_client
    
    def get_account_summary(self) -> dict:
        """
        Get a comprehensive account summary.
        
        Returns:
            Dictionary with account summary information
        """
        from .account import AccountManager
        manager = AccountManager(self.api_keys, self.billing)
        return manager.get_account_summary()
    
    def get_rate_limit_status(self) -> dict:
        """
        Get current rate limit status.
        
        Returns:
            Dictionary with rate limit status information
        """
        from .account import AccountManager
        manager = AccountManager(self.api_keys, self.billing)
        return manager.check_rate_limit_status()
    
    def clear_caches(self) -> None:
        """Clear all caches in the client."""
        if hasattr(self.models_traits, 'clear_cache'):
            self.models_traits.clear_cache()
        if hasattr(self.models_compatibility, 'clear_cache'):
            self.models_compatibility.clear_cache()
        if hasattr(self.characters, 'clear_cache'):
            self.characters.clear_cache()


# Convenience function for easy client creation
def create_client(api_key: Optional[str] = None, **kwargs) -> VeniceClient:
    """
    Create a Venice client with optional configuration.
    
    Args:
        api_key: Optional API key. If not provided, will be loaded from environment.
        **kwargs: Additional configuration parameters
        
    Returns:
        VeniceClient instance
    """
    if api_key:
        config = Config(api_key=api_key, **kwargs)
    else:
        config = load_config()
        # Update config with any additional kwargs
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
    
    return VeniceClient(config)
