"""
Configuration management for the Venice SDK.
"""

import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration class for the Venice SDK."""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        retry_delay: Optional[int] = None
    ):
        """
        Initialize the configuration.

        Args:
            api_key: API key for authentication
            base_url: Optional base URL for the API
            default_model: Optional default model to use
            timeout: Optional request timeout in seconds
            max_retries: Optional maximum number of retries
            retry_delay: Optional delay between retries in seconds

        Raises:
            ValueError: If api_key is not provided
        """
        if not api_key or not api_key.strip():
            raise ValueError("API key must be provided")

        self.api_key = api_key
        self.base_url = base_url if base_url is not None and base_url.strip() else "https://api.venice.ai/api/v1"
        self.default_model = default_model
        self.timeout = timeout if timeout is not None else 30
        self.max_retries = max_retries if max_retries is not None else 3
        self.retry_delay = retry_delay if retry_delay is not None else 1

    @property
    def headers(self) -> dict:
        """Get the default headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def __eq__(self, other) -> bool:
        """Check if two Config objects are equal."""
        if not isinstance(other, Config):
            return False
        return (
            self.api_key == other.api_key and
            self.base_url == other.base_url and
            self.default_model == other.default_model and
            self.timeout == other.timeout and
            self.max_retries == other.max_retries and
            self.retry_delay == other.retry_delay
        )
    
    def __str__(self) -> str:
        """String representation of the Config object."""
        masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}" if len(self.api_key) > 8 else "***"
        return f"Config(api_key='{masked_key}', base_url='{self.base_url}', default_model='{self.default_model}', timeout={self.timeout}, max_retries={self.max_retries}, retry_delay={self.retry_delay})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the Config object."""
        masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}" if len(self.api_key) > 8 else "***"
        return f"Config(api_key='{masked_key}', base_url='{self.base_url}', default_model='{self.default_model}', timeout={self.timeout}, max_retries={self.max_retries}, retry_delay={self.retry_delay})"


def load_config(api_key: Optional[str] = None) -> Config:
    """
    Load configuration from environment variables or provided values.
    
    Args:
        api_key: Optional API key. If not provided, will be loaded from environment.
        
    Returns:
        Config: The loaded configuration.
        
    Raises:
        ValueError: If no API key is found.
    """
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Get API key from parameter or environment
    api_key = api_key or os.getenv("VENICE_API_KEY")
    if not api_key:
        raise ValueError("API key must be provided")
    
    # Get other configuration values from environment
    base_url = os.getenv("VENICE_BASE_URL")
    default_model = os.getenv("VENICE_DEFAULT_MODEL")
    
    # Handle zero values properly
    timeout_str = os.getenv("VENICE_TIMEOUT", "30")
    timeout = int(timeout_str) if timeout_str else 30
    
    max_retries_str = os.getenv("VENICE_MAX_RETRIES", "3")
    max_retries = int(max_retries_str) if max_retries_str else 3
    
    retry_delay_str = os.getenv("VENICE_RETRY_DELAY", "1")
    retry_delay = int(retry_delay_str) if retry_delay_str else 1
    
    return Config(
        api_key=api_key,
        base_url=base_url,
        default_model=default_model,
        timeout=timeout,
        max_retries=max_retries,
        retry_delay=retry_delay
    ) 