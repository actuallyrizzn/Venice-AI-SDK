"""
Venice AI SDK - Unified Client

This module provides a unified client interface for all Venice AI API endpoints.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from .client import HTTPClient
from .config import Config, load_config
from .chat import ChatAPI
from .models import ModelsAPI
from .images import ImageAPI, ImageEditAPI, ImageUpscaleAPI, ImageStylesAPI
from .audio import AudioAPI
from .video import VideoAPI
from .characters import CharactersAPI
from .account import APIKeysAPI, BillingAPI, AccountManager
from .models_advanced import ModelsTraitsAPI, ModelsCompatibilityAPI
from .embeddings import EmbeddingsAPI

logger = logging.getLogger(__name__)


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
        logger.info(
            "Initialized VeniceClient (base_url=%s, timeout=%ss, retries=%s)",
            self.config.base_url,
            self.config.timeout,
            self.config.max_retries,
        )
        
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
        
        # Video generation
        self.video = VideoAPI(self._http_client)
        
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
    
    def get_account_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive account summary.
        
        Returns:
            Dictionary with account summary information
        """
        manager = AccountManager(self.api_keys, self.billing)
        return manager.get_account_summary()
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get current rate limit status.
        
        Returns:
            Dictionary with rate limit status information
        """
        manager = AccountManager(self.api_keys, self.billing)
        return manager.check_rate_limit_status()
    
    def get_rate_limit_metrics(self) -> Optional[Dict[str, Any]]:
        """
        Get rate limiting metrics and analytics.
        
        Returns:
            Dictionary with rate limit metrics summary, or None if metrics are disabled
        """
        if self._http_client.metrics is None:
            return None
        return self._http_client.metrics.get_rate_limit_summary()
    
    def get_rate_limit_events(self, endpoint: Optional[str] = None) -> Optional[list]:
        """
        Get rate limit events, optionally filtered by endpoint.
        
        Args:
            endpoint: Optional endpoint to filter by
            
        Returns:
            List of rate limit events, or None if metrics are disabled
        """
        if self._http_client.metrics is None:
            return None
        events = self._http_client.metrics.get_rate_limit_events(endpoint)
        return [
            {
                "timestamp": event.timestamp.isoformat(),
                "endpoint": event.endpoint,
                "status_code": event.status_code,
                "retry_after": event.retry_after,
                "request_count": event.request_count,
                "remaining_requests": event.remaining_requests,
                "method": event.method
            }
            for event in events
        ]
    
    def get_endpoint_metrics(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """
        Get metrics for a specific endpoint.
        
        Args:
            endpoint: Endpoint to get metrics for
            
        Returns:
            Dictionary with endpoint metrics, or None if metrics are disabled or endpoint not found
        """
        if self._http_client.metrics is None:
            return None
        return self._http_client.metrics.get_endpoint_summary(endpoint)
    
    def clear_caches(self) -> None:
        """Clear all caches in the client."""
        logger.debug("Clearing VeniceClient caches")
        if hasattr(self.models_traits, 'clear_cache'):
            self.models_traits.clear_cache()
        if hasattr(self.models_compatibility, 'clear_cache'):
            self.models_compatibility.clear_cache()
        if hasattr(self.characters, 'clear_cache'):
            self.characters.clear_cache()


# Convenience function for easy client creation
def create_client(api_key: Optional[str] = None, **kwargs: Any) -> VeniceClient:
    """
    Create a Venice client with optional configuration.
    
    Args:
        api_key: Optional API key. If not provided, will be loaded from environment.
        **kwargs: Additional configuration parameters
        
    Returns:
        VeniceClient instance
    """
    if api_key:
        logger.debug("Creating VeniceClient with explicit API key")
        config = Config(api_key=api_key, **kwargs)
    else:
        logger.debug("Creating VeniceClient from environment configuration")
        config = load_config()
        # Update config with any additional kwargs
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
    
    return VeniceClient(config)
