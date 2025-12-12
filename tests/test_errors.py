"""
Tests for the errors module.
"""

import pytest
from venice_sdk.errors import (
    VeniceError,
    VeniceAPIError,
    VeniceConnectionError,
    RateLimitError,
    UnauthorizedError,
    InvalidRequestError
)


def test_venice_error():
    """Test base VeniceError."""
    error = VeniceError("Test error")
    assert str(error) == "Test error"


def test_venice_api_error():
    """Test VeniceAPIError."""
    error = VeniceAPIError("API error", status_code=400)
    assert "API error" in str(error)
    assert "HTTP 400" in str(error)
    assert error.status_code == 400


def test_venice_connection_error():
    """Test VeniceConnectionError."""
    error = VeniceConnectionError("Connection failed")
    assert str(error) == "Connection failed"
    assert isinstance(error, VeniceError)


def test_rate_limit_error():
    """Test RateLimitError."""
    error = RateLimitError("Rate limit exceeded", retry_after=60)
    assert str(error) == "Rate limit exceeded"
    assert error.retry_after == 60
    assert isinstance(error, VeniceAPIError)


def test_unauthorized_error():
    """Test UnauthorizedError."""
    error = UnauthorizedError("Invalid API key")
    assert str(error) == "Invalid API key"
    assert isinstance(error, VeniceAPIError)


def test_invalid_request_error():
    """Test InvalidRequestError."""
    error = InvalidRequestError("Invalid request parameters")
    assert str(error) == "Invalid request parameters"
    assert isinstance(error, VeniceAPIError)


def test_error_hierarchy():
    """Test error class hierarchy."""
    assert issubclass(VeniceAPIError, VeniceError)
    assert issubclass(VeniceConnectionError, VeniceError)
    assert issubclass(RateLimitError, VeniceAPIError)
    assert issubclass(UnauthorizedError, VeniceAPIError)
    assert issubclass(InvalidRequestError, VeniceAPIError) 