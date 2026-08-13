"""
Venice AI SDK - Augment / developer tools (search, scrape, text parser).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, BinaryIO, Dict, Optional, Union

from .client import HTTPClient
from .endpoints import AugmentEndpoints

logger = logging.getLogger(__name__)


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
    ) -> Dict[str, Any]:
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
        return response.json()

    def scrape(self, url: str, **kwargs: Any) -> Dict[str, Any]:
        """Scrape a URL to markdown (``POST /augment/scrape``)."""
        if not url or not str(url).strip():
            raise ValueError("url must be a non-empty string")
        data: Dict[str, Any] = {"url": url, **kwargs}
        response = self.client.post(AugmentEndpoints.SCRAPE, data=data)
        return response.json()

    def parse_text(
        self,
        file: Union[str, Path, BinaryIO, bytes],
        response_format: Optional[str] = None,
        filename: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
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
            return response.json()
        return {"text": response.text}


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
