"""
Chat API implementation for the Venice SDK.
"""

import json
from dataclasses import dataclass
from typing import Any, Dict, Generator, List, Optional, Union

from .client import HTTPClient
from .errors import VeniceAPIError


@dataclass
class Message:
    """A message in a chat conversation."""
    role: str
    content: str


@dataclass
class Choice:
    """A choice in a chat completion response."""
    index: int
    message: Message
    finish_reason: str


@dataclass
class Usage:
    """Token usage statistics."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class ChatCompletion:
    """A chat completion response."""
    id: str
    object: str
    created: int
    model: str
    choices: List[Choice]
    usage: Usage


class ChatAPI:
    """
    API for chat completions.
    
    This class provides methods for interacting with the chat completion endpoint,
    including support for streaming responses and function calling.
    """
    
    def __init__(self, client: HTTPClient):
        """
        Initialize the chat API.
        
        Args:
            client: HTTPClient instance
        """
        self.client = client
    
    def complete(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama-3.3-70b",
        temperature: float = 0.7,
        stream: bool = False,
        tools: Optional[List[Dict[str, Any]]] = None,
        venice_parameters: Optional[Dict[str, Any]] = None,
        # Additional parameters from Swagger spec
        frequency_penalty: Optional[float] = None,
        logprobs: Optional[bool] = None,
        top_logprobs: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        max_temp: Optional[float] = None,
        min_p: Optional[float] = None,
        min_temp: Optional[float] = None,
        n: int = 1,
        presence_penalty: Optional[float] = None,
        repetition_penalty: Optional[float] = None,
        seed: Optional[int] = None,
        stop: Optional[Union[str, List[str]]] = None,
        stop_token_ids: Optional[List[int]] = None,
        stream_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Union[Dict, Generator[str, None, None]]:
        """
        Create a chat completion.

        Args:
            messages: List of messages in the conversation
            model: Model to use for completion
            temperature: Sampling temperature (0-2)
            stream: Whether to stream the response
            tools: Optional list of tools for function calling
            venice_parameters: Optional Venice-specific parameters (e.g., include_venice_system_prompt)
            frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on frequency
            logprobs: Whether to include log probabilities in the response
            top_logprobs: Number of highest probability tokens to return for each token position
            max_completion_tokens: Upper bound for tokens that can be generated
            max_temp: Maximum temperature value for dynamic temperature scaling (0-2)
            min_p: Minimum probability threshold for token selection (0-1)
            min_temp: Minimum temperature value for dynamic temperature scaling (0-2)
            n: Number of chat completion choices to generate (default 1)
            presence_penalty: Number between -2.0 and 2.0. Positive values penalize tokens based on presence
            repetition_penalty: Parameter for repetition penalty. 1.0 means no penalty, >1.0 discourages repetition
            seed: Random seed for reproducible responses
            stop: Up to 4 sequences where the API will stop generating
            stop_token_ids: Array of token IDs where the API will stop generating
            stream_options: Options for streaming (e.g., include_usage)
            **kwargs: Additional optional parameters to pass through

        Returns:
            If stream=False, returns the complete response as a dictionary
            If stream=True, returns a generator yielding response chunks as strings

        Raises:
            ValueError: If messages is empty or parameters are invalid
            VeniceAPIError: If the API request fails
        """
        if not messages:
            raise ValueError("Messages must be a non-empty list")
        if not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        
        # Validate parameter ranges
        if frequency_penalty is not None and not -2 <= frequency_penalty <= 2:
            raise ValueError("Frequency penalty must be between -2.0 and 2.0")
        if presence_penalty is not None and not -2 <= presence_penalty <= 2:
            raise ValueError("Presence penalty must be between -2.0 and 2.0")
        if repetition_penalty is not None and repetition_penalty < 0:
            raise ValueError("Repetition penalty must be >= 0")
        if max_temp is not None and not 0 <= max_temp <= 2:
            raise ValueError("Max temperature must be between 0 and 2")
        if min_temp is not None and not 0 <= min_temp <= 2:
            raise ValueError("Min temperature must be between 0 and 2")
        if min_p is not None and not 0 <= min_p <= 1:
            raise ValueError("Min p must be between 0 and 1")
        if top_logprobs is not None and top_logprobs < 0:
            raise ValueError("Top logprobs must be >= 0")
        if seed is not None and seed < 0:
            raise ValueError("Seed must be >= 0")
        if n < 1:
            raise ValueError("n must be >= 1")
        
        # Validate message format
        for i, message in enumerate(messages):
            if not isinstance(message, dict):
                raise ValueError(f"Message {i} must be a dictionary")
            if "role" not in message:
                raise ValueError(f"Message {i} must have a 'role' field")
            if "content" not in message:
                raise ValueError(f"Message {i} must have a 'content' field")
            if message["role"] not in ["system", "user", "assistant"]:
                raise ValueError(f"Message {i} has invalid role: {message['role']}")

        data = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "stream": stream,
            "n": n
        }
        
        # Add optional parameters if provided
        optional_params = {
            "tools": tools,
            "venice_parameters": venice_parameters,
            "frequency_penalty": frequency_penalty,
            "logprobs": logprobs,
            "top_logprobs": top_logprobs,
            "max_completion_tokens": max_completion_tokens,
            "max_temp": max_temp,
            "min_p": min_p,
            "min_temp": min_temp,
            "presence_penalty": presence_penalty,
            "repetition_penalty": repetition_penalty,
            "seed": seed,
            "stop": stop,
            "stop_token_ids": stop_token_ids,
            "stream_options": stream_options
        }
        
        for key, value in optional_params.items():
            if value is not None:
                data[key] = value
        
        # Allow additional optional parameters (e.g., max_tokens, etc.)
        if kwargs:
            data.update(kwargs)

        if stream:
            response = self.client.stream("chat/completions", data=data)
            return (chunk["choices"][0]["delta"]["content"] 
                   for chunk in response 
                   if "content" in chunk.get("choices", [{}])[0].get("delta", {}))
        else:
            response = self.client.post("chat/completions", data=data)
            return response.json()
    
    def _create_completion(self, data: Dict[str, Any]) -> ChatCompletion:
        """Create a non-streaming completion."""
        response = self.client.post("chat/completions", data=data)
        result = response.json()
        
        return ChatCompletion(
            id=result["id"],
            object=result["object"],
            created=result["created"],
            model=result["model"],
            choices=[
                Choice(
                    index=choice["index"],
                    message=Message(
                        role=choice["message"]["role"],
                        content=choice["message"]["content"]
                    ),
                    finish_reason=choice["finish_reason"]
                )
                for choice in result["choices"]
            ],
            usage=Usage(
                prompt_tokens=result["usage"]["prompt_tokens"],
                completion_tokens=result["usage"]["completion_tokens"],
                total_tokens=result["usage"]["total_tokens"]
            )
        )
    
    def complete_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama-3.3-70b",
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None,
        venice_parameters: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Generator[str, None, None]:
        """
        Create a streaming chat completion.

        Args:
            messages: List of messages in the conversation
            model: Model to use for completion
            temperature: Sampling temperature (0-1)
            tools: Optional list of tools for function calling
            venice_parameters: Optional Venice-specific parameters
            **kwargs: Additional optional parameters

        Returns:
            Generator yielding response chunks as strings in SSE format
        """
        data = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "stream": True
        }
        if tools:
            data["tools"] = tools
        if venice_parameters:
            data["venice_parameters"] = venice_parameters
        if kwargs:
            data.update(kwargs)

        response = self.client.stream("chat/completions", data=data)
        for chunk in response:
            # chunk is already in SSE format (string)
            if isinstance(chunk, str):
                yield chunk
            else:
                # Convert chunk to SSE format if it's a dict
                if chunk.get("object") == "chat.completion.chunk":
                    yield f"data: {json.dumps(chunk)}\n\n"
                elif chunk.get("object") == "chat.completion":
                    yield f"data: {json.dumps(chunk)}\n\n"
        
        # Send final SSE event
        yield "data: [DONE]\n\n"
    
    def _stream_completion(self, data: Dict[str, Any]) -> Generator[ChatCompletion, None, None]:
        """Create a streaming completion."""
        for chunk in self.client.stream("chat/completions", data=data):
            if chunk["object"] == "chat.completion.chunk":
                yield ChatCompletion(
                    id=chunk["id"],
                    object=chunk["object"],
                    created=chunk["created"],
                    model=chunk["model"],
                    choices=[
                        Choice(
                            index=choice["index"],
                            message=Message(
                                role=choice["delta"].get("role", "assistant"),
                                content=choice["delta"].get("content", "")
                            ),
                            finish_reason=choice.get("finish_reason")
                        )
                        for choice in chunk["choices"]
                    ],
                    usage=Usage(
                        prompt_tokens=0,
                        completion_tokens=0,
                        total_tokens=0
                    )
                ) 


def chat_complete(
    messages: List[Dict[str, str]],
    model: str = "llama-3.3-70b",
    temperature: float = 0.7,
    stream: bool = False,
    tools: Optional[List[Dict]] = None,
    client: Optional[HTTPClient] = None,
    **kwargs
) -> Union[Dict, Generator[str, None, None]]:
    """
    Create a chat completion.

    Args:
        messages: List of messages in the conversation
        model: Model to use for completion
        temperature: Sampling temperature (0-1)
        stream: Whether to stream the response
        tools: Optional list of tools to use
        client: Optional HTTPClient instance. If not provided, a new one will be created.
        **kwargs: Additional parameters to pass to the API

    Returns:
        Response data or generator for streaming responses

    Raises:
        ValueError: If messages is empty or temperature is invalid
        VeniceAPIError: If the request fails
    """
    client = client or HTTPClient()
    chat_api = ChatAPI(client)
    return chat_api.complete(
        messages=messages,
        model=model,
        temperature=temperature,
        stream=stream,
        tools=tools,
        **kwargs
    ) 