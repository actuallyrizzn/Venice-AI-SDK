"""
Comprehensive unit tests for the errors module to achieve 100% coverage.
"""

import pytest
from venice_sdk.errors import (
    VeniceError,
    VeniceAPIError,
    VeniceConnectionError,
    RateLimitError,
    UnauthorizedError,
    InvalidRequestError,
    ModelNotFoundError,
    CharacterNotFoundError,
    ImageGenerationError,
    AudioGenerationError,
    BillingError,
    EmbeddingError,
    handle_api_error
)


class TestVeniceError:
    """Test base VeniceError class."""

    def test_venice_error_initialization(self):
        """Test VeniceError initialization."""
        error = VeniceError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)


class TestVeniceAPIError:
    """Test VeniceAPIError class."""

    def test_venice_api_error_initialization(self):
        """Test VeniceAPIError initialization."""
        error = VeniceAPIError("API error", status_code=400)
        rendered = str(error)
        assert rendered.startswith("API error")
        assert "HTTP 400" in rendered
        assert error.status_code == 400
        assert isinstance(error, VeniceError)

    def test_venice_api_error_without_status_code(self):
        """Test VeniceAPIError without status code."""
        error = VeniceAPIError("API error")
        assert str(error) == "API error"
        assert error.status_code is None


class TestVeniceConnectionError:
    """Test VeniceConnectionError class."""

    def test_venice_connection_error_initialization(self):
        """Test VeniceConnectionError initialization."""
        error = VeniceConnectionError("Connection error")
        assert str(error) == "Connection error"
        assert isinstance(error, VeniceError)


class TestRateLimitError:
    """Test RateLimitError class."""

    def test_rate_limit_error_initialization(self):
        """Test RateLimitError initialization."""
        error = RateLimitError("Rate limited", retry_after=60)
        assert str(error) == "Rate limited"
        assert error.retry_after == 60
        assert isinstance(error, VeniceAPIError)

    def test_rate_limit_error_without_retry_after(self):
        """Test RateLimitError without retry_after."""
        error = RateLimitError("Rate limited")
        assert str(error) == "Rate limited"
        assert error.retry_after is None


class TestUnauthorizedError:
    """Test UnauthorizedError class."""

    def test_unauthorized_error_initialization(self):
        """Test UnauthorizedError initialization."""
        error = UnauthorizedError("Unauthorized")
        assert str(error) == "Unauthorized"
        assert isinstance(error, VeniceAPIError)


class TestInvalidRequestError:
    """Test InvalidRequestError class."""

    def test_invalid_request_error_initialization(self):
        """Test InvalidRequestError initialization."""
        error = InvalidRequestError("Invalid request")
        assert str(error) == "Invalid request"
        assert isinstance(error, VeniceAPIError)


class TestModelNotFoundError:
    """Test ModelNotFoundError class."""

    def test_model_not_found_error_initialization(self):
        """Test ModelNotFoundError initialization."""
        error = ModelNotFoundError("Model not found")
        assert str(error) == "Model not found"
        assert isinstance(error, VeniceAPIError)


class TestCharacterNotFoundError:
    """Test CharacterNotFoundError class."""

    def test_character_not_found_error_initialization(self):
        """Test CharacterNotFoundError initialization."""
        error = CharacterNotFoundError("Character not found")
        assert str(error) == "Character not found"
        assert isinstance(error, VeniceAPIError)


class TestImageGenerationError:
    """Test ImageGenerationError class."""

    def test_image_generation_error_initialization(self):
        """Test ImageGenerationError initialization."""
        error = ImageGenerationError("Image generation failed")
        assert str(error) == "Image generation failed"
        assert isinstance(error, VeniceAPIError)


class TestAudioGenerationError:
    """Test AudioGenerationError class."""

    def test_audio_generation_error_initialization(self):
        """Test AudioGenerationError initialization."""
        error = AudioGenerationError("Audio generation failed")
        assert str(error) == "Audio generation failed"
        assert isinstance(error, VeniceAPIError)


class TestBillingError:
    """Test BillingError class."""

    def test_billing_error_initialization(self):
        """Test BillingError initialization."""
        error = BillingError("Billing error")
        assert str(error) == "Billing error"
        assert isinstance(error, VeniceAPIError)


