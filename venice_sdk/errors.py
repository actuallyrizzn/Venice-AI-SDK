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


class ImageGenerationError(VeniceAPIError):
    """Raised when image generation fails."""
    pass


class AudioGenerationError(VeniceAPIError):
    """Raised when audio generation fails."""
    pass


class BillingError(VeniceAPIError):
    """Raised when billing-related operations fail."""
    pass


class APIKeyError(VeniceAPIError):
    """Raised when API key operations fail."""
    pass


class EmbeddingError(VeniceAPIError):
    """Raised when embedding operations fail."""
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
    # Check for error message in various fields
    error_message = "Unknown error"
    error_code = None
    
    # Try to get error message from different possible fields
    if "details" in response_data:
        details = response_data["details"]
        if isinstance(details, dict):
            # Look for error messages in the details
            for field, errors in details.items():
                if isinstance(errors, dict) and "_errors" in errors:
                    error_list = errors["_errors"]
                    if error_list and len(error_list) > 0:
                        error_message = error_list[0]
                        break
                elif isinstance(errors, list) and len(errors) > 0:
                    error_message = errors[0]
                    break
    
    # Fallback to standard error field
    if error_message == "Unknown error":
        error_obj = response_data.get("error")
        if isinstance(error_obj, str):
            error_message = error_obj
        elif isinstance(error_obj, dict):
            error_code = error_obj.get("code")
            error_message = error_obj.get("message", "Unknown error")
    
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