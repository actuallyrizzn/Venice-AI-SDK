"""
Model discovery and management for the Venice SDK.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from .client import HTTPClient


@dataclass
class ModelCapabilities:
    """Capabilities of a model."""
    supports_function_calling: bool
    supports_web_search: bool
    available_context_tokens: int


@dataclass
class Model:
    """Information about a Venice model."""
    id: str
    name: str
    type: str
    capabilities: ModelCapabilities
    description: Optional[str] = None


class ModelsAPI:
    """API for model discovery and management."""
    
    def __init__(self, client: HTTPClient):
        """
        Initialize the models API.
        
        Args:
            client: HTTPClient instance
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
        response = self.client.get(f"models/{model_id}")
        return response.json()
    
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
        except:  # noqa: E722
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
        if model_data["type"] != "text":
            continue
            
        capabilities = ModelCapabilities(
            supports_function_calling=model_data["model_spec"]["capabilities"]["supportsFunctionCalling"],
            supports_web_search=model_data["model_spec"]["capabilities"]["supportsWebSearch"],
            available_context_tokens=model_data["model_spec"]["capabilities"]["availableContextTokens"]
        )
        
        model = Model(
            id=model_data["id"],
            name=model_data["name"],
            type=model_data["type"],
            capabilities=capabilities,
            description=model_data.get("description")
        )
        models.append(model)
    
    return models


def get_model_by_id(model_id: str, client: Optional[HTTPClient] = None) -> Optional[Model]:
    """
    Get a specific model by ID.
    
    Args:
        model_id: The ID of the model to get.
        client: Optional HTTPClient instance. If not provided, a new one will be created.
        
    Returns:
        The model if found, None otherwise.
    """
    models = get_models(client)
    for model in models:
        if model.id == model_id:
            return model
    return None


def get_text_models(client: Optional[HTTPClient] = None) -> List[Model]:
    """
    Get a list of available text models.
    
    Args:
        client: Optional HTTPClient instance. If not provided, a new one will be created.
        
    Returns:
        List of available text models.
    """
    return [model for model in get_models(client) if model.type == "text"] 