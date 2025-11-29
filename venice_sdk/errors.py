"""
Custom exceptions for the Venice SDK.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class VeniceError(Exception):
    """Base exception for all Venice SDK errors."""

    def __init__(
        self,
        message: str,
        *,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.context = dict(context) if context else {}
        self.cause = cause

    def __str__(self) -> str:
        base_msg = super().__str__()
        prefix = f"[{self.error_code}] " if self.error_code else ""
        rendered = f"{prefix}{base_msg}"

        suffix_parts = []
        status_code = getattr(self, "status_code", None)
        if status_code is not None:
            suffix_parts.append(f"HTTP {status_code}")
        if self.context:
            context_pairs = ", ".join(
                f"{key}={repr(value)}" for key, value in sorted(self.context.items())
            )
            suffix_parts.append(f"Context: {context_pairs}")

        if suffix_parts:
            rendered = f"{rendered} ({'; '.join(suffix_parts)})"
        return rendered


class VeniceAPIError(VeniceError):
    """Base exception for all Venice API errors."""

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, error_code=error_code, context=context, cause=cause)
        self.status_code = status_code


class VeniceConnectionError(VeniceError):
    """Raised when there is a connection error."""


class RateLimitError(VeniceAPIError):
    """Raised when the rate limit is exceeded."""

    def __init__(
        self,
        message: str,
        *,
        retry_after: Optional[int] = None,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(
            message,
            status_code=status_code,
            error_code=error_code,
            context=context,
            cause=cause,
        )
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


def handle_api_error(
    status_code: int,
    response_data: Dict[str, Any],
    *,
    extra_context: Optional[Dict[str, Any]] = None,
    cause: Optional[Exception] = None,
) -> None:
    """
    Handle API errors by raising appropriate exceptions.
    
    Args:
        status_code: HTTP status code
        response_data: Response data from the API
        
    Raises:
        VeniceAPIError: Appropriate exception based on the error
    """
    # Normalize non-dict payloads for consistent handling
    if not isinstance(response_data, dict):
        response_data = {"error": {"message": str(response_data)}}

    error_message = "Unknown error"
    error_code: Optional[str] = None
    error_context: Dict[str, Any] = {}
    if extra_context:
        error_context.update(extra_context)

    details = response_data.get("details")
    if isinstance(details, dict):
        error_context["details"] = details
        for field, errors in details.items():
            if isinstance(errors, dict) and "_errors" in errors:
                error_list = errors["_errors"]
                if error_list:
                    error_message = error_list[0]
                    break
            elif isinstance(errors, list) and errors:
                error_message = errors[0]
                break

    raw_error_obj = response_data.get("error")
    if isinstance(raw_error_obj, dict):
        error_obj = raw_error_obj
    elif isinstance(raw_error_obj, str):
        error_obj = {"message": raw_error_obj}
    elif raw_error_obj is None:
        error_obj = {}
    else:
        error_obj = {"message": str(raw_error_obj)}

    if error_obj:
        error_context["error"] = error_obj

    if error_message == "Unknown error":
        if error_obj:
            error_code = error_obj.get("code")
            error_message = error_obj.get("message", error_message)
        else:
            fallback_message = response_data.get("message")
            if isinstance(fallback_message, str):
                error_message = fallback_message

    if error_code is None and isinstance(error_obj, dict):
        error_code = error_obj.get("code")

    request_id = response_data.get("request_id")
    if not request_id and isinstance(error_obj, dict):
        request_id = error_obj.get("request_id")
    if request_id and "request_id" not in error_context:
        error_context["request_id"] = request_id

    retry_after = None
    if isinstance(error_obj, dict):
        retry_after = error_obj.get("retry_after")
    if retry_after is None:
        candidate = response_data.get("retry_after")
        if candidate is not None:
            try:
                retry_after = int(candidate)
            except (TypeError, ValueError):
                retry_after = None

    if isinstance(error_message, str):
        error_message = error_message.strip()
    if not error_message:
        error_message = f"Request failed with status {status_code}"
    
    if status_code == 401:
        raise UnauthorizedError(
            error_message,
            status_code=status_code,
            error_code=error_code,
            context=error_context or None,
            cause=cause,
        )
    elif status_code == 429:
        raise RateLimitError(
            error_message,
            retry_after=retry_after,
            status_code=status_code,
            error_code=error_code,
            context=error_context or None,
            cause=cause,
        )
    elif status_code == 404:
        if error_code == "CHARACTER_NOT_FOUND":
            raise CharacterNotFoundError(
                error_message,
                status_code=status_code,
                error_code=error_code,
                context=error_context or None,
                cause=cause,
            )
        elif error_code == "MODEL_NOT_FOUND":
            raise ModelNotFoundError(
                error_message,
                status_code=status_code,
                error_code=error_code,
                context=error_context or None,
                cause=cause,
            )
        else:
            raise InvalidRequestError(
                error_message,
                status_code=status_code,
                error_code=error_code,
                context=error_context or None,
                cause=cause,
            )
    elif status_code >= 400:
        # If we don't have a more specific mapping, raise generic API error
        raise VeniceAPIError(
            error_message,
            status_code=status_code,
            error_code=error_code,
            context=error_context or None,
            cause=cause,
        )