"""
Venice AI SDK - OpenAI-compatible Responses API (Alpha).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Generator, Optional, Union

from .client import HTTPClient
from .endpoints import ChatEndpoints

logger = logging.getLogger(__name__)

JSONDict = Dict[str, Any]


class ResponsesAPI:
    """``POST /responses`` — typed output blocks (reasoning, messages, tools, web search)."""

    def __init__(self, client: HTTPClient):
        self.client = client

    def create(
        self,
        model: str,
        input: Union[str, list, Dict[str, Any]],
        *,
        stream: bool = False,
        include: Optional[Any] = None,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        fallbacks: Optional[Any] = None,
        reasoning: Optional[Any] = None,
        tools: Optional[Any] = None,
        tool_choice: Optional[Any] = None,
        web_search: Optional[Any] = None,
        venice_parameters: Optional[JSONDict] = None,
        **kwargs: Any,
    ) -> Union[JSONDict, Generator[JSONDict, None, None]]:
        """
        Create a response.

        Note: E2EE models are not supported on this route — use chat completions.
        """
        if not model:
            raise ValueError("model is required")
        data: JSONDict = {
            "model": model,
            "input": input,
            "stream": stream,
        }
        optional = {
            "include": include,
            "max_output_tokens": max_output_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "fallbacks": fallbacks,
            "reasoning": reasoning,
            "tools": tools,
            "tool_choice": tool_choice,
            "web_search": web_search,
            "venice_parameters": venice_parameters,
        }
        for key, value in optional.items():
            if value is not None:
                data[key] = value
        if kwargs:
            data.update(kwargs)

        if stream:
            return self.client.stream(ChatEndpoints.RESPONSES, data=data)

        response = self.client.post(ChatEndpoints.RESPONSES, data=data)
        return response.json()