class TestEmbeddingError:
    """Test EmbeddingError class."""

    def test_embedding_error_initialization(self):
        """Test EmbeddingError initialization."""
        error = EmbeddingError("Embedding error")
        assert str(error) == "Embedding error"
        assert isinstance(error, VeniceAPIError)


class TestHandleAPIError:
    """Test handle_api_error function."""

    def test_handle_api_error_401(self):
        """Test handling 401 error."""
        with pytest.raises(UnauthorizedError) as exc_info:
            handle_api_error(401, {"error": {"message": "Unauthorized"}})
        assert "Unauthorized" in str(exc_info.value)

    def test_handle_api_error_401_with_string_error(self):
        """Test handling 401 error with string error."""
        with pytest.raises(UnauthorizedError) as exc_info:
            handle_api_error(401, {"error": "Unauthorized"})
        assert "Unauthorized" in str(exc_info.value)

    def test_handle_api_error_429(self):
        """Test handling 429 error."""
        with pytest.raises(RateLimitError) as exc_info:
            handle_api_error(429, {"error": {"message": "Rate limited", "retry_after": 60}})
        assert "Rate limited" in str(exc_info.value)
        assert exc_info.value.retry_after == 60

    def test_handle_api_error_429_without_retry_after(self):
        """Test handling 429 error without retry_after."""
        with pytest.raises(RateLimitError) as exc_info:
            handle_api_error(429, {"error": {"message": "Rate limited"}})
        assert "Rate limited" in str(exc_info.value)
        assert exc_info.value.retry_after is None

    def test_handle_api_error_404_character_not_found(self):
        """Test handling 404 error with CHARACTER_NOT_FOUND code."""
        with pytest.raises(CharacterNotFoundError) as exc_info:
            handle_api_error(404, {"error": {"code": "CHARACTER_NOT_FOUND", "message": "Character not found"}})
        assert "Character not found" in str(exc_info.value)

    def test_handle_api_error_404_model_not_found(self):
        """Test handling 404 error with MODEL_NOT_FOUND code."""
        with pytest.raises(ModelNotFoundError) as exc_info:
            handle_api_error(404, {"error": {"code": "MODEL_NOT_FOUND", "message": "Model not found"}})
        assert "Model not found" in str(exc_info.value)

    def test_handle_api_error_404_generic(self):
        """Test handling 404 error without specific code."""
        with pytest.raises(InvalidRequestError) as exc_info:
            handle_api_error(404, {"error": {"message": "Not found"}})
        assert "Not found" in str(exc_info.value)

    def test_handle_api_error_404_with_string_error(self):
        """Test handling 404 error with string error."""
        with pytest.raises(InvalidRequestError) as exc_info:
            handle_api_error(404, {"error": "Not found"})
        assert "Not found" in str(exc_info.value)

    def test_handle_api_error_other_status(self):
        """Test handling other status codes."""
        with pytest.raises(VeniceAPIError) as exc_info:
            handle_api_error(500, {"error": {"message": "Server error"}})
        assert "Server error" in str(exc_info.value)

    def test_handle_api_error_without_error_key(self):
        """Test handling error without error key."""
        with pytest.raises(VeniceAPIError) as exc_info:
            handle_api_error(400, {"message": "Bad request"})
        assert "Bad request" in str(exc_info.value)

    def test_handle_api_error_with_none_error(self):
        """Test handling error with None error."""
        with pytest.raises(VeniceAPIError) as exc_info:
            handle_api_error(400, {"error": None})
        assert "Unknown error" in str(exc_info.value)

    def test_handle_api_error_with_empty_error(self):
        """Test handling error with empty error."""
        with pytest.raises(VeniceAPIError) as exc_info:
            handle_api_error(400, {"error": {}})
        assert "Unknown error" in str(exc_info.value)

    def test_handle_api_error_without_message(self):
        """Test handling error without message."""
        with pytest.raises(VeniceAPIError) as exc_info:
            handle_api_error(400, {"error": {"code": "BAD_REQUEST"}})
        assert "Unknown error" in str(exc_info.value)
