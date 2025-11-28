from __future__ import annotations

from typing import Optional

from .client import HTTPClient
from . import config as _config


def ensure_http_client(client: Optional[HTTPClient]) -> HTTPClient:
    """Return a concrete HTTPClient, instantiating one if necessary."""
    if client is not None:
        return client
    from .venice_client import VeniceClient

    config = _config.load_config()
    venice_client = VeniceClient(config)
    http_client = getattr(venice_client, "http_client", None)
    if isinstance(http_client, HTTPClient):
        return http_client
    return venice_client
