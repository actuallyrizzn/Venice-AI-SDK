"""
Live test runner for the Venice AI SDK.

This module provides utilities for running live tests and managing test data.
"""

import pytest
import os
import time
import psutil
from pathlib import Path
from typing import Dict, List, Any
from venice_sdk.venice_client import VeniceClient
from venice_sdk.config import Config


class LiveTestRunner:
    """Live test runner for comprehensive testing."""
    
    def __init__(self, api_key: str = None):
        """Initialize the live test runner."""
        self.api_key = api_key or os.getenv("VENICE_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set in VENICE_API_KEY environment variable")
        
        self.config = Config(api_key=self.api_key)
        self.client = VeniceClient(self.config)
        self.test_results = {}
        self.performance_metrics = {}
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all live tests and return results."""
        print("🚀 Starting Venice AI SDK Live Tests...")
        print(f"📊 API Key: {self.api_key[:8]}...{self.api_key[-4:]}")
        print(f"🌐 Base URL: {self.config.base_url}")
        print(f"⏱️  Timeout: {self.config.timeout}s")
        print(f"🔄 Max Retries: {self.config.max_retries}")
        print(f"⏳ Retry Delay: {self.config.retry_delay}s")
        print("-" * 60)
        
        # Test categories
        test_categories = [
            "client",
            "chat", 
            "models",
            "audio",
            "embeddings",
            "characters",
            "account",
            "images",
            "models_advanced",
            "config",
            "cli",
            "venice_client"
        ]
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for category in test_categories:
            print(f"\n🧪 Testing {category.upper()} module...")
            
            try:
                category_results = self._run_category_tests(category)
                self.test_results[category] = category_results
                
                category_passed = category_results.get("passed", 0)
                category_failed = category_results.get("failed", 0)
                category_total = category_passed + category_failed
                
                total_tests += category_total
                passed_tests += category_passed
                failed_tests += category_failed
                
                status = "✅ PASSED" if category_failed == 0 else "❌ FAILED"
                print(f"   {status} - {category_passed}/{category_total} tests passed")
                
            except Exception as e:
                print(f"   ❌ ERROR - {str(e)}")
                self.test_results[category] = {"error": str(e)}
                failed_tests += 1
                total_tests += 1
        
        # Performance summary
        self._generate_performance_summary()
        
        # Final results
        print("\n" + "=" * 60)
        print("📈 LIVE TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        
        if self.performance_metrics:
            print(f"\n⚡ Performance Metrics:")
            for metric, value in self.performance_metrics.items():
                print(f"   {metric}: {value}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests/total_tests*100) if total_tests > 0 else 0,
            "test_results": self.test_results,
            "performance_metrics": self.performance_metrics
        }
    
    def _run_category_tests(self, category: str) -> Dict[str, Any]:
        """Run tests for a specific category."""
        start_time = time.time()
        
        try:
            if category == "client":
                return self._test_client_module()
            elif category == "chat":
                return self._test_chat_module()
            elif category == "models":
                return self._test_models_module()
            elif category == "audio":
                return self._test_audio_module()
            elif category == "embeddings":
                return self._test_embeddings_module()
            elif category == "characters":
                return self._test_characters_module()
            elif category == "account":
                return self._test_account_module()
            elif category == "images":
                return self._test_images_module()
            elif category == "models_advanced":
                return self._test_models_advanced_module()
            elif category == "config":
                return self._test_config_module()
            elif category == "cli":
                return self._test_cli_module()
            elif category == "venice_client":
                return self._test_venice_client_module()
            else:
                raise ValueError(f"Unknown test category: {category}")
                
        except Exception as e:
            return {"error": str(e), "passed": 0, "failed": 1}
        finally:
            end_time = time.time()
            self.performance_metrics[f"{category}_duration"] = f"{end_time - start_time:.2f}s"
    
    def _test_client_module(self) -> Dict[str, Any]:
        """Test HTTPClient module."""
        passed = 0
        failed = 0
        
        try:
            # Test basic GET request
            response = self.client.http_client.get("/models")
            assert response.status_code == 200
            passed += 1
        except Exception as e:
            print(f"   ❌ GET request failed: {e}")
            failed += 1
        
        try:
            # Test POST request
            data = {
                "model": "llama-3.3-8b",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            response = self.client.http_client.post("/chat/completions", data=data)
            assert response.status_code == 200
            passed += 1
        except Exception as e:
            print(f"   ❌ POST request failed: {e}")
            failed += 1
        
        return {"passed": passed, "failed": failed}
    
    def _test_chat_module(self) -> Dict[str, Any]:
        """Test ChatAPI module."""
        passed = 0
        failed = 0
        
        try:
            # Test basic chat completion
            messages = [{"role": "user", "content": "Hello, how are you?"}]
            response = self.client.chat.complete(messages=messages, model="llama-3.3-8b", max_tokens=50)
            assert response is not None
            assert "choices" in response
            passed += 1
        except Exception as e:
            print(f"   ❌ Chat completion failed: {e}")
            failed += 1
        
        try:
            # Test streaming
            messages = [{"role": "user", "content": "Tell me a short story."}]
            chunks = list(self.client.chat.complete_stream(messages=messages, model="llama-3.3-8b", max_tokens=50))
            assert len(chunks) > 0
            passed += 1
        except Exception as e:
            print(f"   ❌ Chat streaming failed: {e}")
            failed += 1
        
        return {"passed": passed, "failed": failed}
    
    def _test_models_module(self) -> Dict[str, Any]:
        """Test ModelsAPI module."""
        passed = 0
        failed = 0
        
        try:
            # Test listing models
            models = self.client.models.list()
            assert isinstance(models, list)
            assert len(models) > 0
            passed += 1
        except Exception as e:
            print(f"   ❌ Models listing failed: {e}")
            failed += 1
        
        try:
            # Test getting specific model
            if models:
                model = self.client.models.get(models[0]["id"])
                assert model is not None
                passed += 1
        except Exception as e:
            print(f"   ❌ Model retrieval failed: {e}")
            failed += 1
        
        return {"passed": passed, "failed": failed}
    
    def _test_audio_module(self) -> Dict[str, Any]:
        """Test AudioAPI module."""
        passed = 0
        failed = 0
        
        try:
            # Test getting voices
            voices = self.client.audio.get_voices()
            assert isinstance(voices, list)
            assert len(voices) > 0
            passed += 1
        except Exception as e:
            print(f"   ❌ Voices listing failed: {e}")
            failed += 1
        
        try:
            # Test speech generation
            result = self.client.audio.speech(
                text="Hello, this is a test.",
                voice="alloy",
                model="tts-1"
            )
            assert result is not None
            passed += 1
        except Exception as e:
            print(f"   ❌ Speech generation failed: {e}")
            failed += 1
        
        return {"passed": passed, "failed": failed}
    
    def _test_embeddings_module(self) -> Dict[str, Any]:
        """Test EmbeddingsAPI module."""
        passed = 0
        failed = 0
        
        try:
            # Test generating embedding
            result = self.client.embeddings.generate_single(
                text="This is a test of the embeddings system.",
                model="text-embedding-3-small"
            )
            assert result is not None
            assert hasattr(result, 'embedding')
            passed += 1
        except Exception as e:
            print(f"   ❌ Embedding generation failed: {e}")
            failed += 1
        
        try:
            # Test batch embedding
            texts = ["Text 1", "Text 2", "Text 3"]
            result = self.client.embeddings.generate(texts=texts, model="text-embedding-3-small")
            assert result is not None
            assert hasattr(result, 'embeddings')
            passed += 1
        except Exception as e:
            print(f"   ❌ Batch embedding failed: {e}")
            failed += 1
        
        return {"passed": passed, "failed": failed}
    
    def _test_characters_module(self) -> Dict[str, Any]:
        """Test CharactersAPI module."""
        passed = 0
        failed = 0
        
        try:
            # Test listing characters
            characters = self.client.characters.list()
            assert isinstance(characters, list)
            assert len(characters) > 0
            passed += 1
        except Exception as e:
            print(f"   ❌ Characters listing failed: {e}")
            failed += 1
        
        try:
            # Test searching characters
            search_results = self.client.characters.search("assistant")
            assert isinstance(search_results, list)
            passed += 1
        except Exception as e:
            print(f"   ❌ Character search failed: {e}")
            failed += 1
        
        return {"passed": passed, "failed": failed}
    
    def _test_account_module(self) -> Dict[str, Any]:
        """Test Account APIs."""
        passed = 0
        failed = 0
        
        try:
            # Test listing API keys
            api_keys = self.client.api_keys.list()
            assert isinstance(api_keys, list)
            passed += 1
        except Exception as e:
            print(f"   ❌ API keys listing failed: {e}")
            failed += 1
        
        try:
            # Test getting usage info
            usage_info = self.client.billing.get_usage_info()
            assert usage_info is not None
            passed += 1
        except Exception as e:
            print(f"   ❌ Usage info failed: {e}")
            failed += 1
        
        return {"passed": passed, "failed": failed}
    
    def _test_images_module(self) -> Dict[str, Any]:
        """Test Images APIs."""
        passed = 0
        failed = 0
        
        try:
            # Test image generation
            result = self.client.images.generate(
                prompt="A beautiful sunset over mountains",
                model="dall-e-3"
            )
            assert result is not None
            passed += 1
        except Exception as e:
            print(f"   ❌ Image generation failed: {e}")
            failed += 1
        
        try:
            # Test listing styles
            styles = self.client.image_styles.list_styles()
            assert isinstance(styles, list)
            passed += 1
        except Exception as e:
            print(f"   ❌ Styles listing failed: {e}")
            failed += 1
        
        return {"passed": passed, "failed": failed}
    
    def _test_models_advanced_module(self) -> Dict[str, Any]:
        """Test ModelsAdvanced APIs."""
        passed = 0
        failed = 0
        
        try:
            # Test getting traits
            traits = self.client.models_traits.get_traits()
            assert isinstance(traits, dict)
            passed += 1
        except Exception as e:
            print(f"   ❌ Traits retrieval failed: {e}")
            failed += 1
        
        try:
            # Test getting compatibility mapping
            mapping = self.client.models_compatibility.get_mapping()
            assert mapping is not None
            passed += 1
        except Exception as e:
            print(f"   ❌ Compatibility mapping failed: {e}")
            failed += 1
        
        return {"passed": passed, "failed": failed}
    
    def _test_config_module(self) -> Dict[str, Any]:
        """Test Config module."""
        passed = 0
        failed = 0
        
        try:
            # Test config initialization
            config = Config(api_key="test-key")
            assert config.api_key == "test-key"
            passed += 1
        except Exception as e:
            print(f"   ❌ Config initialization failed: {e}")
            failed += 1
        
        try:
            # Test headers property
            headers = config.headers
            assert "Authorization" in headers
            passed += 1
        except Exception as e:
            print(f"   ❌ Headers property failed: {e}")
            failed += 1
        
        return {"passed": passed, "failed": failed}
    
    def _test_cli_module(self) -> Dict[str, Any]:
        """Test CLI module."""
        passed = 0
        failed = 0
        
        try:
            # Test get_api_key function
            from venice_sdk.cli import get_api_key
            api_key = get_api_key()
            assert api_key is not None
            passed += 1
        except Exception as e:
            print(f"   ❌ get_api_key failed: {e}")
            failed += 1
        
        try:
            # Test CLI group initialization
            from venice_sdk.cli import cli
            assert hasattr(cli, 'commands')
            passed += 1
        except Exception as e:
            print(f"   ❌ CLI group failed: {e}")
            failed += 1
        
        return {"passed": passed, "failed": failed}
    
    def _test_venice_client_module(self) -> Dict[str, Any]:
        """Test VeniceClient module."""
        passed = 0
        failed = 0
        
        try:
            # Test client initialization
            client = VeniceClient()
            assert client is not None
            passed += 1
        except Exception as e:
            print(f"   ❌ Client initialization failed: {e}")
            failed += 1
        
        try:
            # Test account summary
            summary = client.get_account_summary()
            assert isinstance(summary, dict)
            passed += 1
        except Exception as e:
            print(f"   ❌ Account summary failed: {e}")
            failed += 1
        
        return {"passed": passed, "failed": failed}
    
    def _generate_performance_summary(self):
        """Generate performance summary."""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        self.performance_metrics.update({
            "memory_usage": f"{memory_info.rss / 1024 / 1024:.1f} MB",
            "cpu_percent": f"{process.cpu_percent():.1f}%",
            "total_duration": f"{sum(float(v.rstrip('s')) for v in self.performance_metrics.values() if v.endswith('s')):.2f}s"
        })


def run_live_tests(api_key: str = None) -> Dict[str, Any]:
    """Run all live tests and return results."""
    runner = LiveTestRunner(api_key)
    return runner.run_all_tests()


if __name__ == "__main__":
    # Run live tests if executed directly
    results = run_live_tests()
    print(f"\n🎉 Live tests completed with {results['success_rate']:.1f}% success rate!")
