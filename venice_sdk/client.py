"""
Core HTTP client for the Venice SDK.
"""

import json
import time
from typing import Any, Dict, Generator, Optional, Union

import requests
from requests import Response

from .config import Config
from .errors import handle_api_error


class VeniceClient:
    """
    HTTP client for interacting with the Venice API.
    
    This class handles all HTTP requests to the Venice API, including authentication,
    retries, and error handling.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the client.
        
        Args:
            config: Optional configuration. If not provided, will be loaded from environment.
        """
        from .config import load_config
        self.config = config or load_config()
        self.session = requests.Session()
        self.session.headers.update(self.config.headers)
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[Response, Generator[str, None, None]]:
        """
        Make an HTTP request to the Venice API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request data
            stream: Whether to stream the response
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response object or generator for streaming responses
            
        Raises:
            VeniceAPIError: If the request fails
        """
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        
        # Add timeout if not specified
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.config.timeout
        
        # Add retry logic
        for attempt in range(self.config.max_retries):
            try:
                response = self.session.request(
                    method,
                    url,
                    json=data,
                    stream=stream,
                    **kwargs
                )
                
                # Handle streaming responses
                if stream:
                    return self._handle_streaming_response(response)
                
                # Handle non-streaming responses
                if response.status_code >= 400:
                    handle_api_error(response.status_code, response.json())
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt == self.config.max_retries - 1:
                    raise VeniceAPIError(f"Request failed after {self.config.max_retries} attempts: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def _handle_streaming_response(self, response: Response) -> Generator[str, None, None]:
        """
        Handle streaming responses from the API.
        
        Args:
            response: Response object
            
        Yields:
            Chunks of the response
            
        Raises:
            VeniceAPIError: If the request fails
        """
        if response.status_code >= 400:
            handle_api_error(response.status_code, response.json())
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith("data: "):
                    data = line[len("data: "):]
                    if data == "[DONE]":
                        return
                    try:
                        chunk = json.loads(data)
                        yield chunk
                    except json.JSONDecodeError:
                        continue
    
    def get(self, endpoint: str, **kwargs) -> Response:
        """Make a GET request."""
        return self._make_request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Response:
        """Make a POST request."""
        return self._make_request("POST", endpoint, data=data, **kwargs)
    
    def stream(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Generator[str, None, None]:
        """Make a streaming request."""
        return self._make_request("POST", endpoint, data=data, stream=True, **kwargs) 