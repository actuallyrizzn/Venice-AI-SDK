from __future__ import annotations

from typing import Callable, Dict, Optional

from .client import HTTPClient, get_http_client_manager

_manual_override_client: Optional[HTTPClient] = None
_factory_http_clients: Dict[int, HTTPClient] = {}
_http_client_manager = get_http_client_manager()


def set_shared_http_client(client: Optional[HTTPClient]) -> None:
    """Override the cached shared HTTP client (primarily for testing)."""
    global _manual_override_client
    _manual_override_client = client
    if client is None:
        _http_client_manager.clear()
        _factory_http_clients.clear()


def reset_shared_http_client() -> None:
    """Clear the cached shared HTTP client so it will be recreated when needed."""
    set_shared_http_client(None)


def _default_http_client_factory(config: Optional["Config"] = None) -> HTTPClient:
    """Build an HTTPClient via the unified VeniceClient for compatibility."""
    from .venice_client import VeniceClient
    from .config import Config as _Config  # Local import to avoid cycles

    cfg: Optional[_Config] = config
    venice_client = VeniceClient(cfg)
    http_client = getattr(venice_client, "http_client", None)
    if isinstance(http_client, HTTPClient):
        return http_client
    if isinstance(venice_client, HTTPClient):
        return venice_client
    # Tests commonly patch VeniceClient to return a mock; fall back to that mock.
    return venice_client


_http_client_manager.set_builder(_default_http_client_factory)


def get_shared_http_client(
    factory: Optional[Callable[[], HTTPClient]] = None
) -> HTTPClient:
    """Return the cached shared HTTP client, creating it on first use."""
    if factory is None:
        if _manual_override_client is not None:
            return _manual_override_client
        return _http_client_manager.get_client()

    key = id(factory)
    if key not in _factory_http_clients:
        _factory_http_clients[key] = factory()
    return _factory_http_clients[key]


def ensure_http_client(
    client: Optional[HTTPClient],
    factory: Optional[Callable[[], HTTPClient]] = None,
) -> HTTPClient:
    """Return a concrete HTTPClient, instantiating one if necessary."""
    if client is not None:
        return client
    return get_shared_http_client(factory=factory)
