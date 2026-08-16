"""
Venice AI SDK - x402 wallet balance / top-up / transactions.
"""

from __future__ import annotations

import base64
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Protocol, Union

from .client import HTTPClient
from .endpoints import X402Endpoints

logger = logging.getLogger(__name__)

JSONDict = Dict[str, Any]
SignerFn = Callable[[JSONDict], str]


class PaymentSigner(Protocol):
    """Wallet / client that can sign an x402 payment payload."""

    def sign_payment(self, payload: JSONDict) -> str:
        """Return the ``PAYMENT-SIGNATURE`` header value for ``payload``."""
        ...


@dataclass
class X402Balance:
    """Typed ``GET /x402/balance/{walletAddress}`` payload."""

    wallet_address: str = ""
    balance: Any = None
    raw: JSONDict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Any, wallet_address: str = "") -> "X402Balance":
        if not isinstance(data, dict):
            return cls(wallet_address=wallet_address, balance=data, raw={"value": data})
        return cls(
            wallet_address=str(
                data.get("walletAddress")
                or data.get("wallet_address")
                or wallet_address
            ),
            balance=data.get("balance") if "balance" in data else data.get("credits"),
            raw=data,
        )


@dataclass
class X402TopUpResult:
    """Typed ``POST /x402/top-up`` payload."""

    success: Optional[bool] = None
    transaction_id: Optional[str] = None
    raw: JSONDict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Any) -> "X402TopUpResult":
        if not isinstance(data, dict):
            return cls(raw={"value": data})
        success = data.get("success")
        if success is None:
            success = data.get("ok")
        return cls(
            success=bool(success) if success is not None else None,
            transaction_id=data.get("transaction_id")
            or data.get("transactionId")
            or data.get("id"),
            raw=data,
        )


@dataclass
class X402Transactions:
    """Typed ``GET /x402/transactions/{walletAddress}`` payload."""

    wallet_address: str = ""
    transactions: Any = None
    raw: JSONDict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Any, wallet_address: str = "") -> "X402Transactions":
        if not isinstance(data, dict):
            return cls(wallet_address=wallet_address, transactions=data, raw={"value": data})
        txns = data.get("transactions")
        if txns is None:
            txns = data.get("data")
        return cls(
            wallet_address=str(
                data.get("walletAddress")
                or data.get("wallet_address")
                or wallet_address
            ),
            transactions=txns,
            raw=data,
        )


def build_payment_payload(
    *,
    network: str,
    amount: Union[str, int, float],
    pay_to: str,
    asset: Optional[str] = None,
    extra: Optional[JSONDict] = None,
) -> JSONDict:
    """
    Build the canonical unsigned x402 payment object a wallet should sign.

    Venice's top-up route still requires the resulting signature in the
    ``PAYMENT-SIGNATURE`` header — this helper is the SDK side of that wallet
    flow. Pass the dict to :class:`PaymentSigner.sign_payment` (or any callable)
    then :meth:`X402API.top_up`.
    """
    if not network or not str(network).strip():
        raise ValueError("network is required")
    if amount is None or (isinstance(amount, str) and not amount.strip()):
        raise ValueError("amount is required")
    if not pay_to or not str(pay_to).strip():
        raise ValueError("pay_to is required")
    payload: JSONDict = {
        "network": str(network).strip(),
        "amount": str(amount),
        "payTo": str(pay_to).strip(),
    }
    if asset:
        payload["asset"] = asset
    if extra:
        payload.update(extra)
    return payload


def encode_payment_signature(payment: JSONDict) -> str:
    """Base64-encode a (usually already-signed) payment object for the header."""
    if not isinstance(payment, dict) or not payment:
        raise ValueError("payment must be a non-empty dict")
    blob = json.dumps(payment, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return base64.b64encode(blob).decode("ascii")


def decode_payment_signature(signature: str) -> JSONDict:
    """Decode a base64 JSON ``PAYMENT-SIGNATURE`` back to a dict when possible."""
    if not signature or not str(signature).strip():
        raise ValueError("signature is required")
    raw = str(signature).strip()
    try:
        decoded = base64.b64decode(raw)
        data = json.loads(decoded.decode("utf-8"))
        if isinstance(data, dict):
            return data
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        pass
    raise ValueError("signature is not a base64-encoded JSON payment object")


def _invoke_signer(signer: Union[PaymentSigner, SignerFn], payload: JSONDict) -> str:
    if hasattr(signer, "sign_payment"):
        signature = signer.sign_payment(payload)  # type: ignore[union-attr]
    elif callable(signer):
        signature = signer(payload)
    else:
        raise TypeError("signer must be callable or implement sign_payment()")
    if not signature or not isinstance(signature, str):
        raise ValueError("signer must return a non-empty payment signature string")
    return signature


class X402API:
    """Wallet-native Venice credits (x402)."""

    def __init__(self, client: HTTPClient):
        self.client = client

    def balance(self, wallet_address: str) -> X402Balance:
        """``GET /x402/balance/{walletAddress}``."""
        if not wallet_address:
            raise ValueError("wallet_address is required")
        path = X402Endpoints.BALANCE.format(walletAddress=wallet_address)
        response = self.client.get(path)
        return X402Balance.from_dict(response.json(), wallet_address=wallet_address)

    def top_up(
        self,
        payment_signature: str,
        body: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> X402TopUpResult:
        """
        ``POST /x402/top-up`` with ``PAYMENT-SIGNATURE`` header.

        The signature must come from a wallet (see :meth:`top_up_with_signer`).
        Passing an empty string is rejected — there is no SDK-side unsigned top-up.

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
        return X402TopUpResult.from_dict(response.json())

    def top_up_with_signer(
        self,
        signer: Union[PaymentSigner, SignerFn],
        *,
        network: str,
        amount: Union[str, int, float],
        pay_to: str,
        asset: Optional[str] = None,
        extra: Optional[JSONDict] = None,
        body: Optional[JSONDict] = None,
        **kwargs: Any,
    ) -> X402TopUpResult:
        """
        Build a payment payload, ask ``signer`` for a wallet signature, then top up.

        ``signer`` is either ``sign_payment(payload) -> str`` or a callable with
        the same shape. The SDK never holds keys; the wallet does.
        """
        payload = build_payment_payload(
            network=network,
            amount=amount,
            pay_to=pay_to,
            asset=asset,
            extra=extra,
        )
        signature = _invoke_signer(signer, payload)
        return self.top_up(signature, body=body, **kwargs)

    def transactions(self, wallet_address: str, **kwargs: Any) -> X402Transactions:
        """``GET /x402/transactions/{walletAddress}``."""
        if not wallet_address:
            raise ValueError("wallet_address is required")
        path = X402Endpoints.TRANSACTIONS.format(walletAddress=wallet_address)
        response = self.client.get(path, **kwargs)
        return X402Transactions.from_dict(response.json(), wallet_address=wallet_address)
