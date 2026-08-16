"""
Venice AI SDK - Augment / developer tools (search, scrape, text parser).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Union

from .client import HTTPClient
from .endpoints import AugmentEndpoints

logger = logging.getLogger(__name__)

JSONDict = Dict[str, Any]


def _first_str(data: JSONDict, *keys: str) -> Optional[str]:
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value:
            return value
    return None


@dataclass
class SearchHit:
    """One web-search result."""

    title: Optional[str] = None
    url: Optional[str] = None
    snippet: Optional[str] = None
    raw: JSONDict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Any) -> "SearchHit":
        if not isinstance(data, dict):
            return cls(snippet=str(data) if data is not None else None, raw={})
        return cls(
            title=_first_str(data, "title", "name"),
            url=_first_str(data, "url", "link", "href"),
            snippet=_first_str(data, "snippet", "description", "content", "text"),
            raw=data,
        )


@dataclass
class SearchResponse:
    """Typed ``POST /augment/search`` payload."""

    query: Optional[str] = None
    provider: Optional[str] = None
    results: List[SearchHit] = field(default_factory=list)
    raw: JSONDict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Any, query: Optional[str] = None) -> "SearchResponse":
        if not isinstance(data, dict):
            return cls(query=query, raw={"value": data})
        items = data.get("results") or data.get("data") or data.get("organic") or []
        hits = [SearchHit.from_dict(item) for item in items] if isinstance(items, list) else []
        return cls(
            query=data.get("query") or query,
            provider=data.get("search_provider") or data.get("provider"),
            results=hits,
            raw=data,
        )


@dataclass
class ScrapeResponse:
    """Typed ``POST /augment/scrape`` payload."""

    url: Optional[str] = None
    title: Optional[str] = None
    markdown: Optional[str] = None
    raw: JSONDict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Any, url: Optional[str] = None) -> "ScrapeResponse":
        if not isinstance(data, dict):
            text = str(data) if data is not None else None
            return cls(url=url, markdown=text, raw={"value": data})
        return cls(
            url=data.get("url") or url,
            title=_first_str(data, "title", "name"),
            markdown=_first_str(data, "markdown", "content", "text") or "",
            raw=data,
        )


@dataclass
class ParsedDocument:
    """Typed ``POST /augment/text-parser`` payload."""

    text: str = ""
    filename: Optional[str] = None
    raw: JSONDict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Any, filename: Optional[str] = None) -> "ParsedDocument":
        if isinstance(data, str):
            return cls(text=data, filename=filename, raw={"text": data})
        if not isinstance(data, dict):
            return cls(text=str(data) if data is not None else "", filename=filename, raw={})
        text = data.get("text") or data.get("content") or data.get("markdown") or ""
        return cls(
            text=str(text),
            filename=data.get("filename") or filename,
            raw=data,
        )


class AugmentAPI:
    """Web search, scrape, and document text parsing."""

    def __init__(self, client: HTTPClient):
        self.client = client

    def search(
        self,
        query: str,
        limit: Optional[int] = None,
        search_provider: Optional[str] = None,
        **kwargs: Any,
    ) -> SearchResponse:
        """
        Search the web (``POST /augment/search``).

        Args:
            query: Search query.
            limit: Max results.
            search_provider: e.g. ``brave`` (ZDR) or ``google`` (proxied).
        """
        if not query or not str(query).strip():
            raise ValueError("query must be a non-empty string")
        data: Dict[str, Any] = {"query": query, **kwargs}
        if limit is not None:
            data["limit"] = limit
        if search_provider is not None:
            data["search_provider"] = search_provider
        response = self.client.post(AugmentEndpoints.SEARCH, data=data)
        return SearchResponse.from_dict(response.json(), query=query)

    def scrape(self, url: str, **kwargs: Any) -> ScrapeResponse:
        """Scrape a URL to markdown (``POST /augment/scrape``)."""
        if not url or not str(url).strip():
            raise ValueError("url must be a non-empty string")
        data: Dict[str, Any] = {"url": url, **kwargs}
        response = self.client.post(AugmentEndpoints.SCRAPE, data=data)
        return ScrapeResponse.from_dict(response.json(), url=url)

    def parse_text(
        self,
        file: Union[str, Path, BinaryIO, bytes],
        response_format: Optional[str] = None,
        filename: Optional[str] = None,
        **kwargs: Any,
    ) -> ParsedDocument:
        """
        Extract text from a document (``POST /augment/text-parser``).

        Args:
            file: Path, file object, or bytes (PDF/DOCX/XLSX/text).
            response_format: Optional Venice response_format value.
            filename: Override filename when passing bytes/file objects.
        """
        files, form = _build_file_multipart(
            file,
            field_name="file",
            filename=filename,
            extra_fields={"response_format": response_format, **kwargs},
        )
        response = self.client.post_multipart(
            AugmentEndpoints.TEXT_PARSER,
            files=files,
            form_data=form or None,
        )
        ctype = (response.headers.get("Content-Type") or "").lower()
        if "application/json" in ctype:
            return ParsedDocument.from_dict(response.json(), filename=filename)
        return ParsedDocument(text=response.text or "", filename=filename, raw={"text": response.text})


def _build_file_multipart(
    file: Union[str, Path, BinaryIO, bytes],
    *,
    field_name: str,
    filename: Optional[str],
    extra_fields: Optional[Dict[str, Any]] = None,
) -> tuple:
    """Return (files, form_data) for requests multipart."""
    form: Dict[str, Any] = {}
    for key, value in (extra_fields or {}).items():
        if value is not None:
            form[key] = value if not isinstance(value, bool) else ("true" if value else "false")

    if isinstance(file, bytes):
        name = filename or "upload.bin"
        files = {field_name: (name, file)}
        return files, form

    if isinstance(file, (str, Path)):
        path = Path(file)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")
        files = {field_name: (filename or path.name, path.read_bytes())}
        return files, form

    # file-like
    name = filename or getattr(file, "name", None) or "upload.bin"
    if hasattr(file, "read"):
        content = file.read()
        if isinstance(content, str):
            content = content.encode("utf-8")
        files = {field_name: (Path(str(name)).name, content)}
        return files, form

    raise TypeError("file must be a path, bytes, or file-like object")
