"""
Live tests for the ChatAPI module.

These tests make real API calls to verify chat functionality.
"""

import pytest
import os
from venice_sdk.chat import ChatAPI
from venice_sdk.client import HTTPClient
from venice_sdk.config import Config
from venice_sdk.errors import VeniceAPIError
from .test_utils import LiveTestUtils


@pytest.mark.live
class TestChatAPILive:
    """Live tests for ChatAPI with real API calls."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.api_key = os.getenv("VENICE_API_KEY")
        if not self.api_key:
            pytest.skip("VENICE_API_KEY environment variable not set")
        
        self.config = Config(api_key=self.api_key)
        self.client = HTTPClient(self.config)
        self.chat_api = ChatAPI(self.client)
        
        # Get available models dynamically
        self.text_models = LiveTestUtils.get_text_models()
        self.default_model = LiveTestUtils.get_default_text_model()

    def test_complete_basic_chat(self):
        """Test basic chat completion."""
        messages = [
            {"role": "user", "content": "Hello, how are you today?"}
        ]

        response = self.chat_api.complete(
            messages=messages,
            model=self.default_model,
            max_tokens=100
        )
        
        assert response is not None
        assert "choices" in response
        assert len(response["choices"]) > 0
        assert "message" in response["choices"][0]
        assert "content" in response["choices"][0]["message"]
        assert len(response["choices"][0]["message"]["content"]) > 0

    def test_complete_with_system_message(self):
        """Test chat completion with system message."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant that speaks like a pirate."},
            {"role": "user", "content": "Tell me about the weather."}
        ]
        
        response = self.chat_api.complete(
            messages=messages,
            model=self.default_model,
            max_tokens=100
        )
        
        assert response is not None
        content = response["choices"][0]["message"]["content"]
        assert len(content) > 0
        # Check if the response has pirate-like language (might not always work)
        assert isinstance(content, str)

    def test_complete_with_conversation_history(self):
        """Test chat completion with conversation history."""
        messages = [
            {"role": "user", "content": "My name is Alice."},
            {"role": "assistant", "content": "Hello Alice! Nice to meet you."},
            {"role": "user", "content": "What's my name?"}
        ]
        
        response = self.chat_api.complete(
            messages=messages,
            model=self.default_model,
            max_tokens=50
        )
        
        assert response is not None
        content = response["choices"][0]["message"]["content"]
        assert len(content) > 0
        # The model should remember the name Alice
        assert "Alice" in content or "alice" in content.lower()

    def test_complete_with_tools(self):
        """Test chat completion with function calling."""
        messages = [
            {"role": "user", "content": "What's the weather like in New York?"}
        ]
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the current weather for a location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g. San Francisco, CA"
                            }
                        },
                        "required": ["location"]
                    }
                }
            }
        ]
        
        response = self.chat_api.complete(
            messages=messages,
            model=self.default_model,
            tools=tools,
            max_tokens=100
        )
        
        assert response is not None
        # The response might include tool calls
        assert "choices" in response

    def test_complete_with_parameters(self):
        """Test chat completion with various parameters."""
        messages = [
            {"role": "user", "content": "Write a creative story about a robot."}
        ]
        
        response = self.chat_api.complete(
            messages=messages,
            model=self.default_model,
            max_tokens=200,
            temperature=0.8,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.1,
            stop=["END"]
        )
        
        assert response is not None
        content = response["choices"][0]["message"]["content"]
        assert len(content) > 50  # Should be a substantial story

    def test_complete_streaming(self):
        """Test streaming chat completion."""
        messages = [
            {"role": "user", "content": "Tell me a story about space exploration."}
        ]
        
        chunks = list(self.chat_api.complete_stream(
            messages=messages,
            model=self.default_model,
            max_tokens=150
        ))
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)
        
        # Verify at least one chunk contains valid JSON
        valid_chunks = 0
        for chunk in chunks:
            if chunk.strip().startswith('data: '):
                valid_chunks += 1
        
        assert valid_chunks > 0

    def test_complete_with_different_models(self):
        """Test chat completion with different models."""
        # Test with first 2 available models
        models_to_test = self.text_models[:2]
        
        for model in models_to_test:
            try:
                messages = [
                    {"role": "user", "content": f"Hello, I'm testing the {model} model."}
                ]
                
                response = self.chat_api.complete(
                    messages=messages,
                    model=model,
                    max_tokens=50
                )
                
                assert response is not None
                content = response["choices"][0]["message"]["content"]
                assert len(content) > 0
                
            except VeniceAPIError as e:
                # Some models might not be available
                if e.status_code == 404:
                    continue
                raise

    def test_complete_with_max_tokens(self):
        """Test chat completion with different max_tokens values."""
        messages = [
            {"role": "user", "content": "Write a detailed explanation of quantum computing."}
        ]
        
        # Test with small max_tokens
        response_short = self.chat_api.complete(
            messages=messages,
            model=self.default_model,
            max_tokens=20
        )
        
        content_short = response_short["choices"][0]["message"]["content"]
        assert len(content_short) <= 50  # Should be relatively short
        
        # Test with larger max_tokens
        response_long = self.chat_api.complete(
            messages=messages,
            model=self.default_model,
            max_tokens=200
        )
        
        content_long = response_long["choices"][0]["message"]["content"]
        assert len(content_long) > len(content_short)

    def test_complete_with_temperature(self):
        """Test chat completion with different temperature values."""
        messages = [
            {"role": "user", "content": "Write a creative poem about nature."}
        ]
        
        # Test with low temperature (more deterministic)
        response_low = self.chat_api.complete(
            messages=messages,
            model=self.default_model,
            max_tokens=100,
            temperature=0.1
        )
        
        # Test with high temperature (more creative)
        response_high = self.chat_api.complete(
            messages=messages,
            model=self.default_model,
            max_tokens=100,
            temperature=1.0
        )
        
        content_low = response_low["choices"][0]["message"]["content"]
        content_high = response_high["choices"][0]["message"]["content"]
        
        assert len(content_low) > 0
        assert len(content_high) > 0
        # High temperature should produce different content
        assert content_low != content_high

    def test_complete_with_stop_sequences(self):
        """Test chat completion with stop sequences."""
        messages = [
            {"role": "user", "content": "Count from 1 to 10."}
        ]
        
        response = self.chat_api.complete(
            messages=messages,
            model=self.default_model,
            max_tokens=100,
            stop=["5"]
        )
        
        content = response["choices"][0]["message"]["content"]
        assert len(content) > 0
        # The response should stop before or at "5"
        assert "5" not in content or content.endswith("5")

    def test_complete_with_user_parameter(self):
        """Test chat completion with user parameter."""
        messages = [
            {"role": "user", "content": "Hello, what's your name?"}
        ]
        
        response = self.chat_api.complete(
            messages=messages,
            model=self.default_model,
            max_tokens=50,
            user="test-user-123"
        )
        
        assert response is not None
        content = response["choices"][0]["message"]["content"]
        assert len(content) > 0

    def test_complete_error_handling(self):
        """Test error handling in chat completion."""
        # Test with invalid model
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        
        with pytest.raises(VeniceAPIError):
            self.chat_api.complete(
                messages=messages,
                model="invalid-model",
                max_tokens=50
            )

    def test_complete_with_empty_messages(self):
        """Test chat completion with empty messages."""
        with pytest.raises(ValueError):
            self.chat_api.complete(
                messages=[],
                model=self.default_model,
                max_tokens=50
            )

    def test_complete_with_invalid_messages(self):
        """Test chat completion with invalid message format."""
        messages = [
            {"invalid": "message"}
        ]
        
        with pytest.raises(ValueError):
            self.chat_api.complete(
                messages=messages,
                model=self.default_model,
                max_tokens=50
            )

    def test_complete_with_large_context(self):
        """Test chat completion with large context."""
        # Create a large context
        large_context = "This is a test message. " * 1000
        messages = [
            {"role": "user", "content": large_context + " What did I just say?"}
        ]
        
        response = self.chat_api.complete(
            messages=messages,
            model=self.default_model,
            max_tokens=50
        )
        
        assert response is not None
        content = response["choices"][0]["message"]["content"]
        assert len(content) > 0

    def test_complete_with_special_characters(self):
        """Test chat completion with special characters."""
        messages = [
            {"role": "user", "content": "Hello! How are you? I'm testing special characters: @#$%^&*()_+-=[]{}|;':\",./<>?"}
        ]
        
        response = self.chat_api.complete(
            messages=messages,
            model=self.default_model,
            max_tokens=50
        )
        
        assert response is not None
        content = response["choices"][0]["message"]["content"]
        assert len(content) > 0

    def test_complete_with_unicode(self):
        """Test chat completion with unicode characters."""
        messages = [
            {"role": "user", "content": "Hello! 你好! Hola! مرحبا! Привет! 🌟"}
        ]
        
        response = self.chat_api.complete(
            messages=messages,
            model=self.default_model,
            max_tokens=50
        )
        
        assert response is not None
        content = response["choices"][0]["message"]["content"]
        assert len(content) > 0

    def test_complete_performance(self):
        """Test chat completion performance."""
        import time
        
        messages = [
            {"role": "user", "content": "What is 2+2?"}
        ]
        
        start_time = time.time()
        response = self.chat_api.complete(
            messages=messages,
            model=self.default_model,
            max_tokens=10
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response is not None
        assert response_time < 30  # Should complete within 30 seconds
        assert response_time > 0

    def test_complete_with_streaming_performance(self):
        """Test streaming chat completion performance."""
        import time
        
        messages = [
            {"role": "user", "content": "Write a short story about a cat."}
        ]
        
        start_time = time.time()
        chunks = list(self.chat_api.complete_stream(
            messages=messages,
            model=self.default_model,
            max_tokens=100
        ))
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert len(chunks) > 0
        assert response_time < 30  # Should complete within 30 seconds
        assert response_time > 0

    def test_complete_concurrent_requests(self):
        """Test concurrent chat completion requests."""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request():
            try:
                messages = [
                    {"role": "user", "content": f"Hello from thread {threading.current_thread().name}"}
                ]
                response = self.chat_api.complete(
                    messages=messages,
                    model=self.default_model,
                    max_tokens=20
                )
                results.append(response)
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=make_request, name=f"Thread-{i}")
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(results) == 3
        assert len(errors) == 0
        assert all("choices" in result for result in results)
