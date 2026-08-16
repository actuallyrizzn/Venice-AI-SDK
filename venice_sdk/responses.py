"""
Venice AI SDK - OpenAI-compatible Responses API (Alpha).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, List, Optional, Union

from .client import HTTPClient
from .endpoints import ChatEndpoints

logger = logging.getLogger(__name__)

JSONDict = Dict[str, Any]


def _output_item_text(content: Any) -> str:
    """Flatten Responses API content blocks into plain text."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        for key in ("text", "output_text", "content"):
            value = content.get(key)
            if isinstance(value, str):
                return value
        return _output_item_text(content.get("content"))
    if isinstance(content, list):
        return "".join(_output_item_text(part) for part in content)
    return str(content)


@dataclass
class ResponseOutputItem:
    """A single item in a Responses API ``output`` array."""

    type: str
    id: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    content: Any = None
    raw: JSONDict = field(default_factory=dict)

    def text(self) -> str:
        """Plain text for this item, if any."""
        return _output_item_text(self.content)

    @classmethod
    def from_dict(cls, data: Any) -> "ResponseOutputItem":
        if not isinstance(data, dict):
            return cls(type="unknown", content=data, raw={})
        return cls(
            type=str(data.get("type") or "unknown"),
            id=data.get("id"),
            role=data.get("role"),
            status=data.get("status"),
            content=data.get("content"),
            raw=data,
        )


@dataclass
class Response:
    """Typed ``POST /responses`` payload."""

    id: str = ""
    object: str = "response"
    created_at: Optional[int] = None
    model: Optional[str] = None
    status: Optional[str] = None
    output: List[ResponseOutputItem] = field(default_factory=list)
    usage: Optional[JSONDict] = None
    raw: JSONDict = field(default_factory=dict)

    @property
    def output_text(self) -> str:
        """Concatenate text from all output items."""
        return "".join(item.text() for item in self.output)

    @classmethod
    def from_dict(cls, data: Any) -> "Response":
        if not isinstance(data, dict):
            return cls(raw={"value": data})
        items = data.get("output") or data.get("choices") or []
        output = [ResponseOutputItem.from_dict(item) for item in items] if isinstance(items, list) else []
        created = data.get("created_at")
        if created is None:
            created = data.get("created")
        return cls(
            id=str(data.get("id") or ""),
            object=str(data.get("object") or "response"),
            created_at=created if isinstance(created, int) else None,
            model=data.get("model"),
            status=data.get("status"),
            output=output,
            usage=data.get("usage") if isinstance(data.get("usage"), dict) else None,
            raw=data,
        )


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
    ) -> Union[Response, Generator[JSONDict, None, None]]:
        """
        Create a response.

        Non-streaming calls return a :class:`Response`. Streaming still yields
        raw JSON chunks.

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
        return Response.from_dict(response.json())
