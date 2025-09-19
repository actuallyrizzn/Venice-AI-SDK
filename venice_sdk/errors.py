"""
Custom exceptions for the Venice SDK.
"""


class VeniceError(Exception):
    """Base exception for all Venice SDK errors."""
    pass


class VeniceAPIError(VeniceError):
    """Base exception for all Venice API errors."""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class VeniceConnectionError(VeniceError):
    """Raised when there is a connection error."""
    pass


class RateLimitError(VeniceAPIError):
    """Raised when the rate limit is exceeded."""
    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after


class UnauthorizedError(VeniceAPIError):
    """Raised when authentication fails."""
    pass


class InvalidRequestError(VeniceAPIError):
    """Raised when the request is invalid."""
    pass


class ModelNotFoundError(VeniceAPIError):
    """Raised when the requested model is not found."""
    pass


class CharacterNotFoundError(VeniceAPIError):
    """Raised when the requested character is not found."""
    pass


def handle_api_error(status_code: int, response_data: dict) -> None:
    """
    Handle API errors by raising appropriate exceptions.
    
    Args:
        status_code: HTTP status code
        response_data: Response data from the API
        
    Raises:
        VeniceAPIError: Appropriate exception based on the error
    """
    # Normalize shapes: "error" may be a string or dict
    error_obj = response_data.get("error")
    if isinstance(error_obj, str):
        error_code = None
        error_message = error_obj
        error_payload = {}
    else:
        error_payload = error_obj or {}
        error_code = error_payload.get("code")
        error_message = error_payload.get("message", "Unknown error")
    
    if status_code == 401:
        raise UnauthorizedError(error_message, status_code=status_code)
    elif status_code == 429:
        retry_after = response_data.get("error", {}).get("retry_after")
        raise RateLimitError(error_message, retry_after=retry_after)
    elif status_code == 404:
        if error_code == "CHARACTER_NOT_FOUND":
            raise CharacterNotFoundError(error_message, status_code=status_code)
        elif error_code == "MODEL_NOT_FOUND":
            raise ModelNotFoundError(error_message, status_code=status_code)
        else:
            raise InvalidRequestError(error_message, status_code=status_code)
    elif status_code >= 400:
        # If we don't have a more specific mapping, raise generic API error
        raise VeniceAPIError(error_message, status_code=status_code)