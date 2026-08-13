"""
Unit tests for the endpoints module.
"""

from venice_sdk.endpoints import (
    ImageEndpoints,
    ChatEndpoints,
    AccountEndpoints,
    AudioEndpoints,
    CharactersEndpoints,
    EmbeddingsEndpoints,
    ModelsEndpoints,
    VideoEndpoints,
    AugmentEndpoints,
    CryptoEndpoints,
    X402Endpoints,
    TEEEndpoints,
)


class TestImageEndpoints:
    """Test ImageEndpoints constants."""

    def test_image_endpoints_constants(self):
        """Test that all image endpoint constants are defined correctly."""
        assert ImageEndpoints.GENERATIONS == "/images/generations"
        assert ImageEndpoints.GENERATE == "/image/generate"
        assert ImageEndpoints.EDIT == "/image/edit"
        assert ImageEndpoints.UPSCALE == "/image/upscale"
        assert ImageEndpoints.STYLES == "/image/styles"

    def test_native_image_routes_are_singular(self):
        """Native Venice image routes use singular /image/ (live API, 2026-08)."""
        for endpoint in (
            ImageEndpoints.GENERATE,
            ImageEndpoints.EDIT,
            ImageEndpoints.MULTI_EDIT,
            ImageEndpoints.BACKGROUND_REMOVE,
            ImageEndpoints.UPSCALE,
            ImageEndpoints.STYLES,
        ):
            assert endpoint.startswith("/image/"), f"{endpoint} should start with /image/"

    def test_openai_compat_generations_is_plural(self):
        """OpenAI-compatible generations alias stays under /images/."""
        assert ImageEndpoints.GENERATIONS.startswith("/images/")


class TestOtherEndpoints:
    """Test other endpoint constants."""

    def test_chat_endpoints(self):
        """Test chat endpoint constants."""
        assert ChatEndpoints.COMPLETIONS == "chat/completions"
        assert ChatEndpoints.RESPONSES == "/responses"

    def test_account_endpoints(self):
        """Test account endpoint constants."""
        assert AccountEndpoints.API_KEYS == "/api_keys"
        assert AccountEndpoints.API_KEYS_GENERATE_WEB3 == "/api_keys/generate_web3_key"
        assert AccountEndpoints.API_KEYS_RATE_LIMITS == "/api_keys/rate_limits"
        assert AccountEndpoints.API_KEYS_RATE_LIMITS_LOG == "/api_keys/rate_limits/log"
        assert AccountEndpoints.BILLING_USAGE == "/billing/usage"
        assert AccountEndpoints.BILLING_BALANCE == "/billing/balance"
        assert AccountEndpoints.BILLING_USAGE_ANALYTICS == "/billing/usage-analytics"
        assert AccountEndpoints.BILLING_USAGE_HISTORY == "/billing/usage-history"
        # Legacy alias now points at balance (summary path removed from Venice).
        assert AccountEndpoints.BILLING_SUMMARY == "/billing/balance"

    def test_audio_endpoints(self):
        """Test audio endpoint constants."""
        assert AudioEndpoints.SPEECH == "/audio/speech"
        assert AudioEndpoints.TRANSCRIPTIONS == "/audio/transcriptions"
        assert AudioEndpoints.VOICES == "/audio/voices"

    def test_characters_endpoints(self):
        """Test characters endpoint constants."""
        assert CharactersEndpoints.CHARACTERS == "/characters"

    def test_embeddings_endpoints(self):
        """Test embeddings endpoint constants."""
        assert EmbeddingsEndpoints.EMBEDDINGS == "/embeddings"

    def test_models_endpoints(self):
        """Test models endpoint constants."""
        assert ModelsEndpoints.MODELS == "models"
        assert ModelsEndpoints.MODELS_TRAITS == "/models/traits"
        assert ModelsEndpoints.MODELS_COMPATIBILITY_MAPPING == "/models/compatibility_mapping"

    def test_video_endpoints(self):
        assert VideoEndpoints.TRANSCRIPTIONS == "/video/transcriptions"

    def test_augment_crypto_x402_tee(self):
        assert AugmentEndpoints.SEARCH == "/augment/search"
        assert AugmentEndpoints.SCRAPE == "/augment/scrape"
        assert AugmentEndpoints.TEXT_PARSER == "/augment/text-parser"
        assert CryptoEndpoints.NETWORKS == "/crypto/rpc/networks"
        assert CryptoEndpoints.RPC == "/crypto/rpc/{network}"
        assert X402Endpoints.TOP_UP == "/x402/top-up"
        assert TEEEndpoints.ATTESTATION == "/tee/attestation"
