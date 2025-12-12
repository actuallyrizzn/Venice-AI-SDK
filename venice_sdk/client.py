"""
Core HTTP client for the Venice SDK.
"""

import hashlib
import json
import logging
import threading
import time
from typing import Any, Callable, Dict, Generator, Optional, Union

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import Config, load_config
from .errors import VeniceAPIError, VeniceConnectionError, handle_api_error
from .metrics import RateLimitMetrics

logger = logging.getLogger(__name__)


class HTTPClient:
    """
    HTTP client for interacting with the Venice API.
    
    This class handles all HTTP requests to the Venice API, including authentication,
    retries, and error handling.
    """
    
    def __init__(self, config: Optional[Config] = None, enable_metrics: bool = True):
        """
        Initialize the client.
        
        Args:
            config: Optional configuration. If not provided, will be loaded from environment.
            enable_metrics: Whether to enable rate limiting metrics collection (default: True)
        """
        self.config = config or load_config()
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        })
        retry_strategy = Retry(
            total=self.config.max_retries,
            status_forcelist=self.config.retry_status_codes,
            allowed_methods=frozenset(
                ["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE", "PATCH"]
            ),
            backoff_factor=self.config.retry_backoff_factor,
            raise_on_status=False,
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=self.config.pool_connections,
            pool_maxsize=self.config.pool_maxsize,
        )
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.metrics = RateLimitMetrics() if enable_metrics else None
    
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

        # Manual retry loop for rate limits (429). urllib3 Retry doesn't raise on status by
        # default, and tests also monkeypatch session.request directly.
        max_attempts = int(self.config.max_retries) if self.config.max_retries is not None else 1
        if max_attempts < 1:
            max_attempts = 1

        response: Response
        attempt = 0
        while True:
            attempt += 1
            try:
                response = self.session.request(
                    method,
                    url,
                    json=data,
                    stream=stream,
                    **kwargs,
                )
            except requests.exceptions.RequestException as e:
                logger.error(
                    "HTTP %s %s raised %s",
                    method.upper(),
                    url,
                    type(e).__name__,
                    exc_info=True,
                )
                raise VeniceConnectionError(
                    f"Request failed: {str(e)}",
                    context={"method": method.upper(), "url": url},
                    cause=e,
                ) from e

            if response.status_code != 429 or attempt >= max_attempts:
                break

            retry_after_header = (
                response.headers.get("Retry-After") if hasattr(response, "headers") else None
            )
            retry_after_seconds = None
            if retry_after_header is not None:
                try:
                    retry_after_seconds = int(retry_after_header)
                except (TypeError, ValueError):
                    retry_after_seconds = None

            # Backoff fallback when Retry-After is absent/invalid.
            if retry_after_seconds is None:
                delay = float(self.config.retry_delay) if self.config.retry_delay is not None else 0.0
                backoff = float(self.config.retry_backoff_factor) if self.config.retry_backoff_factor is not None else 0.0
                retry_after_seconds = int(max(0.0, delay * (backoff ** max(0, attempt - 1)))) if delay else 0

            if retry_after_seconds > 0:
                time.sleep(retry_after_seconds)

        if response.status_code >= 400:
            logger.warning(
                "HTTP %s %s failed with status %s",
                method.upper(),
                url,
                response.status_code,
            )
            parse_error: Optional[Exception] = None
            try:
                error_data = response.json() or {}
            except ValueError as json_error:
                parse_error = json_error
                error_data = {"error": {"message": response.text or "Unknown error"}}

            if isinstance(error_data.get("error"), str):
                error_data = {"error": {"message": error_data.get("error")}}

            retry_after_header = (
                response.headers.get("Retry-After") if hasattr(response, "headers") else None
            )
            retry_after_seconds = None
            if retry_after_header is not None:
                try:
                    retry_after_seconds = int(retry_after_header)
                except (TypeError, ValueError):
                    retry_after_seconds = None

            # If 429 and body lacks retry_after, inject from header for better error context
            if response.status_code == 429:
                error_obj = error_data.get("error") or {}
                if isinstance(error_obj, dict) and error_obj.get("retry_after") is None and retry_after_seconds is not None:
                    error_obj["retry_after"] = retry_after_seconds
                    error_data["error"] = error_obj

                # Record rate limit event in metrics
                if self.metrics is not None:
                    remaining_requests = None
                    # Try to extract remaining requests from response headers
                    if hasattr(response, "headers"):
                        remaining = response.headers.get("X-RateLimit-Remaining") or response.headers.get("x-ratelimit-remaining")
                        if remaining is not None:
                            try:
                                remaining_requests = int(remaining)
                            except (TypeError, ValueError):
                                pass

                    self.metrics.record_rate_limit(
                        endpoint=endpoint,
                        status_code=response.status_code,
                        retry_after=retry_after_seconds,
                        request_count=1,
                        remaining_requests=remaining_requests,
                        method=method.upper()
                    )

            error_context_extra = {
                "method": method.upper(),
                "url": url,
                "stream": stream,
            }
            if hasattr(response, "headers"):
                request_id_header = response.headers.get("X-Request-ID") or response.headers.get("x-request-id")
                if request_id_header:
                    error_context_extra["request_id"] = request_id_header
                if retry_after_header is not None:
                    error_context_extra["retry_after_header"] = retry_after_header

            handle_api_error(
                response.status_code,
                error_data,
                extra_context=error_context_extra,
                cause=parse_error,
            )
            return response

        logger.debug(
            "HTTP %s %s succeeded with status %s (stream=%s)",
            method.upper(),
            url,
            response.status_code,
            stream,
        )
        return response
    
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
            parse_error: Optional[Exception] = None
            try:
                error_data = response.json() or {}
            except ValueError as json_error:
                parse_error = json_error
                error_data = {"error": {"message": response.text or "Unknown error"}}

            # Normalize string error payloads to dict form
            if isinstance(error_data.get("error"), str):
                error_data = {"error": {"message": error_data.get("error")}}

            # Inject Retry-After header if present but missing in body for 429s
            if response.status_code == 429:
                retry_after_header = response.headers.get("Retry-After") if hasattr(response, "headers") else None
                retry_after_seconds = None
                if retry_after_header is not None:
                    try:
                        retry_after_seconds = int(retry_after_header)
                    except (TypeError, ValueError):
                        retry_after_seconds = None
                    if retry_after_seconds is not None:
                        error_obj = error_data.get("error") or {}
                        if isinstance(error_obj, dict) and error_obj.get("retry_after") is None:
                            error_obj["retry_after"] = retry_after_seconds
                            error_data["error"] = error_obj
                
                # Record rate limit event in metrics
                if self.metrics is not None:
                    remaining_requests = None
                    if hasattr(response, "headers"):
                        remaining = response.headers.get("X-RateLimit-Remaining") or response.headers.get("x-ratelimit-remaining")
                        if remaining is not None:
                            try:
                                remaining_requests = int(remaining)
                            except (TypeError, ValueError):
                                pass
                    
                    # Extract endpoint from response URL if available
                    endpoint = getattr(response, "url", "unknown")
                    self.metrics.record_rate_limit(
                        endpoint=endpoint,
                        status_code=response.status_code,
                        retry_after=retry_after_seconds,
                        request_count=1,
                        remaining_requests=remaining_requests,
                        method="POST"  # Streaming is typically POST
                    )

            extra_context = {
                "stream": True,
                "url": getattr(response, "url", None),
            }
            handle_api_error(
                response.status_code,
                error_data,
                extra_context=extra_context,
                cause=parse_error,
            )
        
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

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        **kwargs: Any,
    ):
        """Backward compatible wrapper for legacy callers expecting `_make_request`."""
        response = self._request(method, endpoint, data=data, stream=stream, **kwargs)
        if stream:
            return self._handle_streaming_response(response)
        return response


