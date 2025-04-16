"""
Configuration management for the Venice SDK.
"""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Config:
    """Configuration for the Venice SDK."""
    api_key: str
    base_url: str = "https://api.venice.ai/api/v1"
    default_model: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3

    @property
    def headers(self) -> dict:
        """Get the default headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }


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
        raise ValueError(
            "No API key provided. Set VENICE_API_KEY environment variable or pass api_key parameter."
        )
    
    # Get default model from environment if set
    default_model = os.getenv("VENICE_DEFAULT_MODEL")
    
    return Config(
        api_key=api_key,
        default_model=default_model,
    ) 