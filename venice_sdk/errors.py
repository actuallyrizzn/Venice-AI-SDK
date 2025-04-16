"""
Custom exceptions for the Venice SDK.
"""

class VeniceAPIError(Exception):
    """Base exception for all Venice API errors."""
    pass


class RateLimitError(VeniceAPIError):
    """Raised when the rate limit is exceeded."""
    pass


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
    error_code = response_data.get("error", {}).get("code")
    error_message = response_data.get("error", {}).get("message", "Unknown error")
    
    if status_code == 401:
        raise UnauthorizedError(error_message)
    elif status_code == 429:
        raise RateLimitError(error_message)
    elif status_code == 404:
        if error_code == "CHARACTER_NOT_FOUND":
            raise CharacterNotFoundError(error_message)
        elif error_code == "MODEL_NOT_FOUND":
            raise ModelNotFoundError(error_message)
        else:
            raise InvalidRequestError(error_message)
    elif status_code >= 400:
        raise InvalidRequestError(error_message) 