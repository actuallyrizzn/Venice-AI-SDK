"""
Model discovery and management for the Venice SDK.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .client import HTTPClient
from .errors import VeniceAPIError


@dataclass
class ModelCapabilities:
    """Model capabilities."""
    supports_function_calling: bool
    supports_web_search: bool
    available_context_tokens: int


@dataclass
class Model:
    """Model information."""
    id: str
    name: str
    type: str
    capabilities: ModelCapabilities
    description: str
    display_name: Optional[str] = None


logger = logging.getLogger(__name__)


class ModelsAPI:
    """API client for model-related endpoints."""
    
    def __init__(self, client: HTTPClient):
        """
        Initialize the models API client.
        
        Args:
            client: HTTP client for making requests
        """
        self.client = client
    
    def list(self) -> List[Dict]:
        """
        Get a list of available models.
        
        Returns:
            List of model data
            
        Raises:
            VeniceAPIError: If the request fails
        """
        response = self.client.get("models")
        return response.json()["data"]
    
    def get(self, model_id: str) -> Dict:
        """
        Get a specific model by ID.
        
        Args:
            model_id: The ID of the model to get
            
        Returns:
            Model data
            
        Raises:
            VeniceAPIError: If the model is not found or request fails
        """
        models = self.list()
        for model in models:
            if model.get("id") == model_id:
                return model
        raise VeniceAPIError(f"Model {model_id} not found", status_code=404)
    
    def validate(self, model_id: str) -> bool:
        """
        Validate that a model exists.
        
        Args:
            model_id: The ID of the model to validate
            
        Returns:
            True if the model exists, False otherwise
        """
        try:
            self.get(model_id)
            return True
        except Exception:
            return False


def get_models(client: Optional[HTTPClient] = None) -> List[Model]:
    """
    Get a list of available models.
    
    Args:
        client: Optional HTTPClient instance. If not provided, a new one will be created.
        
    Returns:
        List of available models.
        
    Raises:
        VeniceAPIError: If the request fails.
    """
    client = client or HTTPClient()
    models_api = ModelsAPI(client)
    models_data = models_api.list()
    
    models = []
    for model_data in models_data:
        models.append(_build_model_from_data(model_data))
    
    return models


def get_model_by_id(model_id: str, client: Optional[HTTPClient] = None) -> Optional[Model]:
    """
    Get a specific model by ID.
    
    Args:
        model_id: The ID of the model to get
        client: Optional HTTPClient instance. If not provided, a new one will be created.
        
    Returns:
        Model if found, None otherwise.
    """
    client = client or HTTPClient()
    models_api = ModelsAPI(client)
    model_data = models_api.get(model_id)
    return _build_model_from_data(model_data)


def get_text_models(client: Optional[HTTPClient] = None) -> List[Model]:
    """
    Get a list of available text models.
    
    Args:
        client: Optional HTTPClient instance. If not provided, a new one will be created.
        
    Returns:
        List of available text models.
    """
    return [model for model in get_models(client) if model.type == "text"] 


def _build_model_from_data(model_data: Dict[str, Any]) -> Model:
    """
    Build a Model object from raw API data using defensive defaults.
    """
    if not isinstance(model_data, dict):
        raise VeniceAPIError("Invalid model payload returned by API.", status_code=500)
    
    model_id = model_data.get("id")
    model_type = model_data.get("type")
    if not model_id or not model_type:
        raise VeniceAPIError("Model payload missing required `id` or `type` fields.", status_code=500)
    
    model_spec = model_data.get("model_spec") or {}
    if "model_spec" not in model_data:
        logger.debug("Model %s missing model_spec; falling back to defaults.", model_id)
    
    capabilities_data = model_spec.get("capabilities") or {}
    if not capabilities_data:
        logger.debug("Model %s missing capabilities; defaulting capability flags.", model_id)
    
    supports_function_calling = _get_capability_bool(capabilities_data, "supportsFunctionCalling", model_id)
    supports_web_search = _get_capability_bool(capabilities_data, "supportsWebSearch", model_id)
    available_context_tokens = _get_available_context_tokens(model_spec, model_id)
    
    description = (
        model_data.get("description")
        or model_spec.get("modelSource")
        or "No description available"
    )
    
    raw_name = model_data.get("name")

    return Model(
        id=model_id,
        name=model_id,
        type=model_type,
        capabilities=ModelCapabilities(
            supports_function_calling=supports_function_calling,
            supports_web_search=supports_web_search,
            available_context_tokens=available_context_tokens,
        ),
        description=description,
        display_name=raw_name or model_id,
    )


def _get_capability_bool(capabilities: Dict[str, Any], field: str, model_id: str) -> bool:
    value = capabilities.get(field)
    if value is None:
        logger.debug(
            "Model %s missing capability `%s`; defaulting to False.",
            model_id,
            field,
        )
        return False
    return bool(value)


def _get_available_context_tokens(model_spec: Dict[str, Any], model_id: str) -> int:
    raw_value = model_spec.get("availableContextTokens")
    if raw_value is None:
        logger.debug(
            "Model %s missing availableContextTokens; defaulting to 0.",
            model_id,
        )
        return 0
    try:
        return int(raw_value)
    except (TypeError, ValueError):
        logger.debug(
            "Model %s provided invalid availableContextTokens=%r; defaulting to 0.",
            model_id,
            raw_value,
        )
        return 0