class HTTPClientManager:
    """Manages pooled HTTPClient instances keyed by configuration."""

    def __init__(self, builder: Optional[Callable[[Config], HTTPClient]] = None):
        self._builder: Callable[[Config], HTTPClient] = builder or (lambda cfg: HTTPClient(cfg))
        self._clients: Dict[str, HTTPClient] = {}
        self._lock = threading.Lock()

    def set_builder(self, builder: Callable[[Config], HTTPClient]) -> None:
        """Override the client builder and clear existing cache."""
        with self._lock:
            self._builder = builder
            self._clients.clear()

    def _ensure_config(self, config: Optional[Config]) -> Config:
        return config or load_config()

    def _config_key(self, config: Config) -> str:
        """Create a stable cache key without exposing sensitive data."""
        api_key_hash = hashlib.sha256(config.api_key.encode("utf-8")).hexdigest()
        raw = "|".join(
            [
                api_key_hash,
                config.base_url or "",
                config.default_model or "",
                str(config.timeout),
                str(config.max_retries),
                str(config.retry_delay),
            ]
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get_client(self, config: Optional[Config] = None, force_refresh: bool = False) -> HTTPClient:
        """Retrieve a cached HTTP client for the provided configuration."""
        cfg = self._ensure_config(config)
        cache_key = self._config_key(cfg)

        if not force_refresh:
            with self._lock:
                cached = self._clients.get(cache_key)
                if cached is not None:
                    return cached

        client = self._builder(cfg)
        if isinstance(client, HTTPClient):
            with self._lock:
                self._clients[cache_key] = client
        return client

    def clear(self, config: Optional[Config] = None) -> None:
        """Clear cached clients (all or specific configuration)."""
        with self._lock:
            if config is None:
                self._clients.clear()
                return
            cache_key = self._config_key(self._ensure_config(config))
            self._clients.pop(cache_key, None)


_http_client_manager = HTTPClientManager()


def get_http_client_manager() -> HTTPClientManager:
    """Return the process-wide HTTP client manager."""
    return _http_client_manager