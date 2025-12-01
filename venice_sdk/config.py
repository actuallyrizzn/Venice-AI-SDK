"""
Configuration management for the Venice SDK.
"""

import os
from typing import Dict, Iterable, List, Optional
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
        retry_delay: Optional[int] = None,
        pool_connections: Optional[int] = None,
        pool_maxsize: Optional[int] = None,
        retry_backoff_factor: Optional[float] = None,
        retry_status_codes: Optional[Iterable[int]] = None,
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
        self.base_url = base_url if base_url is not None else "https://api.venice.ai/api/v1"
        self.default_model = default_model
        self.timeout = timeout if timeout is not None else 30
        self.max_retries = max_retries if max_retries is not None else 3
        self.retry_delay = retry_delay if retry_delay is not None else 1
        self.pool_connections = pool_connections if pool_connections is not None else 10
        self.pool_maxsize = pool_maxsize if pool_maxsize is not None else 20
        self.retry_backoff_factor = (
            retry_backoff_factor if retry_backoff_factor is not None else 0.5
        )
        default_retry_statuses: List[int] = [429, 500, 502, 503, 504]
        if retry_status_codes is None:
            self.retry_status_codes = default_retry_statuses
        else:
            self.retry_status_codes = list(retry_status_codes) or default_retry_statuses

    @property
    def headers(self) -> Dict[str, str]:
        """Get the default headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def __eq__(self, other: object) -> bool:
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
        return f"Config(api_key='***', base_url='{self.base_url}', default_model='{self.default_model}', timeout={self.timeout}, max_retries={self.max_retries}, retry_delay={self.retry_delay})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the Config object."""
        return f"Config(api_key='***', base_url='{self.base_url}', default_model='{self.default_model}', timeout={self.timeout}, max_retries={self.max_retries}, retry_delay={self.retry_delay})"


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
    
    pool_connections_str = os.getenv("VENICE_POOL_CONNECTIONS", "10")
    pool_connections = int(pool_connections_str) if pool_connections_str else 10

    pool_maxsize_str = os.getenv("VENICE_POOL_MAXSIZE", "20")
    pool_maxsize = int(pool_maxsize_str) if pool_maxsize_str else 20

    retry_backoff_str = os.getenv("VENICE_RETRY_BACKOFF_FACTOR", "0.5")
    retry_backoff_factor = float(retry_backoff_str) if retry_backoff_str else 0.5

    retry_status_codes_env = os.getenv("VENICE_RETRY_STATUS_CODES")
    retry_status_codes: Optional[List[int]] = None
    if retry_status_codes_env:
        try:
            retry_status_codes = [
                int(code.strip())
                for code in retry_status_codes_env.split(",")
                if code.strip()
            ]
        except ValueError:
            retry_status_codes = None

    return Config(
        api_key=api_key,
        base_url=base_url,
        default_model=default_model,
        timeout=timeout,
        max_retries=max_retries,
        retry_delay=retry_delay,
        pool_connections=pool_connections,
        pool_maxsize=pool_maxsize,
        retry_backoff_factor=retry_backoff_factor,
        retry_status_codes=retry_status_codes,
    )