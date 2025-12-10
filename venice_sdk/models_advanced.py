"""
Venice AI SDK - Advanced Models Module

This module provides advanced model capabilities including traits and compatibility mapping.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

from .client import HTTPClient
from ._http import ensure_http_client
from .errors import VeniceAPIError, ModelNotFoundError
from .config import load_config


@dataclass
class ModelTraits:
    """Represents detailed traits and capabilities of a model."""
    model_id: str
    capabilities: Dict[str, Any]
    traits: Dict[str, Any]
    performance_metrics: Optional[Dict[str, Any]] = None
    supported_formats: Optional[List[str]] = None
    context_length: Optional[int] = None
    max_tokens: Optional[int] = None
    temperature_range: Optional[Tuple[float, float]] = None
    languages: Optional[List[str]] = None
    
    def has_capability(self, capability: str) -> bool:
        """Check if model has a specific capability."""
        return capability in self.capabilities
    
    def get_capability_value(self, capability: str, default: Any = None) -> Any:
        """Get the value of a specific capability."""
        return self.capabilities.get(capability, default)
    
    def has_trait(self, trait: str) -> bool:
        """Check if model has a specific trait."""
        return trait in self.traits
    
    def get_trait_value(self, trait: str, default: Any = None) -> Any:
        """Get the value of a specific trait."""
        return self.traits.get(trait, default)
    
    def supports_function_calling(self) -> bool:
        """Check if model supports function calling."""
        return self.has_capability("function_calling") or self.has_trait("function_calling")
    
    def supports_streaming(self) -> bool:
        """Check if model supports streaming."""
        return self.has_capability("streaming") or self.has_trait("streaming")
    
    def supports_web_search(self) -> bool:
        """Check if model supports web search."""
        return self.has_capability("web_search") or self.has_trait("web_search")
    
    def supports_vision(self) -> bool:
        """Check if model supports vision/image processing."""
        return self.has_capability("vision") or self.has_trait("vision")
    
    def supports_audio(self) -> bool:
        """Check if model supports audio processing."""
        return self.has_capability("audio") or self.has_trait("audio")


@dataclass
class CompatibilityMapping:
    """Represents model compatibility mapping between different providers."""
    openai_to_venice: Dict[str, str]
    venice_to_openai: Dict[str, str]
    provider_mappings: Dict[str, Dict[str, str]]
    
    def get_venice_model(self, openai_model: str) -> Optional[str]:
        """Get Venice model equivalent for OpenAI model."""
        return self.openai_to_venice.get(openai_model)
    
    def get_openai_model(self, venice_model: str) -> Optional[str]:
        """Get OpenAI model equivalent for Venice model."""
        return self.venice_to_openai.get(venice_model)
    
    def get_provider_model(self, provider: str, model: str) -> Optional[str]:
        """Get model equivalent for a specific provider."""
        if provider in self.provider_mappings:
            return self.provider_mappings[provider].get(model)
        return None
    
    def list_available_mappings(self) -> List[str]:
        """List all available provider mappings."""
        return list(self.provider_mappings.keys())


def _to_temperature_range(raw: Any) -> Optional[Tuple[float, float]]:
    """Coerce API temperature ranges into a typed tuple."""
    if isinstance(raw, (list, tuple)) and len(raw) >= 2:
        try:
            return float(raw[0]), float(raw[1])
        except (TypeError, ValueError):
            return None
    return None


def _recommendation_score(entry: Dict[str, Any]) -> float:
    """Safely extract a numeric score from a recommendation dictionary."""
    score = entry.get("score", 0.0)
    try:
        return float(score)
    except (TypeError, ValueError):
        return 0.0


class ModelsTraitsAPI:
    """Advanced model traits API client."""
    
    def __init__(self, client: HTTPClient):
        self.client = client
        self._traits_cache: Dict[str, ModelTraits] = {}
    
    def get_traits(self, use_cache: bool = True) -> Dict[str, ModelTraits]:
        """
        Get detailed traits for all models.

        Args:
            use_cache: Whether to use cached results

        Returns:
            Dictionary mapping model IDs to ModelTraits objects
        """
        if use_cache and self._traits_cache is not None and len(self._traits_cache) > 0:
            return self._traits_cache

        # Use the regular models endpoint since /models/traits doesn't exist
        response = self.client.get("/models")
        result = response.json()

        if not isinstance(result, dict) or "data" not in result:
            raise ModelNotFoundError("Invalid response format from models endpoint")

        traits = {}
        # Extract traits from the models data
        for model_data in result["data"]:
            model_id = model_data.get("id")
            if not model_id:
                continue
                
            model_spec = model_data.get("model_spec", {})
            capabilities = model_spec.get("capabilities", {})
            traits_list = model_spec.get("traits", [])
            context_length = model_spec.get("availableContextTokens")
            
            # Convert traits to dict
            model_traits = {}
            if isinstance(traits_list, dict):
                # If traits is already a dict, use it directly
                model_traits = traits_list
            elif isinstance(traits_list, list):
                # If traits is a list, convert it
                for trait in traits_list:
                    if isinstance(trait, str):
                        model_traits[trait] = True
                    elif isinstance(trait, dict):
                        model_traits.update(trait)
                    else:
                        # Handle other types
                        model_traits[str(trait)] = trait
            
            traits[model_id] = ModelTraits(
                model_id=model_id,
                capabilities=capabilities,
                traits=model_traits,
                performance_metrics=None,
                supported_formats=None,
                context_length=context_length,
                max_tokens=None,
                temperature_range=None,
                languages=None
            )

        if use_cache:
            self._traits_cache = traits

        return traits
    
    def get_model_traits(self, model_id: str, use_cache: bool = True) -> Optional[ModelTraits]:
        """
        Get traits for a specific model.
        
        Args:
            model_id: Model identifier
            use_cache: Whether to use cached results
            
        Returns:
            ModelTraits object or None if not found
        """
        all_traits = self.get_traits(use_cache=use_cache)
        return all_traits.get(model_id)
    
    def get_capabilities(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get capabilities for a specific model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Capabilities dictionary or None if not found
        """
        traits = self.get_model_traits(model_id)
        return traits.capabilities if traits else None
    
    def get_traits_dict(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get traits dictionary for a specific model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Traits dictionary or None if not found
        """
        traits = self.get_model_traits(model_id)
        return traits.traits if traits else None
    
    def find_models_by_capability(self, capability: str) -> List[str]:
        """
        Find models that have a specific capability.
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of model IDs with the capability
        """
        all_traits = self.get_traits()
        matching_models = []
        
        for model_id, traits in all_traits.items():
            if traits.has_capability(capability):
                matching_models.append(model_id)
        
        return matching_models
    
    def find_models_by_trait(self, trait: str) -> List[str]:
        """
        Find models that have a specific trait.
        
        Args:
            trait: Trait to search for
            
        Returns:
            List of model IDs with the trait
        """
        all_traits = self.get_traits()
        matching_models = []
        
        for model_id, traits in all_traits.items():
            if traits.has_trait(trait):
                matching_models.append(model_id)
        
        return matching_models
    
    def get_models_by_type(self, model_type: str) -> List[str]:
        """
        Get models of a specific type.
        
        Args:
            model_type: Type of model (e.g., "text", "image", "audio")
            
        Returns:
            List of model IDs of the specified type
        """
        all_traits = self.get_traits()
        matching_models = []
        
        for model_id, traits in all_traits.items():
            if traits.get_capability_value("type") == model_type:
                matching_models.append(model_id)
        
        return matching_models
    
    def get_best_models_for_task(self, task: str) -> List[str]:
        """
        Get best models for a specific task.
        
        Args:
            task: Task description
            
        Returns:
            List of model IDs ranked by suitability for the task
        """
        # Define task-to-capability mapping
        task_capabilities = {
            "chat": ["supportsFunctionCalling", "supportsWebSearch", "supportsLogProbs"],
            "image_generation": ["supportsVision"],
            "text_to_speech": ["supportsAudio"],
            "embeddings": ["supportsEmbeddings"],
            "code_generation": ["optimizedForCode", "supportsFunctionCalling"],
            "translation": ["supportsMultilingual"],
            "summarization": ["supportsTextProcessing"],
            "question_answering": ["supportsWebSearch", "supportsReasoning"]
        }
        
        task_lower = task.lower()
        required_capabilities = []
        
        for task_name, capabilities in task_capabilities.items():
            if task_name in task_lower:
                required_capabilities.extend(capabilities)
        
        if not required_capabilities:
            # Default to general text capabilities
            required_capabilities = ["text_generation", "chat"]
        
        all_traits = self.get_traits()
        scored_models: List[Tuple[str, int]] = []
        
        for model_id, traits in all_traits.items():
            score = 0
            for capability in required_capabilities:
                if traits.has_capability(capability):
                    score += 1
            
            if score > 0:
                scored_models.append((model_id, score))
        
        # Sort by score (descending) and return model IDs
        scored_models.sort(key=lambda item: item[1], reverse=True)
        return [model_id for model_id, _ in scored_models]
    
    def clear_cache(self) -> None:
        """Clear the traits cache."""
        self._traits_cache.clear()
    
    def _parse_model_traits(self, model_id: str, data: Dict[str, Any]) -> ModelTraits:
        """Parse model traits from API response."""
        return ModelTraits(
            model_id=model_id,
            capabilities=data.get("capabilities", {}),
            traits=data.get("traits", {}),
            performance_metrics=data.get("performance_metrics"),
            supported_formats=data.get("supported_formats"),
            context_length=data.get("context_length"),
            max_tokens=data.get("max_tokens"),
            temperature_range=_to_temperature_range(data.get("temperature_range")),
            languages=data.get("languages")
        )


class ModelsCompatibilityAPI:
    """Model compatibility mapping API client."""
    
    def __init__(self, client: HTTPClient):
        self.client = client
        self._mapping_cache: Optional[CompatibilityMapping] = None
    
    def get_mapping(self, use_cache: bool = True) -> CompatibilityMapping:
        """
        Get model compatibility mapping.
        
        Args:
            use_cache: Whether to use cached results
            
        Returns:
            CompatibilityMapping object
        """
        if use_cache and self._mapping_cache:
            return self._mapping_cache
        
        response = self.client.get("/models/compatibility_mapping")
        result = response.json()
        
        if "data" not in result:
            raise ModelNotFoundError("Invalid response format from compatibility mapping endpoint")
        
        data = result["data"]
        mapping = CompatibilityMapping(
            openai_to_venice=data.get("openai_to_venice", {}),
            venice_to_openai=data.get("venice_to_openai", {}),
            provider_mappings=data.get("provider_mappings", {})
        )
        
        if use_cache:
            self._mapping_cache = mapping
        
        return mapping
    
    def get_venice_model(self, openai_model: str) -> Optional[str]:
        """
        Get Venice model equivalent for OpenAI model.
        
        Args:
            openai_model: OpenAI model name
            
        Returns:
            Venice model name or None if not found
        """
        mapping = self.get_mapping()
        return mapping.get_venice_model(openai_model)
    
    def get_openai_model(self, venice_model: str) -> Optional[str]:
        """
        Get OpenAI model equivalent for Venice model.
        
        Args:
            venice_model: Venice model name
            
        Returns:
            OpenAI model name or None if not found
        """
        mapping = self.get_mapping()
        return mapping.get_openai_model(venice_model)
    
    def migrate_openai_models(self, models: List[str]) -> Dict[str, str]:
        """
        Migrate a list of OpenAI models to Venice equivalents.
        
        Args:
            models: List of OpenAI model names
            
        Returns:
            Dictionary mapping OpenAI models to Venice models
        """
        mapping = self.get_mapping()
        migrated = {}
        
        for model in models:
            venice_model = mapping.get_venice_model(model)
            if venice_model:
                migrated[model] = venice_model
        
        return migrated
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available provider mappings.
        
        Returns:
            List of provider names
        """
        try:
            mapping = self.get_mapping()
            return list(mapping.provider_mappings.keys())
        except Exception:
            # Fallback to basic provider list
            return ["openai", "anthropic", "google", "cohere", "huggingface"]
    
    def clear_cache(self) -> None:
        """Clear the mapping cache."""
        self._mapping_cache = None


class ModelRecommendationEngine:
    """Advanced model recommendation engine."""
    
    def __init__(self, traits_api: ModelsTraitsAPI, compatibility_api: ModelsCompatibilityAPI):
        self.traits_api = traits_api
        self.compatibility_api = compatibility_api
    
    def recommend_models(
        self,
        task: str,
        requirements: Optional[Dict[str, Any]] = None,
        budget_constraint: Optional[str] = None,
        performance_priority: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Recommend models based on task and requirements.
        
        Args:
            task: Task description
            requirements: Specific requirements dictionary
            budget_constraint: Budget constraint level ("low", "medium", "high")
            performance_priority: Performance priority ("speed", "quality", "balanced")
            
        Returns:
            List of model recommendations with scores
        """
        # Get best models for the task
        best_models = self.traits_api.get_best_models_for_task(task)
        
        if not best_models:
            return []
        
        # Get traits for all models
        all_traits = self.traits_api.get_traits()
        recommendations: List[Dict[str, Any]] = []
        
        for model_id in best_models:
            if model_id not in all_traits:
                continue
            
            traits = all_traits[model_id]
            score = self._calculate_recommendation_score(
                traits, task, requirements, budget_constraint, performance_priority
            )
            
            recommendations.append({
                "model_id": model_id,
                "score": score,
                "capabilities": traits.capabilities,
                "traits": traits.traits,
                "context_length": traits.context_length,
                "max_tokens": traits.max_tokens
            })
        
        # Sort by score (descending)
        recommendations.sort(key=_recommendation_score, reverse=True)
        return recommendations
    
    def _calculate_recommendation_score(
        self,
        traits: ModelTraits,
        task: str,
        requirements: Optional[Dict[str, Any]],
        budget_constraint: Optional[str],
        performance_priority: Optional[str]
    ) -> float:
        """Calculate recommendation score for a model."""
        score = 0.0
        
        # Base score from task matching
        task_models = self.traits_api.get_best_models_for_task(task)
        if traits.model_id in task_models:
            score += 10.0
        
        # Requirements matching
        if requirements:
            for req_key, req_value in requirements.items():
                if traits.has_capability(req_key) and traits.get_capability_value(req_key) == req_value:
                    score += 5.0
                elif traits.has_trait(req_key) and traits.get_trait_value(req_key) == req_value:
                    score += 5.0
        
        # Budget constraint scoring
        if budget_constraint:
            cost_trait = traits.get_trait_value("cost_level", "medium")
            if budget_constraint == "low" and cost_trait == "low":
                score += 3.0
            elif budget_constraint == "medium" and cost_trait in ["low", "medium"]:
                score += 2.0
            elif budget_constraint == "high":
                score += 1.0
        
        # Performance priority scoring
        if performance_priority:
            speed_trait = traits.get_trait_value("speed", "medium")
            quality_trait = traits.get_trait_value("quality", "medium")
            
            if performance_priority == "speed" and speed_trait == "high":
                score += 3.0
            elif performance_priority == "quality" and quality_trait == "high":
                score += 3.0
            elif performance_priority == "balanced":
                score += 2.0
        
        return score


# Convenience functions
def get_model_traits(
    model_id: str,
    client: Optional[HTTPClient] = None
) -> Optional[ModelTraits]:
    """Convenience function to get model traits."""
    http_client = ensure_http_client(client)
    api = ModelsTraitsAPI(http_client)
    return api.get_model_traits(model_id)


def get_compatibility_mapping(
    client: Optional[HTTPClient] = None
) -> CompatibilityMapping:
    """Convenience function to get compatibility mapping."""
    http_client = ensure_http_client(client)
    api = ModelsCompatibilityAPI(http_client)
    return api.get_mapping()


def find_models_by_capability(
    capability: str,
    client: Optional[HTTPClient] = None
) -> List[str]:
    """Convenience function to find models by capability."""
    http_client = ensure_http_client(client)
    api = ModelsTraitsAPI(http_client)
    return api.find_models_by_capability(capability)
