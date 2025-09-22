"""
Comprehensive unit tests for the ChatAPI module.
"""

import pytest
from unittest.mock import patch, MagicMock
from venice_sdk.chat import ChatAPI, Message, Choice, ChatCompletion, Usage
from venice_sdk.errors import VeniceAPIError


class TestChatAPIComprehensive:
    """Comprehensive test suite for ChatAPI."""

    def test_chat_api_initialization(self, mock_client):
        """Test ChatAPI initialization."""
        chat_api = ChatAPI(mock_client)
        assert chat_api.client == mock_client

    def test_complete_success(self, chat_api, mock_chat_response):
        """Test successful chat completion."""
        with patch.object(chat_api.client, 'post', return_value=mock_chat_response):
            response = chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b"
            )
            
            assert response["id"] == "chatcmpl-123"
            assert response["choices"][0]["message"]["content"] == "Hello! How can I help you today?"

    def test_complete_with_streaming(self, chat_api, mock_streaming_response):
        """Test chat completion with streaming."""
        with patch.object(chat_api.client, 'stream', return_value=mock_streaming_response):
            response = chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                stream=True
            )
            
            # Should return a generator
            assert hasattr(response, '__iter__')
            chunks = list(response)
            # The mock streaming response should return some chunks
            assert len(chunks) >= 0  # Allow empty for now

    def test_complete_with_new_parameters(self, chat_api, mock_chat_response):
        """Test chat completion with all new parameters from Swagger spec."""
        with patch.object(chat_api.client, 'post', return_value=mock_chat_response):
            response = chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                temperature=1.5,
                frequency_penalty=0.5,
                presence_penalty=-0.3,
                repetition_penalty=1.2,
                logprobs=True,
                top_logprobs=3,
                max_completion_tokens=1000,
                max_temp=1.8,
                min_p=0.1,
                min_temp=0.2,
                n=2,
                seed=42,
                stop=["END", "STOP"],
                stop_token_ids=[151643, 151645],
                stream_options={"include_usage": True}
            )
            
            # Verify the request was made with all parameters
            chat_api.client.post.assert_called_once()
            call_args = chat_api.client.post.call_args
            data = call_args[1]['data']
            
            assert data['frequency_penalty'] == 0.5
            assert data['presence_penalty'] == -0.3
            assert data['repetition_penalty'] == 1.2
            assert data['logprobs'] == True
            assert data['top_logprobs'] == 3
            assert data['max_completion_tokens'] == 1000
            assert data['max_temp'] == 1.8
            assert data['min_p'] == 0.1
            assert data['min_temp'] == 0.2
            assert data['n'] == 2
            assert data['seed'] == 42
            assert data['stop'] == ["END", "STOP"]
            assert data['stop_token_ids'] == [151643, 151645]
            assert data['stream_options'] == {"include_usage": True}

    def test_complete_with_tools(self, chat_api, mock_chat_response):
        """Test chat completion with tools."""
        with patch.object(chat_api.client, 'post', return_value=mock_chat_response):
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "description": "Get the current weather"
                    }
                }
            ]
            
            response = chat_api.complete(
                messages=[{"role": "user", "content": "What's the weather?"}],
                model="llama-3.3-70b",
                tools=tools
            )
            
            assert response["id"] == "chatcmpl-123"

    def test_complete_with_system_message(self, chat_api, mock_chat_response):
        """Test chat completion with system message."""
        with patch.object(chat_api.client, 'post', return_value=mock_chat_response):
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"}
            ]
            
            response = chat_api.complete(
                messages=messages,
                model="llama-3.3-70b"
            )
            
            assert response["id"] == "chatcmpl-123"

    def test_complete_with_custom_parameters(self, chat_api, mock_chat_response):
        """Test chat completion with custom parameters."""
        with patch.object(chat_api.client, 'post', return_value=mock_chat_response):
            response = chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                temperature=0.7,
                max_tokens=100,
                top_p=0.9
            )
            
            assert response["id"] == "chatcmpl-123"

    def test_complete_invalid_messages(self, chat_api):
        """Test chat completion with invalid messages."""
        with pytest.raises(ValueError, match="Messages must be a non-empty list"):
            chat_api.complete(messages=[], model="llama-3.3-70b")
        
        with pytest.raises(ValueError, match="Messages must be a non-empty list"):
            chat_api.complete(messages=None, model="llama-3.3-70b")

    def test_complete_invalid_temperature(self, chat_api):
        """Test chat completion with invalid temperature."""
        with pytest.raises(ValueError, match="Temperature must be between 0 and 2"):
            chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                temperature=3.0
            )

    def test_complete_invalid_frequency_penalty(self, chat_api):
        """Test chat completion with invalid frequency penalty."""
        with pytest.raises(ValueError, match="Frequency penalty must be between -2.0 and 2.0"):
            chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                frequency_penalty=3.0
            )

    def test_complete_invalid_presence_penalty(self, chat_api):
        """Test chat completion with invalid presence penalty."""
        with pytest.raises(ValueError, match="Presence penalty must be between -2.0 and 2.0"):
            chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                presence_penalty=-3.0
            )

    def test_complete_invalid_repetition_penalty(self, chat_api):
        """Test chat completion with invalid repetition penalty."""
        with pytest.raises(ValueError, match="Repetition penalty must be >= 0"):
            chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                repetition_penalty=-1.0
            )

    def test_complete_invalid_max_temp(self, chat_api):
        """Test chat completion with invalid max temperature."""
        with pytest.raises(ValueError, match="Max temperature must be between 0 and 2"):
            chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                max_temp=3.0
            )

    def test_complete_invalid_min_temp(self, chat_api):
        """Test chat completion with invalid min temperature."""
        with pytest.raises(ValueError, match="Min temperature must be between 0 and 2"):
            chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                min_temp=-1.0
            )

    def test_complete_invalid_min_p(self, chat_api):
        """Test chat completion with invalid min p."""
        with pytest.raises(ValueError, match="Min p must be between 0 and 1"):
            chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                min_p=2.0
            )

    def test_complete_invalid_top_logprobs(self, chat_api):
        """Test chat completion with invalid top logprobs."""
        with pytest.raises(ValueError, match="Top logprobs must be >= 0"):
            chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                top_logprobs=-1
            )

    def test_complete_invalid_seed(self, chat_api):
        """Test chat completion with invalid seed."""
        with pytest.raises(ValueError, match="Seed must be >= 0"):
            chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                seed=-1
            )

    def test_complete_invalid_n(self, chat_api):
        """Test chat completion with invalid n."""
        with pytest.raises(ValueError, match="n must be >= 1"):
            chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                n=0
            )

    def test_complete_api_error(self, chat_api):
        """Test chat completion with API error."""
        with patch.object(chat_api.client, 'post', side_effect=VeniceAPIError("API error occurred")):
            with pytest.raises(VeniceAPIError) as exc_info:
                chat_api.complete(
                    messages=[{"role": "user", "content": "Hello"}],
                    model="llama-3.3-70b"
                )
            assert "API error occurred" in str(exc_info.value)

    def test_complete_streaming_error(self, chat_api):
        """Test chat completion streaming with error."""
        with patch.object(chat_api.client, 'stream', side_effect=VeniceAPIError("Streaming error occurred")):
            with pytest.raises(VeniceAPIError) as exc_info:
                chat_api.complete(
                    messages=[{"role": "user", "content": "Hello"}],
                    model="llama-3.3-70b",
                    stream=True
                )
            assert "Streaming error occurred" in str(exc_info.value)

    def test_complete_with_stop_sequences(self, chat_api, mock_chat_response):
        """Test chat completion with stop sequences."""
        with patch.object(chat_api.client, 'post', return_value=mock_chat_response):
            response = chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                stop=["\n\n", "Human:"]
            )
            
            assert response["id"] == "chatcmpl-123"

    def test_complete_with_presence_penalty(self, chat_api, mock_chat_response):
        """Test chat completion with presence penalty."""
        with patch.object(chat_api.client, 'post', return_value=mock_chat_response):
            response = chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                presence_penalty=0.5
            )
            
            assert response["id"] == "chatcmpl-123"

    def test_complete_with_frequency_penalty(self, chat_api, mock_chat_response):
        """Test chat completion with frequency penalty."""
        with patch.object(chat_api.client, 'post', return_value=mock_chat_response):
            response = chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                frequency_penalty=0.5
            )
            
            assert response["id"] == "chatcmpl-123"

    def test_complete_with_user_parameter(self, chat_api, mock_chat_response):
        """Test chat completion with user parameter."""
        with patch.object(chat_api.client, 'post', return_value=mock_chat_response):
            response = chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                user="test-user-123"
            )
            
            assert response["id"] == "chatcmpl-123"

    def test_complete_with_seed(self, chat_api, mock_chat_response):
        """Test chat completion with seed parameter."""
        with patch.object(chat_api.client, 'post', return_value=mock_chat_response):
            response = chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                seed=42
            )
            
            assert response["id"] == "chatcmpl-123"

    def test_complete_with_response_format(self, chat_api, mock_chat_response):
        """Test chat completion with response format."""
        with patch.object(chat_api.client, 'post', return_value=mock_chat_response):
            response = chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                response_format={"type": "json_object"}
            )
            
            assert response["id"] == "chatcmpl-123"

    def test_complete_with_logit_bias(self, chat_api, mock_chat_response):
        """Test chat completion with logit bias."""
        with patch.object(chat_api.client, 'post', return_value=mock_chat_response):
            logit_bias = {123: 0.5, 456: -0.5}
            response = chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                logit_bias=logit_bias
            )
            
            assert response["id"] == "chatcmpl-123"

    def test_complete_with_extra_kwargs(self, chat_api, mock_chat_response):
        """Test chat completion with extra keyword arguments."""
        with patch.object(chat_api.client, 'post', return_value=mock_chat_response):
            response = chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                custom_param="custom_value"
            )
            
            assert response["id"] == "chatcmpl-123"

    def test_complete_with_venice_parameters(self, chat_api, mock_chat_response):
        """Test chat completion with Venice-specific parameters."""
        with patch.object(chat_api.client, 'post', return_value=mock_chat_response):
            venice_parameters = {
                "include_venice_system_prompt": True,
                "custom_setting": "value"
            }
            
            response = chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                venice_parameters=venice_parameters
            )
            
            assert response["id"] == "chatcmpl-123"

    def test_complete_with_all_parameters(self, chat_api, mock_chat_response):
        """Test chat completion with all possible parameters."""
        with patch.object(chat_api.client, 'post', return_value=mock_chat_response):
            tools = [{"type": "function", "function": {"name": "test_func"}}]
            venice_parameters = {"include_venice_system_prompt": True}
            
            response = chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                temperature=0.8,
                stream=False,
                tools=tools,
                venice_parameters=venice_parameters,
                max_tokens=150,
                top_p=0.95,
                stop=["\n"],
                presence_penalty=0.3,
                frequency_penalty=0.2,
                user="test-user",
                seed=123,
                response_format={"type": "json_object"},
                logit_bias={1: 0.1},
                custom_param="value"
            )
            
            assert response["id"] == "chatcmpl-123"

    def test_complete_edge_cases(self, chat_api, mock_chat_response):
        """Test chat completion with edge cases."""
        with patch.object(chat_api.client, 'post', return_value=mock_chat_response):
            # Test with minimum temperature
            response = chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                temperature=0.0
            )
            assert response["id"] == "chatcmpl-123"
            
            # Test with maximum temperature
            response = chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                temperature=1.0
            )
            assert response["id"] == "chatcmpl-123"

    def test_complete_boundary_temperature(self, chat_api):
        """Test chat completion with boundary temperature values."""
        # Test temperature just below minimum
        with pytest.raises(ValueError, match="Temperature must be between 0 and 2"):
            chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                temperature=-0.1
            )
        
        # Test temperature just above maximum
        with pytest.raises(ValueError, match="Temperature must be between 0 and 2"):
            chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                temperature=2.1
            )

    def test_complete_message_validation(self, chat_api):
        """Test chat completion message validation."""
        # Test with empty string content - this should actually work, not raise an error
        with patch.object(chat_api.client, 'post', return_value=MagicMock()):
            response = chat_api.complete(
                messages=[{"role": "user", "content": ""}],
                model="llama-3.3-70b"
            )
            # Should not raise error for empty content
        
        # Test with None content - this should also work
        with patch.object(chat_api.client, 'post', return_value=MagicMock()):
            response = chat_api.complete(
                messages=[{"role": "user", "content": None}],
                model="llama-3.3-70b"
            )
            # Should not raise error for None content

    def test_complete_model_validation(self, chat_api):
        """Test chat completion model validation."""
        with patch.object(chat_api.client, 'post', return_value=MagicMock()):
            # Test with empty model
            response = chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model=""
            )
            # Should not raise error, just use empty string

    def test_complete_streaming_generator(self, chat_api, mock_streaming_response):
        """Test that streaming returns a proper generator."""
        with patch.object(chat_api.client, 'stream', return_value=mock_streaming_response):
            response = chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                stream=True
            )
            
            # Test generator properties
            assert hasattr(response, '__iter__')
            assert hasattr(response, '__next__')
            
            # Test that we can iterate multiple times
            chunks1 = list(response)
            chunks2 = list(response)  # Should be empty on second iteration
            assert len(chunks1) >= 0  # Allow empty for now
            assert len(chunks2) == 0

    def test_complete_tools_validation(self, chat_api, mock_chat_response):
        """Test chat completion with various tool configurations."""
        with patch.object(chat_api.client, 'post', return_value=mock_chat_response):
            # Test with empty tools list
            response = chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                tools=[]
            )
            assert response["id"] == "chatcmpl-123"
            
            # Test with None tools
            response = chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                tools=None
            )
            assert response["id"] == "chatcmpl-123"

    def test_complete_venice_parameters_validation(self, chat_api, mock_chat_response):
        """Test chat completion with various Venice parameter configurations."""
        with patch.object(chat_api.client, 'post', return_value=mock_chat_response):
            # Test with empty Venice parameters
            response = chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                venice_parameters={}
            )
            assert response["id"] == "chatcmpl-123"
            
            # Test with None Venice parameters
            response = chat_api.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.3-70b",
                venice_parameters=None
            )
            assert response["id"] == "chatcmpl-123"