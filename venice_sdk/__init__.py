"""
Venice SDK for Python.

This module provides a comprehensive Python interface to the Venice AI API.
"""

import logging

from .client import HTTPClient
from .venice_client import VeniceClient, create_client
from .config import Config, load_config
from .errors import (
    VeniceError,
    VeniceAPIError,
    VeniceConnectionError,
    RateLimitError,
    UnauthorizedError,
    InsufficientBalanceError,
    InvalidRequestError,
    ModelNotFoundError,
    CharacterNotFoundError,
    ImageGenerationError,
    AudioGenerationError,
    VideoGenerationError,
    BillingError,
    APIKeyError,
    EmbeddingError,
)
from .models import (
    Model,
    ModelCapabilities,
    ModelsAPI,
    get_models,
    get_model_by_id,
    get_text_models,
)
from .chat import (
    Message,
    Choice,
    Usage,
    ChatCompletion,
    ChatAPI,
    chat_complete,
)
from .images import (
    ImageGeneration,
    ImageEditResult,
    ImageUpscaleResult,
    ImageStyle,
    ImageAPI,
    ImageEditAPI,
    ImageUpscaleAPI,
    ImageStylesAPI,
    generate_image,
    edit_image,
    upscale_image,
)
from .audio import (
    Voice,
    AudioResult,
    AudioAPI,
    AudioBatchProcessor,
    text_to_speech,
    text_to_speech_file,
)
from .video import (
    VideoMetadata,
    VideoJob,
    VideoQuote,
    VideoAPI,
)
from .characters import (
    Character,
    CharactersAPI,
    CharacterManager,
    get_character,
    list_characters,
    search_characters,
)
from .account import (
    APIKey,
    Web3APIKey,
    RateLimits,
    RateLimitLog,
    UsageInfo,
    ModelUsage,
    APIKeysAPI,
    BillingAPI,
    AccountManager,
    get_account_usage,
    get_rate_limits,
    list_api_keys,
)
from .models_advanced import (
    ModelTraits,
    CompatibilityMapping,
    ModelsTraitsAPI,
    ModelsCompatibilityAPI,
    ModelRecommendationEngine,
    get_model_traits,
    get_compatibility_mapping,
    find_models_by_capability,
)
from .embeddings import (
    Embedding,
    EmbeddingResult,
    EmbeddingsAPI,
    EmbeddingSimilarity,
    SemanticSearch,
    EmbeddingClustering,
    generate_embedding,
    calculate_similarity,
    generate_embeddings,
)
from .logging_config import setup_logging

_root_logger = logging.getLogger("venice_sdk")
if not any(isinstance(handler, logging.NullHandler) for handler in _root_logger.handlers):
    _root_logger.addHandler(logging.NullHandler())

__version__ = "0.2.1"

__all__ = [
    # Core client
    "HTTPClient",
    "VeniceClient",
    "create_client",
    "Config",
    "load_config",
    
    # Errors
    "VeniceError",
    "VeniceAPIError",
    "VeniceConnectionError",
    "RateLimitError",
    "UnauthorizedError",
    "InsufficientBalanceError",
    "InvalidRequestError",
    "ModelNotFoundError",
    "CharacterNotFoundError",
    "ImageGenerationError",
    "AudioGenerationError",
    "VideoGenerationError",
    "BillingError",
    "APIKeyError",
    "EmbeddingError",
    
    # Models
    "Model",
    "ModelCapabilities",
    "ModelsAPI",
    "get_models",
    "get_model_by_id",
    "get_text_models",
    
    # Chat
    "Message",
    "Choice",
    "Usage",
    "ChatCompletion",
    "ChatAPI",
    "chat_complete",
    
    # Images
    "ImageGeneration",
    "ImageEditResult",
    "ImageUpscaleResult",
    "ImageStyle",
    "ImageAPI",
    "ImageEditAPI",
    "ImageUpscaleAPI",
    "ImageStylesAPI",
    "generate_image",
    "edit_image",
    "upscale_image",
    
    # Audio
    "Voice",
    "AudioResult",
    "AudioAPI",
    "AudioBatchProcessor",
    "text_to_speech",
    "text_to_speech_file",
    
    # Video
    "VideoMetadata",
    "VideoJob",
    "VideoQuote",
    "VideoAPI",
    
    # Characters
    "Character",
    "CharactersAPI",
    "CharacterManager",
    "get_character",
    "list_characters",
    "search_characters",
    
    # Account
    "APIKey",
    "Web3APIKey",
    "RateLimits",
    "RateLimitLog",
    "UsageInfo",
    "ModelUsage",
    "APIKeysAPI",
    "BillingAPI",
    "AccountManager",
    "get_account_usage",
    "get_rate_limits",
    "list_api_keys",
    
    # Advanced Models
    "ModelTraits",
    "CompatibilityMapping",
    "ModelsTraitsAPI",
    "ModelsCompatibilityAPI",
    "ModelRecommendationEngine",
    "get_model_traits",
    "get_compatibility_mapping",
    "find_models_by_capability",
    
    # Embeddings
    "Embedding",
    "EmbeddingResult",
    "EmbeddingsAPI",
    "EmbeddingSimilarity",
    "SemanticSearch",
    "EmbeddingClustering",
    "generate_embedding",
    "calculate_similarity",
    "generate_embeddings",

    # Logging
    "setup_logging",
] 