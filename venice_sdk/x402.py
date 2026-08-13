"""
Venice AI SDK - x402 wallet balance / top-up / transactions.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from .client import HTTPClient
from .endpoints import X402Endpoints

logger = logging.getLogger(__name__)


class X402API:
    """Wallet-native Venice credits (x402)."""

    def __init__(self, client: HTTPClient):
        self.client = client

    def balance(self, wallet_address: str) -> Dict[str, Any]:
        """``GET /x402/balance/{walletAddress}``."""
        if not wallet_address:
            raise ValueError("wallet_address is required")
        path = X402Endpoints.BALANCE.format(walletAddress=wallet_address)
        response = self.client.get(path)
        return response.json()

    def top_up(
        self,
        payment_signature: str,
        body: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        ``POST /x402/top-up`` with ``PAYMENT-SIGNATURE`` header.

        Args:
            payment_signature: x402 payment signature header value.
            body: Optional JSON body (Venice may accept empty object).
        """
        if not payment_signature:
            raise ValueError("payment_signature is required")
        headers = {"PAYMENT-SIGNATURE": payment_signature}
        response = self.client.post(
            X402Endpoints.TOP_UP,
            data=body if body is not None else {},
            headers=headers,
            **kwargs,
        )
        return response.json()

    def transactions(self, wallet_address: str, **kwargs: Any) -> Dict[str, Any]:
        """``GET /x402/transactions/{walletAddress}``."""
        if not wallet_address:
            raise ValueError("wallet_address is required")
        path = X402Endpoints.TRANSACTIONS.format(walletAddress=wallet_address)
        response = self.client.get(path, **kwargs)
        return response.json()
