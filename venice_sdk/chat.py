"""
Chat API implementation for the Venice SDK.
"""

from dataclasses import dataclass
from typing import Any, Dict, Generator, List, Optional, Union

from .client import VeniceClient


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
    
    def __init__(self, client: VeniceClient):
        """
        Initialize the chat API.
        
        Args:
            client: VeniceClient instance
        """
        self.client = client
    
    def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        *,
        temperature: float = 0.15,
        stream: bool = False,
        max_completion_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        venice_parameters: Optional[Dict] = None,
        stop: Optional[Union[str, List[str]]] = None,
        **kwargs
    ) -> Union[ChatCompletion, Generator[ChatCompletion, None, None]]:
        """
        Create a chat completion.
        
        Args:
            messages: List of message objects
            model: ID of the model to use
            temperature: Sampling temperature (0-2)
            stream: Whether to stream the response
            max_completion_tokens: Maximum number of tokens to generate
            tools: List of tools available to the model
            venice_parameters: Venice-specific parameters
            stop: Stop sequences
            **kwargs: Additional parameters
            
        Returns:
            ChatCompletion object or generator for streaming responses
        """
        data: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }
        
        if max_completion_tokens is not None:
            data["max_completion_tokens"] = max_completion_tokens
        
        if tools is not None:
            data["tools"] = tools
        
        if venice_parameters is not None:
            data["venice_parameters"] = venice_parameters
        
        if stop is not None:
            data["stop"] = stop
        
        data.update(kwargs)
        
        if stream:
            return self._stream_completion(data)
        else:
            return self._create_completion(data)
    
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