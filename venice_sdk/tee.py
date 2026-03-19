"""
Venice AI SDK - TEE (Trusted Execution Environment) Module

Verify that models run in a genuine Trusted Execution Environment and that
responses were produced inside the attested TEE enclave.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from .client import HTTPClient
from .endpoints import TEEEndpoints
from .errors import VeniceAPIError

logger = logging.getLogger(__name__)


class TEEAPI:
    """
    TEE attestation and signature verification API.

    Use these endpoints to verify that a model runs in a genuine TEE and that
    a response was produced inside the attested enclave. See Venice docs for
    TEE & E2EE models.
    """

    def __init__(self, client: HTTPClient):
        self.client = client

    def attestation(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Request TEE attestation to verify a model runs in a genuine Trusted Execution Environment.

        Returns attestation data for verification. See Venice API docs for request/response schema.

        Returns:
            Dict with attestation payload (format depends on API version).
        """
        response = self.client.post(TEEEndpoints.ATTESTATION, data=kwargs or {})
        if response.status_code >= 400:
            try:
                err = response.json()
                raise VeniceAPIError(err.get("error", "Attestation request failed"))
            except VeniceAPIError:
                raise
            except Exception:
                raise VeniceAPIError("Attestation request failed")
        return response.json()

    def signature(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Verify that a response was produced inside the attested TEE enclave.

        See Venice API docs for required parameters and response format.

        Returns:
            Dict with signature verification result.
        """
        response = self.client.post(TEEEndpoints.SIGNATURE, data=kwargs or {})
        if response.status_code >= 400:
            try:
                err = response.json()
                raise VeniceAPIError(err.get("error", "Signature request failed"))
            except VeniceAPIError:
                raise
            except Exception:
                raise VeniceAPIError("Signature request failed")
        return response.json()
