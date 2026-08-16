"""
Chat API implementation for the Venice SDK.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, List, Optional, Union, cast

from .client import HTTPClient
from ._http import ensure_http_client
from .errors import VeniceAPIError

JSONDict = Dict[str, Any]
ChatStream = Generator[str, None, None]
MessageContent = Union[str, List[JSONDict]]
ChatMessageInput = Union["Message", JSONDict]

logger = logging.getLogger(__name__)

_MULTIMODAL_PART_TYPES = {
    "text",
    "image_url",
    "input_audio",
    "video_url",
    "input_image",
    "input_video",
}


@dataclass
class Message:
    """A message in a chat conversation.

    ``content`` may be a string or a multimodal content-part list
    (``text`` / ``image_url`` / ``input_audio`` / ``video_url``).
    """

    role: str
    content: Optional[MessageContent] = None
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[JSONDict]] = field(default=None)

    def text_content(self) -> str:
        """Flatten string or multimodal ``text`` parts into one string."""
        if self.content is None:
            return ""
        if isinstance(self.content, str):
            return self.content
        parts: List[str] = []
        for part in self.content:
            if not isinstance(part, dict):
                continue
            if part.get("type") == "text" and part.get("text") is not None:
                parts.append(str(part.get("text")))
            elif "text" in part and "type" not in part:
                parts.append(str(part.get("text")))
        return "".join(parts)

    def to_dict(self) -> JSONDict:
        """Serialize to a chat-completions message payload."""
        payload: JSONDict = {"role": self.role}
        if self.content is not None:
            payload["content"] = self.content
        if self.name is not None:
            payload["name"] = self.name
        if self.tool_call_id is not None:
            payload["tool_call_id"] = self.tool_call_id
        if self.tool_calls is not None:
            payload["tool_calls"] = self.tool_calls
        return payload

    @classmethod
    def from_dict(cls, data: JSONDict) -> "Message":
        if not isinstance(data, dict):
            raise ValueError("Message payload must be a dictionary")
        return cls(
            role=str(data.get("role") or ""),
            content=data.get("content"),
            name=data.get("name"),
            tool_call_id=data.get("tool_call_id"),
            tool_calls=data.get("tool_calls") if isinstance(data.get("tool_calls"), list) else None,
        )


def _coerce_message_dict(message: ChatMessageInput, index: int) -> JSONDict:
    if isinstance(message, Message):
        payload = message.to_dict()
    elif isinstance(message, dict):
        payload = dict(message)
    else:
        raise ValueError(f"Message {index} must be a dictionary or Message")
    return payload


def _validate_message_payload(payload: JSONDict, index: int) -> None:
    allowed_roles = {"system", "user", "assistant", "tool"}
    if "role" not in payload:
        raise ValueError(f"Message {index} must have a 'role' field")
    if "content" not in payload and "tool_calls" not in payload:
        raise ValueError(f"Message {index} must have a 'content' or 'tool_calls' field")
    if payload["role"] not in allowed_roles:
        raise ValueError(f"Message {index} has invalid role: {payload['role']}")
    content = payload.get("content")
    if content is None:
        return
    if isinstance(content, str):
        return
    if not isinstance(content, list):
        raise ValueError(
            f"Message {index} content must be a string or a list of content parts"
        )
    for part_i, part in enumerate(content):
        if not isinstance(part, dict):
            raise ValueError(
                f"Message {index} content part {part_i} must be an object"
            )
        part_type = part.get("type")
        if not part_type:
            raise ValueError(
                f"Message {index} content part {part_i} must have a 'type' field"
            )
        if part_type not in _MULTIMODAL_PART_TYPES:
            raise ValueError(
                f"Message {index} content part {part_i} has unsupported type: {part_type}"
            )



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
        messages: List[ChatMessageInput],
        model: str = "llama-3.3-70b",
        temperature: float = 0.7,
        stream: bool = False,
        tools: Optional[List[JSONDict]] = None,
        tool_choice: Optional[Any] = None,
        venice_parameters: Optional[JSONDict] = None,
        prompt_cache_key: Optional[str] = None,
        # Additional parameters from Swagger spec
        frequency_penalty: Optional[float] = None,
        logprobs: Optional[bool] = None,
        top_logprobs: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        max_tokens: Optional[int] = None,
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
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        response_format: Optional[Any] = None,
        parallel_tool_calls: Optional[bool] = None,
        reasoning: Optional[Any] = None,
        reasoning_effort: Optional[Any] = None,
        fallbacks: Optional[Any] = None,
        **kwargs: Any
    ) -> Union[JSONDict, ChatStream]:
        """
        Create a chat completion.

        Args:
            messages: List of messages in the conversation. Each item may be a
                dict or :class:`Message`. ``content`` may be a string or a
                multimodal content-part array (text / image_url / input_audio /
                video_url). Roles include ``system``, ``user``, ``assistant``,
                and ``tool``.
            model: Model to use for completion
            temperature: Sampling temperature (0-1)
            stream: Whether to stream the response
            tools: Optional list of tools for function calling
            tool_choice: Optional tool choice control
            venice_parameters: Optional Venice-specific parameters. Supported keys include:
                character_slug, include_venice_system_prompt, enable_web_search ("off"|"on"|"auto"),
                strip_thinking_response, disable_thinking, enable_web_scraping, enable_x_search,
                enable_web_citations, include_search_results_in_stream,
                return_search_results_as_documents, enable_e2ee.
            frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on frequency
            logprobs: Whether to include log probabilities in the response
            top_logprobs: Number of highest probability tokens to return for each token position
            max_completion_tokens: Upper bound for tokens that can be generated
            max_tokens: Legacy max tokens alias
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
            top_p: Nucleus sampling
            top_k: Top-k sampling
            response_format: Structured output / JSON schema control
            parallel_tool_calls: Whether to allow parallel tool calls
            reasoning: Reasoning controls for thinking models
            reasoning_effort: Reasoning effort hint
            fallbacks: Optional model fallbacks
            prompt_cache_key: Optional routing hint for prompt caching (improves cache hit rates)
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
        max_allowed_temp = min(max_temp, 2.0) if max_temp is not None else 1.0
        if not 0 <= temperature <= max_allowed_temp:
            raise ValueError(
                "Temperature must be between 0 and 1 for default requests. "
                "Temperature must be between 0 and 2 per API limits."
            )
        
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
        
        # Validate and coerce message format
        normalized: List[JSONDict] = []
        for i, message in enumerate(messages):
            payload = _coerce_message_dict(message, i)
            _validate_message_payload(payload, i)
            normalized.append(payload)

        data = {
            "messages": normalized,
            "model": model,
            "temperature": temperature,
            "stream": stream,
        }
        if n != 1:
            data["n"] = n
        
        # Add optional parameters if provided
        optional_params = {
            "tools": tools,
            "tool_choice": tool_choice,
            "venice_parameters": venice_parameters,
            "prompt_cache_key": prompt_cache_key,
            "frequency_penalty": frequency_penalty,
            "logprobs": logprobs,
            "top_logprobs": top_logprobs,
            "max_completion_tokens": max_completion_tokens,
            "max_tokens": max_tokens,
            "max_temp": max_temp,
            "min_p": min_p,
            "min_temp": min_temp,
            "presence_penalty": presence_penalty,
            "repetition_penalty": repetition_penalty,
            "seed": seed,
            "stop": stop,
            "stop_token_ids": stop_token_ids,
            "stream_options": stream_options,
            "top_p": top_p,
            "top_k": top_k,
            "response_format": response_format,
            "parallel_tool_calls": parallel_tool_calls,
            "reasoning": reasoning,
            "reasoning_effort": reasoning_effort,
            "fallbacks": fallbacks,
        }
        
        for key, value in optional_params.items():
            if value is not None:
                data[key] = value
        
        # Allow additional optional parameters (e.g., max_tokens, etc.)
        if kwargs:
            data.update(kwargs)

        logger.debug(
            "Chat completion request (model=%s, stream=%s, message_count=%s)",
            model,
            stream,
            len(messages),
        )

        if stream:
            stream_response = self.client.stream("chat/completions", data=data)
            logger.debug("Streaming chat completion started for model %s", model)
            return self._stream_text_chunks(stream_response)

        http_response = self.client.post("chat/completions", data=data)
        logger.debug("Chat completion finished for model %s", model)
        return cast(JSONDict, http_response.json())
    
    def _create_completion(self, data: JSONDict) -> ChatCompletion:
        """Create a non-streaming completion."""
        response = self.client.post("chat/completions", data=data)
        result = cast(JSONDict, response.json())
        
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
                        content=choice["message"].get("content"),
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
        messages: List[ChatMessageInput],
        model: str = "llama-3.3-70b",
        temperature: float = 0.7,
        tools: Optional[List[JSONDict]] = None,
        venice_parameters: Optional[JSONDict] = None,
        **kwargs: Any
    ) -> ChatStream:
        """
        Create a streaming chat completion.

        Args:
            messages: List of messages in the conversation
            model: Model to use for completion
            temperature: Sampling temperature (0-2)
            tools: Optional list of tools for function calling
            venice_parameters: Optional Venice-specific parameters
            **kwargs: Additional optional parameters

        Returns:
            Generator yielding response chunks as strings in SSE format
        """
        data = {
            "messages": [_coerce_message_dict(m, i) for i, m in enumerate(messages)],
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
            if chunk.get("object") == "chat.completion.chunk":
                yield f"data: {json.dumps(chunk)}\n\n"
            elif chunk.get("object") == "chat.completion":
                yield f"data: {json.dumps(chunk)}\n\n"
        yield "data: [DONE]\n\n"
    
    def _stream_text_chunks(self, response: Generator[JSONDict, None, None]) -> ChatStream:
        """Yield plain text content from streaming delta chunks."""
        for chunk in response:
            choices = chunk.get("choices") or []
            if not choices:
                continue
            delta = choices[0].get("delta", {})
            content = delta.get("content")
            if isinstance(content, str):
                yield content
    
    def _stream_completion(self, data: JSONDict) -> Generator[ChatCompletion, None, None]:
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
    messages: List[ChatMessageInput],
    model: str = "llama-3.3-70b",
    temperature: float = 0.7,
    stream: bool = False,
    tools: Optional[List[JSONDict]] = None,
    client: Optional[HTTPClient] = None,
    **kwargs: Any
) -> Union[JSONDict, ChatStream]:
    """
    Create a chat completion.

    Args:
        messages: List of messages in the conversation
        model: Model to use for completion
        temperature: Sampling temperature (0-2)
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
    http_client = ensure_http_client(client, factory=HTTPClient)
    chat_api = ChatAPI(http_client)
    return chat_api.complete(
        messages=messages,
        model=model,
        temperature=temperature,
        stream=stream,
        tools=tools,
        **kwargs
    ) 