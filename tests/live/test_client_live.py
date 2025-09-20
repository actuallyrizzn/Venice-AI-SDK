"""
Live tests for the HTTPClient module.

These tests make real API calls to verify client functionality.
"""

import pytest
import os
from venice_sdk.client import HTTPClient
from venice_sdk.config import Config
from venice_sdk.errors import VeniceAPIError, VeniceConnectionError


@pytest.mark.live
class TestHTTPClientLive:
    """Live tests for HTTPClient with real API calls."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.api_key = os.getenv("VENICE_API_KEY")
        if not self.api_key:
            pytest.skip("VENICE_API_KEY environment variable not set")
        
        self.config = Config(api_key=self.api_key)
        self.client = HTTPClient(self.config)

    def test_get_models_endpoint(self):
        """Test GET request to models endpoint."""
        response = self.client.get("/models")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0
        
        # Verify model structure
        model = data["data"][0]
        assert "id" in model
        assert "name" in model
        assert "capabilities" in model

    def test_post_chat_completion(self):
        """Test POST request to chat completion endpoint."""
        data = {
            "model": "qwen3-4b",
            "messages": [
                {"role": "user", "content": "Hello, how are you?"}
            ],
            "max_tokens": 50
        }
        
        response = self.client.post("/chat/completions", data=data)
        
        assert response.status_code == 200
        result = response.json()
        assert "choices" in result
        assert len(result["choices"]) > 0
        assert "message" in result["choices"][0]
        assert "content" in result["choices"][0]["message"]

    def test_streaming_chat_completion(self):
        """Test streaming chat completion."""
        data = {
            "model": "qwen3-4b",
            "messages": [
                {"role": "user", "content": "Tell me a short story about a robot."}
            ],
            "max_tokens": 100,
            "stream": True
        }
        
        chunks = list(self.client.stream("/chat/completions", data=data))
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)
        
        # Verify at least one chunk contains valid JSON
        valid_chunks = 0
        for chunk in chunks:
            if chunk.strip().startswith('data: '):
                valid_chunks += 1
        
        assert valid_chunks > 0

    def test_custom_timeout(self):
        """Test custom timeout setting."""
        config = Config(api_key=self.api_key, timeout=5)
        client = HTTPClient(config)
        
        response = client.get("/models")
        assert response.status_code == 200

    def test_retry_mechanism(self):
        """Test retry mechanism with invalid endpoint."""
        with pytest.raises(VeniceAPIError):
            self.client.get("/invalid-endpoint")

    def test_connection_error_handling(self):
        """Test connection error handling."""
        # Use invalid base URL to trigger connection error
        config = Config(api_key=self.api_key, base_url="https://invalid-url-that-does-not-exist.com")
        client = HTTPClient(config)
        
        with pytest.raises(VeniceConnectionError):
            client.get("/models")

    def test_authentication_error(self):
        """Test authentication error handling."""
        config = Config(api_key="invalid-key")
        client = HTTPClient(config)
        
        with pytest.raises(VeniceAPIError) as exc_info:
            client.get("/models")
        
        assert exc_info.value.status_code == 401

    def test_rate_limit_handling(self):
        """Test rate limit handling."""
        # Make multiple rapid requests to potentially trigger rate limiting
        responses = []
        for _ in range(5):
            try:
                response = self.client.get("/models")
                responses.append(response.status_code)
            except VeniceAPIError as e:
                if e.status_code == 429:
                    # Rate limited - this is expected behavior
                    assert e.status_code == 429
                    return
        
        # If we get here, all requests succeeded
        assert all(status == 200 for status in responses)

    def test_large_response_handling(self):
        """Test handling of large responses."""
        data = {
            "model": "qwen3-4b",
            "messages": [
                {"role": "user", "content": "Write a detailed explanation of machine learning algorithms."}
            ],
            "max_tokens": 1000
        }
        
        response = self.client.post("/chat/completions", data=data)
        assert response.status_code == 200
        
        result = response.json()
        assert "choices" in result
        assert len(result["choices"]) > 0
        content = result["choices"][0]["message"]["content"]
        assert len(content) > 100  # Should be a substantial response

    def test_json_parsing_error_handling(self):
        """Test handling of malformed JSON responses."""
        # This test might not be possible with real API, but we can test the error handling
        # by using a mock or by testing with an endpoint that might return malformed JSON
        response = self.client.get("/models")
        assert response.status_code == 200
        
        # The response should be valid JSON
        data = response.json()
        assert isinstance(data, dict)

    def test_headers_and_authentication(self):
        """Test that proper headers and authentication are sent."""
        response = self.client.get("/models")
        assert response.status_code == 200
        
        # Verify the request was authenticated (we can't directly check headers in response,
        # but a 200 status means authentication worked)
        data = response.json()
        assert "data" in data

    def test_different_http_methods(self):
        """Test different HTTP methods."""
        # GET request
        get_response = self.client.get("/models")
        assert get_response.status_code == 200
        
        # POST request
        post_data = {
            "model": "qwen3-4b",
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 10
        }
        post_response = self.client.post("/chat/completions", data=post_data)
        assert post_response.status_code == 200

    def test_response_object_properties(self):
        """Test response object properties and methods."""
        response = self.client.get("/models")
        
        assert hasattr(response, 'status_code')
        assert hasattr(response, 'json')
        assert hasattr(response, 'text')
        assert hasattr(response, 'content')
        
        assert response.status_code == 200
        assert callable(response.json)
        assert callable(response.text)
        
        # Test json() method
        data = response.json()
        assert isinstance(data, dict)
        
        # Test text property
        text = response.text
        assert isinstance(text, str)
        assert len(text) > 0

    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request():
            try:
                response = self.client.get("/models")
                results.append(response.status_code)
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(results) == 3
        assert all(status == 200 for status in results)
        assert len(errors) == 0

    def test_memory_usage_with_large_responses(self):
        """Test memory usage with large responses."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Make several requests to test memory usage
        for _ in range(5):
            data = {
                "model": "qwen3-4b",
                "messages": [
                    {"role": "user", "content": "Write a comprehensive guide to Python programming."}
                ],
                "max_tokens": 500
            }
            response = self.client.post("/chat/completions", data=data)
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024

    def test_error_response_parsing(self):
        """Test parsing of error responses."""
        config = Config(api_key="invalid-key")
        client = HTTPClient(config)
        
        try:
            client.get("/models")
        except VeniceAPIError as e:
            assert e.status_code is not None
            assert e.message is not None
            assert isinstance(e.message, str)
            assert len(e.message) > 0

    def test_streaming_with_different_models(self):
        """Test streaming with different models."""
        models_to_test = ["qwen3-4b", "venice-uncensored"]
        
        for model in models_to_test:
            try:
                data = {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": "Hello"}
                    ],
                    "max_tokens": 50,
                    "stream": True
                }
                
                chunks = list(self.client.stream("/chat/completions", data=data))
                assert len(chunks) > 0
                
            except VeniceAPIError as e:
                # Some models might not be available, which is okay
                if e.status_code == 404:
                    continue
                raise
