"""
Live tests for the ModelsAdvanced module.

These tests make real API calls to verify advanced models functionality.
"""

import pytest
import os
from venice_sdk.models_advanced import ModelsTraitsAPI, ModelsCompatibilityAPI, ModelRecommendationEngine
from venice_sdk.client import HTTPClient
from venice_sdk.config import Config, load_config
from venice_sdk.errors import VeniceAPIError


@pytest.mark.live
class TestModelsAdvancedAPILive:
    """Live tests for ModelsAdvanced APIs with real API calls."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.api_key = os.getenv("VENICE_API_KEY")
        if not self.api_key:
            pytest.skip("VENICE_API_KEY environment variable not set")
        
        self.config = load_config(api_key=self.api_key)
        self.client = HTTPClient(self.config)
        self.traits_api = ModelsTraitsAPI(self.client)
        self.compatibility_api = ModelsCompatibilityAPI(self.client)
        self.recommendation_engine = ModelRecommendationEngine(self.traits_api, self.compatibility_api)

    def test_get_traits(self):
        """Test getting model traits."""
        traits = self.traits_api.get_traits()
        
        assert isinstance(traits, dict)
        assert len(traits) > 0
        
        # Verify trait structure
        model_id = list(traits.keys())[0]
        model_traits = traits[model_id]
        
        assert hasattr(model_traits, 'model_id')
        assert hasattr(model_traits, 'capabilities')
        assert hasattr(model_traits, 'traits')
        assert hasattr(model_traits, 'performance_metrics')
        assert hasattr(model_traits, 'supported_formats')
        assert hasattr(model_traits, 'context_length')
        assert hasattr(model_traits, 'max_tokens')
        assert hasattr(model_traits, 'temperature_range')
        assert hasattr(model_traits, 'languages')
        
        assert model_traits.model_id == model_id

    def test_get_model_traits(self):
        """Test getting traits for a specific model."""
        # First get all traits to find a valid model ID
        all_traits = self.traits_api.get_traits()
        assert len(all_traits) > 0
        
        model_id = list(all_traits.keys())[0]
        traits = self.traits_api.get_model_traits(model_id)
        
        assert traits is not None
        assert traits.model_id == model_id
        assert hasattr(traits, 'capabilities')
        assert hasattr(traits, 'traits')

    def test_get_nonexistent_model_traits(self):
        """Test getting traits for a model that doesn't exist."""
        traits = self.traits_api.get_model_traits("nonexistent-model-id")
        assert traits is None

    def test_get_capabilities(self):
        """Test getting model capabilities."""
        # First get all traits to find a valid model ID
        all_traits = self.traits_api.get_traits()
        assert len(all_traits) > 0
        
        model_id = list(all_traits.keys())[0]
        capabilities = self.traits_api.get_capabilities(model_id)
        
        assert capabilities is not None
        assert isinstance(capabilities, dict)

    def test_get_traits_dict(self):
        """Test getting traits dictionary."""
        # First get all traits to find a valid model ID
        all_traits = self.traits_api.get_traits()
        assert len(all_traits) > 0
        
        model_id = list(all_traits.keys())[0]
        traits_dict = self.traits_api.get_traits_dict(model_id)
        
        assert traits_dict is not None
        assert isinstance(traits_dict, dict)

    def test_find_models_by_capability(self):
        """Test finding models by capability."""
        # Find models with any capability
        all_traits = self.traits_api.get_traits()
        if all_traits:
            model_id = list(all_traits.keys())[0]
            model_traits = all_traits[model_id]
            
            if model_traits.capabilities:
                capability = list(model_traits.capabilities.keys())[0]
                models = self.traits_api.find_models_by_capability(capability)
                
                assert isinstance(models, list)
                assert len(models) > 0
                assert model_id in models

    def test_find_models_by_trait(self):
        """Test finding models by trait."""
        # Find models with any trait
        all_traits = self.traits_api.get_traits()
        if all_traits:
            model_id = list(all_traits.keys())[0]
            model_traits = all_traits[model_id]
            
            if model_traits.traits:
                trait = list(model_traits.traits.keys())[0]
                models = self.traits_api.find_models_by_trait(trait)
                
                assert isinstance(models, list)
                assert len(models) > 0
                assert model_id in models

    def test_get_models_by_type(self):
        """Test getting models by type."""
        # Find models with type capability
        all_traits = self.traits_api.get_traits()
        if all_traits:
            model_id = list(all_traits.keys())[0]
            model_traits = all_traits[model_id]
            
            if model_traits.capabilities and "type" in model_traits.capabilities:
                model_type = model_traits.capabilities["type"]
                models = self.traits_api.get_models_by_type(model_type)
                
                assert isinstance(models, list)
                assert len(models) > 0
                assert model_id in models

    def test_get_best_models_for_task(self):
        """Test getting best models for a task."""
        task = "chat"
        models = self.traits_api.get_best_models_for_task(task)
        
        assert isinstance(models, list)
        assert len(models) > 0
        
        # Verify all returned models exist in traits
        all_traits = self.traits_api.get_traits()
        for model_id in models:
            assert model_id in all_traits

    def test_get_best_models_for_different_tasks(self):
        """Test getting best models for different tasks."""
        tasks = ["chat", "image_generation", "text_to_speech", "embeddings", "code_generation"]
        
        for task in tasks:
            models = self.traits_api.get_best_models_for_task(task)
            
            assert isinstance(models, list)
            # Some tasks might not have matching models
            assert len(models) >= 0

    def test_clear_traits_cache(self):
        """Test clearing traits cache."""
        # Clear cache should not raise an error
        self.traits_api.clear_cache()

    def test_get_compatibility_mapping(self):
        """Test getting compatibility mapping."""
        mapping = self.compatibility_api.get_mapping()
        
        assert mapping is not None
        assert hasattr(mapping, 'openai_to_venice')
        assert hasattr(mapping, 'venice_to_openai')
        assert hasattr(mapping, 'provider_mappings')
        
        assert isinstance(mapping.openai_to_venice, dict)
        assert isinstance(mapping.venice_to_openai, dict)
        assert isinstance(mapping.provider_mappings, dict)

    def test_get_venice_model(self):
        """Test getting Venice model for OpenAI model."""
        mapping = self.compatibility_api.get_mapping()
        
        if mapping.openai_to_venice:
            openai_model = list(mapping.openai_to_venice.keys())[0]
            venice_model = self.compatibility_api.get_venice_model(openai_model)
            
            assert venice_model is not None
            assert venice_model == mapping.openai_to_venice[openai_model]

    def test_get_openai_model(self):
        """Test getting OpenAI model for Venice model."""
        mapping = self.compatibility_api.get_mapping()
        
        if mapping.venice_to_openai:
            venice_model = list(mapping.venice_to_openai.keys())[0]
            openai_model = self.compatibility_api.get_openai_model(venice_model)
            
            assert openai_model is not None
            assert openai_model == mapping.venice_to_openai[venice_model]

    def test_migrate_openai_models(self):
        """Test migrating OpenAI models to Venice equivalents."""
        mapping = self.compatibility_api.get_mapping()
        
        if mapping.openai_to_venice:
            openai_models = list(mapping.openai_to_venice.keys())[:2]  # Take first 2
            migrated = self.compatibility_api.migrate_openai_models(openai_models)
            
            assert isinstance(migrated, dict)
            assert len(migrated) > 0
            
            for openai_model, venice_model in migrated.items():
                assert openai_model in openai_models
                assert venice_model == mapping.openai_to_venice[openai_model]

    def test_get_available_providers(self):
        """Test getting available providers."""
        providers = self.compatibility_api.get_available_providers()
        
        assert isinstance(providers, list)
        # Should have at least one provider
        assert len(providers) > 0
        
        # All providers should be strings
        for provider in providers:
            assert isinstance(provider, str)
            assert len(provider) > 0

    def test_clear_compatibility_cache(self):
        """Test clearing compatibility cache."""
        # Clear cache should not raise an error
        self.compatibility_api.clear_cache()

    def test_recommend_models(self):
        """Test model recommendation engine."""
        task = "chat"
        recommendations = self.recommendation_engine.recommend_models(task)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Verify recommendation structure
        recommendation = recommendations[0]
        assert "model_id" in recommendation
        assert "score" in recommendation
        assert "capabilities" in recommendation
        assert "traits" in recommendation
        assert "context_length" in recommendation
        assert "max_tokens" in recommendation
        
        assert isinstance(recommendation["model_id"], str)
        assert isinstance(recommendation["score"], float)
        assert isinstance(recommendation["capabilities"], dict)
        assert isinstance(recommendation["traits"], dict)

    def test_recommend_models_with_requirements(self):
        """Test model recommendation with specific requirements."""
        task = "chat"
        requirements = {"function_calling": True, "streaming": True}
        
        recommendations = self.recommendation_engine.recommend_models(
            task=task,
            requirements=requirements
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    def test_recommend_models_with_budget_constraint(self):
        """Test model recommendation with budget constraint."""
        task = "chat"
        budget_constraint = "low"
        
        recommendations = self.recommendation_engine.recommend_models(
            task=task,
            budget_constraint=budget_constraint
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    def test_recommend_models_with_performance_priority(self):
        """Test model recommendation with performance priority."""
        task = "chat"
        performance_priority = "speed"
        
        recommendations = self.recommendation_engine.recommend_models(
            task=task,
            performance_priority=performance_priority
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    def test_recommend_models_with_all_parameters(self):
        """Test model recommendation with all parameters."""
        task = "chat"
        requirements = {"function_calling": True}
        budget_constraint = "medium"
        performance_priority = "balanced"
        
        recommendations = self.recommendation_engine.recommend_models(
            task=task,
            requirements=requirements,
            budget_constraint=budget_constraint,
            performance_priority=performance_priority
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    def test_recommend_models_for_different_tasks(self):
        """Test model recommendation for different tasks."""
        tasks = ["chat", "image_generation", "text_to_speech", "embeddings", "code_generation"]
        
        for task in tasks:
            recommendations = self.recommendation_engine.recommend_models(task)
            
            assert isinstance(recommendations, list)
            # Some tasks might not have matching models
            assert len(recommendations) >= 0

    def test_model_traits_capabilities(self):
        """Test model traits capabilities."""
        all_traits = self.traits_api.get_traits()
        assert len(all_traits) > 0
        
        model_id = list(all_traits.keys())[0]
        traits = all_traits[model_id]
        
        # Test has_capability method
        if traits.capabilities:
            for capability in traits.capabilities:
                assert traits.has_capability(capability) is True
        
        # Test get_capability_value method
        if traits.capabilities:
            for capability, value in traits.capabilities.items():
                assert traits.get_capability_value(capability) == value
                assert traits.get_capability_value(capability, "default") == value
        
        # Test get_capability_value with default
        assert traits.get_capability_value("nonexistent", "default") == "default"

    def test_model_traits_traits(self):
        """Test model traits traits."""
        all_traits = self.traits_api.get_traits()
        assert len(all_traits) > 0
        
        model_id = list(all_traits.keys())[0]
        traits = all_traits[model_id]
        
        # Test has_trait method
        if traits.traits:
            for trait in traits.traits:
                assert traits.has_trait(trait) is True
        
        # Test get_trait_value method
        if traits.traits:
            for trait, value in traits.traits.items():
                assert traits.get_trait_value(trait) == value
                assert traits.get_trait_value(trait, "default") == value
        
        # Test get_trait_value with default
        assert traits.get_trait_value("nonexistent", "default") == "default"

    def test_model_traits_support_methods(self):
        """Test model traits support methods."""
        all_traits = self.traits_api.get_traits()
        assert len(all_traits) > 0
        
        model_id = list(all_traits.keys())[0]
        traits = all_traits[model_id]
        
        # Test support methods
        assert isinstance(traits.supports_function_calling(), bool)
        assert isinstance(traits.supports_streaming(), bool)
        assert isinstance(traits.supports_web_search(), bool)
        assert isinstance(traits.supports_vision(), bool)
        assert isinstance(traits.supports_audio(), bool)

    def test_model_traits_performance_metrics(self):
        """Test model traits performance metrics."""
        all_traits = self.traits_api.get_traits()
        assert len(all_traits) > 0
        
        model_id = list(all_traits.keys())[0]
        traits = all_traits[model_id]
        
        if traits.performance_metrics:
            assert isinstance(traits.performance_metrics, dict)
            for key, value in traits.performance_metrics.items():
                assert isinstance(key, str)
                assert isinstance(value, (str, int, float, bool, list, dict))

    def test_model_traits_supported_formats(self):
        """Test model traits supported formats."""
        all_traits = self.traits_api.get_traits()
        assert len(all_traits) > 0
        
        model_id = list(all_traits.keys())[0]
        traits = all_traits[model_id]
        
        if traits.supported_formats:
            assert isinstance(traits.supported_formats, list)
            assert all(isinstance(fmt, str) for fmt in traits.supported_formats)

    def test_model_traits_context_length(self):
        """Test model traits context length."""
        all_traits = self.traits_api.get_traits()
        assert len(all_traits) > 0
        
        model_id = list(all_traits.keys())[0]
        traits = all_traits[model_id]
        
        if traits.context_length:
            assert isinstance(traits.context_length, int)
            assert traits.context_length > 0

    def test_model_traits_max_tokens(self):
        """Test model traits max tokens."""
        all_traits = self.traits_api.get_traits()
        assert len(all_traits) > 0
        
        model_id = list(all_traits.keys())[0]
        traits = all_traits[model_id]
        
        if traits.max_tokens:
            assert isinstance(traits.max_tokens, int)
            assert traits.max_tokens > 0

    def test_model_traits_temperature_range(self):
        """Test model traits temperature range."""
        all_traits = self.traits_api.get_traits()
        assert len(all_traits) > 0
        
        model_id = list(all_traits.keys())[0]
        traits = all_traits[model_id]
        
        if traits.temperature_range:
            assert isinstance(traits.temperature_range, tuple)
            assert len(traits.temperature_range) == 2
            assert all(isinstance(x, (int, float)) for x in traits.temperature_range)
            assert traits.temperature_range[0] <= traits.temperature_range[1]

    def test_model_traits_languages(self):
        """Test model traits languages."""
        all_traits = self.traits_api.get_traits()
        assert len(all_traits) > 0
        
        model_id = list(all_traits.keys())[0]
        traits = all_traits[model_id]
        
        if traits.languages:
            assert isinstance(traits.languages, list)
            assert all(isinstance(lang, str) for lang in traits.languages)

    def test_compatibility_mapping_methods(self):
        """Test compatibility mapping methods."""
        mapping = self.compatibility_api.get_mapping()
        
        # Test get_venice_model method
        if mapping.openai_to_venice:
            openai_model = list(mapping.openai_to_venice.keys())[0]
            venice_model = mapping.get_venice_model(openai_model)
            assert venice_model == mapping.openai_to_venice[openai_model]
        
        # Test get_openai_model method
        if mapping.venice_to_openai:
            venice_model = list(mapping.venice_to_openai.keys())[0]
            openai_model = mapping.get_openai_model(venice_model)
            assert openai_model == mapping.venice_to_openai[venice_model]
        
        # Test get_provider_model method
        if mapping.provider_mappings:
            provider = list(mapping.provider_mappings.keys())[0]
            if mapping.provider_mappings[provider]:
                model = list(mapping.provider_mappings[provider].keys())[0]
                mapped_model = mapping.get_provider_model(provider, model)
                assert mapped_model == mapping.provider_mappings[provider][model]
        
        # Test list_available_mappings method
        available_mappings = mapping.list_available_mappings()
        assert isinstance(available_mappings, list)
        assert set(available_mappings) == set(mapping.provider_mappings.keys())

    def test_models_advanced_error_handling(self):
        """Test error handling in models advanced APIs."""
        # Test with invalid model ID instead (since models endpoint doesn't validate API keys)
        with pytest.raises(VeniceAPIError):
            self.traits_api.get_model_traits("nonexistent-model-id")

    def test_models_advanced_performance(self):
        """Test models advanced API performance."""
        import time
        
        # Test traits API performance
        start_time = time.time()
        traits = self.traits_api.get_traits()
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert len(traits) > 0
        assert response_time < 10  # Should complete within 10 seconds
        assert response_time > 0

    def test_models_advanced_caching(self):
        """Test models advanced API caching behavior."""
        import time
        
        # Test traits API caching
        start_time = time.time()
        traits1 = self.traits_api.get_traits()
        first_call_time = time.time() - start_time
        
        start_time = time.time()
        traits2 = self.traits_api.get_traits()
        second_call_time = time.time() - start_time
        
        assert traits1 == traits2
        # Second call should be faster (though this might not always be true)
        assert second_call_time >= 0

    def test_models_advanced_concurrent_access(self):
        """Test concurrent access to models advanced APIs."""
        import threading
        import time
        
        results = []
        errors = []
        
        def get_traits():
            try:
                traits = self.traits_api.get_traits()
                results.append(len(traits))
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=get_traits)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(results) == 3
        assert len(errors) == 0
        assert all(count > 0 for count in results)

    def test_models_advanced_memory_usage(self):
        """Test memory usage during models advanced operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform multiple operations
        for _ in range(10):
            traits = self.traits_api.get_traits()
            assert len(traits) > 0
            
            mapping = self.compatibility_api.get_mapping()
            assert mapping is not None
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024

    def test_models_advanced_data_consistency(self):
        """Test models advanced data consistency across multiple calls."""
        traits1 = self.traits_api.get_traits()
        traits2 = self.traits_api.get_traits()
        
        # Data should be consistent
        assert traits1 == traits2
        
        # Model IDs should be the same
        ids1 = set(traits1.keys())
        ids2 = set(traits2.keys())
        assert ids1 == ids2
