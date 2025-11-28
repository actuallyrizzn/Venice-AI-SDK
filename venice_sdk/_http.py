from __future__ import annotations

from typing import Optional

from .client import HTTPClient
from .config import load_config


def ensure_http_client(client: Optional[HTTPClient]) -> HTTPClient:
    """Return a concrete HTTPClient, instantiating one if necessary."""
    if client is not None:
        return client
    return HTTPClient(load_config())
