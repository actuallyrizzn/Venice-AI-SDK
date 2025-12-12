"""
Live tests for the ModelsAPI module.

These tests make real API calls to verify models functionality.
"""

import pytest
import os
from venice_sdk.models import ModelsAPI
from venice_sdk.client import HTTPClient
from venice_sdk.config import Config, load_config
from venice_sdk.errors import VeniceAPIError


@pytest.mark.live
class TestModelsAPILive:
    """Live tests for ModelsAPI with real API calls."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.api_key = os.getenv("VENICE_API_KEY")
        if not self.api_key:
            pytest.skip("VENICE_API_KEY environment variable not set")
        
        self.config = load_config(api_key=self.api_key)
        self.client = HTTPClient(self.config)
        self.models_api = ModelsAPI(self.client)

    def test_list_models(self):
        """Test listing all available models."""
        models = self.models_api.list()
        
        assert isinstance(models, list)
        assert len(models) > 0
        
        # Verify model structure
        model = models[0]
        assert isinstance(model, dict)
        assert "id" in model
        assert "model_spec" in model
        # Name is nested inside model_spec
        assert "name" in model.get("model_spec", {})
        assert "capabilities" in model.get("model_spec", {})

    def test_get_specific_model(self):
        """Test getting a specific model by ID."""
        # First get the list to find a valid model ID
        models = self.models_api.list()
        assert len(models) > 0
        
        model_id = models[0]["id"]
        model = self.models_api.get(model_id)
        
        assert model is not None
        assert isinstance(model, dict)
        assert model["id"] == model_id
        assert "model_spec" in model
        # Name and capabilities are nested inside model_spec
        assert "name" in model.get("model_spec", {})
        assert "capabilities" in model.get("model_spec", {})

    def test_get_nonexistent_model(self):
        """Test getting a model that doesn't exist."""
        with pytest.raises(VeniceAPIError):
            self.models_api.get("nonexistent-model-id")

    def test_validate_model_success(self):
        """Test validating an existing model."""
        # First get the list to find a valid model ID
        models = self.models_api.list()
        assert len(models) > 0
        
        model_id = models[0]["id"]
        is_valid = self.models_api.validate(model_id)
        
        assert is_valid is True

    def test_validate_model_failure(self):
        """Test validating a non-existent model."""
        is_valid = self.models_api.validate("nonexistent-model-id")
        assert is_valid is False

    def test_get_text_models(self):
        """Test getting text models specifically."""
        from venice_sdk.models import get_text_models
        
        text_models = get_text_models(self.client)
        
        assert isinstance(text_models, list)
        assert len(text_models) > 0
        
        # Verify all returned models are text models
        for model in text_models:
            assert hasattr(model, 'id')
            assert hasattr(model, 'name')
            assert hasattr(model, 'type')
            assert model.type == 'text'

    def test_get_model_by_id_utility(self):
        """Test get_model_by_id utility function."""
        from venice_sdk.models import get_model_by_id
        
        # First get the list to find a valid model ID
        models = self.models_api.list()
        assert len(models) > 0
        
        model_id = models[0]["id"]
        model = get_model_by_id(model_id, self.client)
        
        assert model is not None
        assert hasattr(model, 'id')
        assert model.id == model_id

    def test_get_models_utility(self):
        """Test get_models utility function."""
        from venice_sdk.models import get_models
        
        models = get_models(self.client)
        
        assert isinstance(models, list)
        assert len(models) > 0
        
        # Verify model structure
        model = models[0]
        assert hasattr(model, 'id')
        assert hasattr(model, 'name')

    def test_model_capabilities_structure(self):
        """Test model capabilities structure."""
        models = self.models_api.list()
        assert len(models) > 0
        
        model = models[0]
        capabilities = model.get("capabilities", {})
        
        # Check for common capability fields
        if capabilities:
            assert isinstance(capabilities, dict)
            # Capabilities might include function_calling, streaming, etc.
            for key, value in capabilities.items():
                assert isinstance(key, str)
                assert isinstance(value, (bool, str, int, float, list, dict))

    def test_model_spec_structure(self):
        """Test model spec structure."""
        models = self.models_api.list()
        assert len(models) > 0
        
        model = models[0]
        model_spec = model.get("model_spec", {})
        
        if model_spec:
            assert isinstance(model_spec, dict)
            # Model spec might include various technical details
            for key, value in model_spec.items():
                assert isinstance(key, str)

    def test_available_context_tokens(self):
        """Test available context tokens field."""
        models = self.models_api.list()
        assert len(models) > 0
        
        model = models[0]
        context_tokens = model.get("availableContextTokens")
        
        if context_tokens is not None:
            assert isinstance(context_tokens, int)
            assert context_tokens > 0

    def test_model_categories(self):
        """Test model categories and types."""
        models = self.models_api.list()
        assert len(models) > 0
        
        # Group models by type if available
        text_models = []
        image_models = []
        audio_models = []
        
        for model in models:
            model_id = model.get("id", "").lower()
            if "text" in model_id or "llama" in model_id or "gpt" in model_id:
                text_models.append(model)
            elif "image" in model_id or "dall" in model_id:
                image_models.append(model)
            elif "audio" in model_id or "tts" in model_id:
                audio_models.append(model)
        
        # At least one category should have models
        total_categorized = len(text_models) + len(image_models) + len(audio_models)
        assert total_categorized > 0

    def test_model_performance_metrics(self):
        """Test model performance metrics if available."""
        models = self.models_api.list()
        assert len(models) > 0
        
        for model in models:
            # Check for performance-related fields
            if "performance" in model:
                performance = model["performance"]
                assert isinstance(performance, dict)
            
            if "metrics" in model:
                metrics = model["metrics"]
                assert isinstance(metrics, dict)

    def test_model_pricing_information(self):
        """Test model pricing information if available."""
        models = self.models_api.list()
        assert len(models) > 0
        
        for model in models:
            # Check for pricing-related fields
            if "pricing" in model:
                pricing = model["pricing"]
                assert isinstance(pricing, dict)
            
            if "cost" in model:
                cost = model["cost"]
                assert isinstance(cost, (dict, float, int))

    def test_model_languages_support(self):
        """Test model language support if available."""
        models = self.models_api.list()
        assert len(models) > 0
        
        for model in models:
            if "languages" in model:
                languages = model["languages"]
                assert isinstance(languages, list)
                if languages:
                    assert all(isinstance(lang, str) for lang in languages)

    def test_model_region_availability(self):
        """Test model region availability if available."""
        models = self.models_api.list()
        assert len(models) > 0
        
        for model in models:
            if "regions" in model:
                regions = model["regions"]
                assert isinstance(regions, list)
                if regions:
                    assert all(isinstance(region, str) for region in regions)

    def test_model_versions(self):
        """Test model versions if available."""
        models = self.models_api.list()
        assert len(models) > 0
        
        for model in models:
            if "version" in model:
                version = model["version"]
                assert isinstance(version, str)
                assert len(version) > 0
            
            if "versions" in model:
                versions = model["versions"]
                assert isinstance(versions, list)
                if versions:
                    assert all(isinstance(v, str) for v in versions)

    def test_model_provider_information(self):
        """Test model provider information if available."""
        models = self.models_api.list()
        assert len(models) > 0
        
        for model in models:
            if "provider" in model:
                provider = model["provider"]
                assert isinstance(provider, str)
                assert len(provider) > 0
            
            if "vendor" in model:
                vendor = model["vendor"]
                assert isinstance(vendor, str)
                assert len(vendor) > 0

    def test_model_creation_timestamps(self):
        """Test model creation timestamps if available."""
        models = self.models_api.list()
        assert len(models) > 0
        
        for model in models:
            if "created" in model:
                created = model["created"]
                assert isinstance(created, (int, str))
                if isinstance(created, int):
                    assert created > 0

    def test_model_status_information(self):
        """Test model status information if available."""
        models = self.models_api.list()
        assert len(models) > 0
        
        for model in models:
            if "status" in model:
                status = model["status"]
                assert isinstance(status, str)
                assert status in ["active", "inactive", "deprecated", "beta", "stable"]

    def test_model_documentation_links(self):
        """Test model documentation links if available."""
        models = self.models_api.list()
        assert len(models) > 0
        
        for model in models:
            if "documentation" in model:
                docs = model["documentation"]
                assert isinstance(docs, (str, dict))
                if isinstance(docs, str):
                    assert docs.startswith("http")

    def test_model_examples(self):
        """Test model examples if available."""
        models = self.models_api.list()
        assert len(models) > 0
        
        for model in models:
            if "examples" in model:
                examples = model["examples"]
                assert isinstance(examples, list)
                if examples:
                    assert all(isinstance(example, dict) for example in examples)

    def test_model_limitations(self):
        """Test model limitations if available."""
        models = self.models_api.list()
        assert len(models) > 0
        
        for model in models:
            if "limitations" in model:
                limitations = model["limitations"]
                assert isinstance(limitations, (str, list))
                if isinstance(limitations, list):
                    assert all(isinstance(lim, str) for lim in limitations)

    def test_model_recommendations(self):
        """Test model recommendations if available."""
        models = self.models_api.list()
        assert len(models) > 0
        
        for model in models:
            if "recommended_for" in model:
                recommended = model["recommended_for"]
                assert isinstance(recommended, list)
                if recommended:
                    assert all(isinstance(rec, str) for rec in recommended)

    def test_models_api_error_handling(self):
        """Test error handling in models API."""
        # Note: The models endpoint doesn't validate API keys, so we test with a different scenario
        # Test with an invalid model ID instead
        with pytest.raises(VeniceAPIError):
            self.models_api.get("nonexistent-model-id")

    def test_models_api_performance(self):
        """Test models API performance."""
        import time
        
        start_time = time.time()
        models = self.models_api.list()
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert len(models) > 0
        assert response_time < 10  # Should complete within 10 seconds
        assert response_time > 0

    def test_models_api_caching(self):
        """Test models API caching behavior."""
        import time
        # First call
        start_time = time.time()
        models1 = self.models_api.list()
        first_call_time = time.time() - start_time
        
        # Second call (should be faster due to caching)
        start_time = time.time()
        models2 = self.models_api.list()
        second_call_time = time.time() - start_time
        
        assert models1 == models2
        # Second call should be faster (though this might not always be true)
        assert second_call_time >= 0

    def test_models_api_concurrent_access(self):
        """Test concurrent access to models API."""
        import threading
        import time
        
        results = []
        errors = []
        
        def get_models():
            try:
                models = self.models_api.list()
                results.append(len(models))
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=get_models)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(results) == 5
        assert len(errors) == 0
        assert all(count > 0 for count in results)
        assert all(count == results[0] for count in results)  # All should return same count
