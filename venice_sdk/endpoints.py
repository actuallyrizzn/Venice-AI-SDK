"""
API endpoint constants for the Venice SDK.

This module contains centralized endpoint definitions to ensure consistency
across the SDK and make endpoint management easier.
"""


class ImageEndpoints:
    """Image-related API endpoints.

    Venice uses singular ``/image/...`` for native routes and plural
    ``/images/generations`` for the OpenAI-compatible generation alias.
    """

    GENERATIONS = "/images/generations"  # OpenAI-compatible
    GENERATE = "/image/generate"  # Venice-native
    EDIT = "/image/edit"
    MULTI_EDIT = "/image/multi-edit"
    BACKGROUND_REMOVE = "/image/background-remove"
    UPSCALE = "/image/upscale"
    STYLES = "/image/styles"


class ChatEndpoints:
    """Chat-related API endpoints."""

    COMPLETIONS = "chat/completions"
    RESPONSES = "/responses"


class AccountEndpoints:
    """Account-related API endpoints."""

    API_KEYS = "/api_keys"
    API_KEYS_GENERATE_WEB3 = "/api_keys/generate_web3_key"
    API_KEYS_RATE_LIMITS = "/api_keys/rate_limits"
    API_KEYS_RATE_LIMITS_LOG = "/api_keys/rate_limits/log"
    BILLING_USAGE = "/billing/usage"
    BILLING_BALANCE = "/billing/balance"
    BILLING_USAGE_ANALYTICS = "/billing/usage-analytics"
    BILLING_USAGE_HISTORY = "/billing/usage-history"
    # Removed from Venice API (404 as of 2026-08); kept as alias name only in older SDK docs.
    BILLING_SUMMARY = "/billing/balance"


class AudioEndpoints:
    """Audio-related API endpoints."""

    SPEECH = "/audio/speech"
    TRANSCRIPTIONS = "/audio/transcriptions"
    VOICES = "/audio/voices"
    QUEUE = "/audio/queue"
    RETRIEVE = "/audio/retrieve"
    QUOTE = "/audio/quote"
    COMPLETE = "/audio/complete"


class CharactersEndpoints:
    """Character-related API endpoints."""

    CHARACTERS = "/characters"


class EmbeddingsEndpoints:
    """Embedding-related API endpoints."""

    EMBEDDINGS = "/embeddings"


class ModelsEndpoints:
    """Model-related API endpoints."""

    MODELS = "models"
    MODELS_TRAITS = "/models/traits"
    MODELS_COMPATIBILITY_MAPPING = "/models/compatibility_mapping"


class VideoEndpoints:
    """Video-related API endpoints."""

    QUEUE = "/video/queue"
    RETRIEVE = "/video/retrieve"
    QUOTE = "/video/quote"
    COMPLETE = "/video/complete"
    TRANSCRIPTIONS = "/video/transcriptions"


class AugmentEndpoints:
    """Developer tools / augment endpoints."""

    SEARCH = "/augment/search"
    SCRAPE = "/augment/scrape"
    TEXT_PARSER = "/augment/text-parser"


class CryptoEndpoints:
    """Crypto RPC endpoints."""

    NETWORKS = "/crypto/rpc/networks"
    RPC = "/crypto/rpc/{network}"


class X402Endpoints:
    """x402 wallet authentication / credits endpoints."""

    BALANCE = "/x402/balance/{walletAddress}"
    TOP_UP = "/x402/top-up"
    TRANSACTIONS = "/x402/transactions/{walletAddress}"


class TEEEndpoints:
    """TEE (Trusted Execution Environment) API endpoints.

    Still served by Venice (live) though currently omitted from swagger.yaml.
    """

    ATTESTATION = "/tee/attestation"
    SIGNATURE = "/tee/signature"