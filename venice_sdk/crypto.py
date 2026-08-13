"""
Venice AI SDK - Crypto RPC (networks + JSON-RPC proxy).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Union

from .client import HTTPClient
from .endpoints import CryptoEndpoints

logger = logging.getLogger(__name__)


class CryptoAPI:
    """Blockchain RPC via Venice credits."""

    def __init__(self, client: HTTPClient):
        self.client = client

    def networks(self) -> Any:
        """List supported networks (``GET /crypto/rpc/networks``)."""
        response = self.client.get(CryptoEndpoints.NETWORKS)
        return response.json()

    def rpc(
        self,
        network: str,
        method: Optional[str] = None,
        params: Optional[List[Any]] = None,
        *,
        id: Union[int, str] = 1,
        jsonrpc: str = "2.0",
        batch: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Proxy a JSON-RPC request (``POST /crypto/rpc/{network}``).

        Pass either ``method`` (+ optional ``params``) for a single call, or
        ``batch`` for up to 100 batched requests.
        """
        if not network:
            raise ValueError("network is required")
        path = CryptoEndpoints.RPC.format(network=network)
        if batch is not None:
            payload: Any = batch
        else:
            if not method:
                raise ValueError("method is required unless batch is provided")
            payload = {
                "jsonrpc": jsonrpc,
                "id": id,
                "method": method,
                "params": params if params is not None else [],
            }
            if kwargs:
                payload.update(kwargs)
        response = self.client.post(path, data=payload)
        return response.json()
