"""
Core HTTP client for the Venice SDK.
"""

import json
import logging
import time
from typing import Any, Dict, Generator, Optional, Union

import requests
from requests import Response

from .config import Config, load_config
from .errors import VeniceAPIError, VeniceConnectionError, handle_api_error

logger = logging.getLogger(__name__)


class HTTPClient:
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
        self.config = config or load_config()
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        })
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        **kwargs: Any
    ) -> Response:
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
            VeniceConnectionError: If there is a connection error
        """
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        payload_keys = sorted(data.keys()) if isinstance(data, dict) else None
        logger.debug(
            "Preparing HTTP %s %s (stream=%s, payload_keys=%s)",
            method.upper(),
            url,
            stream,
            payload_keys,
        )

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
                
                # Common error handling (non-2xx)
                if response.status_code >= 400:
                    logger.warning(
                        "HTTP %s %s failed with status %s (attempt %s/%s)",
                        method.upper(),
                        url,
                        response.status_code,
                        attempt + 1,
                        self.config.max_retries,
                    )
                    # Attempt to parse error payload safely
                    try:
                        error_data = response.json() or {}
                    except Exception:
                        error_data = {"error": {"message": response.text or "Unknown error"}}

                    # Normalize string error payloads to dict form
                    if isinstance(error_data.get("error"), str):
                        error_data = {"error": {"message": error_data.get("error")}}

                    status = response.status_code

                    # Determine if this error is retriable
                    is_rate_limited = status == 429
                    is_server_error = status >= 500

                    # Calculate retry delay using Retry-After header if present
                    retry_after_header = response.headers.get("Retry-After") if hasattr(response, "headers") else None
                    retry_after_seconds = None
                    if retry_after_header is not None:
                        try:
                            retry_after_seconds = int(retry_after_header)
                        except Exception:
                            retry_after_seconds = None

                    # If 429 and body lacks retry_after, inject from header for better error context
                    if is_rate_limited:
                        error_obj = error_data.get("error") or {}
                        if isinstance(error_obj, dict) and error_obj.get("retry_after") is None and retry_after_seconds is not None:
                            error_obj["retry_after"] = retry_after_seconds
                            error_data["error"] = error_obj

                    # Retry on 429 and 5xx if attempts remain
                    if (is_rate_limited or is_server_error) and attempt < self.config.max_retries - 1:
                        delay_seconds = retry_after_seconds if retry_after_seconds is not None else self.config.retry_delay * (2 ** attempt)
                        logger.info(
                            "Retrying HTTP %s %s after %ss delay (attempt %s/%s)",
                            method.upper(),
                            url,
                            delay_seconds,
                            attempt + 1,
                            self.config.max_retries,
                        )
                        time.sleep(delay_seconds)
                        continue

                    # No retry or attempts exhausted: raise specific API error
                    handle_api_error(status, error_data)
                    # handle_api_error always raises; the following return is unreachable.
                    return response

                # Success
                logger.debug(
                    "HTTP %s %s succeeded with status %s (stream=%s)",
                    method.upper(),
                    url,
                    response.status_code,
                    stream,
                )
                return response
                
            except requests.exceptions.RequestException as e:
                logger.error(
                    "HTTP %s %s raised %s on attempt %s/%s",
                    method.upper(),
                    url,
                    type(e).__name__,
                    attempt + 1,
                    self.config.max_retries,
                    exc_info=True,
                )
                if attempt == self.config.max_retries - 1:
                    raise VeniceConnectionError(f"Request failed after {self.config.max_retries} attempts: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def _handle_streaming_response(self, response: Response) -> Generator[Dict[str, Any], None, None]:
        """
        Handle streaming responses from the API.
        
        Args:
            response: Response object
            
        Yields:
            Parsed JSON chunks as dictionaries
            
        Raises:
            VeniceAPIError: If the request fails
        """
        if response.status_code >= 400:
            logger.warning(
                "Streaming response returned status %s before payload consumption",
                response.status_code,
            )
            try:
                error_data = response.json() or {}
            except Exception:
                error_data = {"error": {"message": response.text or "Unknown error"}}

            # Normalize string error payloads to dict form
            if isinstance(error_data.get("error"), str):
                error_data = {"error": {"message": error_data.get("error")}}

            # Inject Retry-After header if present but missing in body for 429s
            if response.status_code == 429:
                retry_after_header = response.headers.get("Retry-After") if hasattr(response, "headers") else None
                if retry_after_header is not None:
                    try:
                        retry_after_seconds = int(retry_after_header)
                    except Exception:
                        retry_after_seconds = None
                    if retry_after_seconds is not None:
                        error_obj = error_data.get("error") or {}
                        if isinstance(error_obj, dict) and error_obj.get("retry_after") is None:
                            error_obj["retry_after"] = retry_after_seconds
                            error_data["error"] = error_obj

            handle_api_error(response.status_code, error_data)
        
        for line in response.iter_lines():
            if not line:
                continue
            
            line_str = line.decode("utf-8")
            logger.debug("Received streaming chunk: %s", line_str[:200])
            
            # Handle Server-Sent Events format
            if line_str.startswith("data: "):
                data_content = line_str[6:]  # Remove "data: " prefix
                if data_content.strip() == "[DONE]":
                    break
                try:
                    data = json.loads(data_content)
                    # Yield the parsed JSON data as a dict
                    yield data
                except json.JSONDecodeError:
                    logger.debug("Skipping non-JSON streaming line")
                    continue
            else:
                # Handle other formats (legacy)
                try:
                    data = json.loads(line_str)
                    if "chunk" in data:
                        yield data["chunk"]
                    else:
                        yield data
                except json.JSONDecodeError:
                    continue
    
    def get(self, endpoint: str, **kwargs: Any) -> Response:
        """Make a GET request."""
        return self._request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Response:
        """Make a POST request."""
        return self._request("POST", endpoint, data=data, **kwargs)
    
    def stream(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Generator[Dict[str, Any], None, None]:
        """Make a streaming request."""
        response = self._request("POST", endpoint, data=data, stream=True, **kwargs)
        logger.debug("HTTP POST %s streaming response started", endpoint)
        return self._handle_streaming_response(response)
    
    def delete(self, endpoint: str, **kwargs: Any) -> Response:
        """Make a DELETE request."""
        return self._request("DELETE", endpoint, **kwargs)