"""Comprehensive unit tests for new API parity modules (0.3.1)."""

from __future__ import annotations

import io
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from venice_sdk.augment import AugmentAPI, _build_file_multipart
from venice_sdk.crypto import CryptoAPI
from venice_sdk.responses import ResponsesAPI
from venice_sdk.x402 import X402API
from venice_sdk.tee import TEEAPI
from venice_sdk.endpoints import (
    AugmentEndpoints,
    ChatEndpoints,
    CryptoEndpoints,
    TEEEndpoints,
    X402Endpoints,
)
from venice_sdk.errors import VeniceAPIError, ModelNotFoundError, BillingError


@pytest.fixture
def mock_client():
    return MagicMock()


class TestAugmentAPI:
    def test_search_success(self, mock_client):
        mock_client.post.return_value.json.return_value = {"results": []}
        api = AugmentAPI(mock_client)
        out = api.search("hello", limit=3, search_provider="brave", foo=1)
        assert out.results == []
        assert out.query == "hello"
        assert out.raw == {"results": []}
        mock_client.post.assert_called_once()
        args, kwargs = mock_client.post.call_args
        assert args[0] == AugmentEndpoints.SEARCH
        assert kwargs["data"]["query"] == "hello"
        assert kwargs["data"]["limit"] == 3
        assert kwargs["data"]["search_provider"] == "brave"
        assert kwargs["data"]["foo"] == 1

    def test_search_empty_raises(self, mock_client):
        with pytest.raises(ValueError):
            AugmentAPI(mock_client).search("  ")

    def test_scrape_success(self, mock_client):
        mock_client.post.return_value.json.return_value = {"markdown": "# hi"}
        out = AugmentAPI(mock_client).scrape("https://example.com", depth=1)
        assert out.markdown.startswith("#")
        assert mock_client.post.call_args.kwargs["data"]["url"] == "https://example.com"

    def test_scrape_empty_raises(self, mock_client):
        with pytest.raises(ValueError):
            AugmentAPI(mock_client).scrape("")

    def test_parse_text_json(self, mock_client, tmp_path):
        path = tmp_path / "doc.txt"
        path.write_text("hello")
        resp = MagicMock()
        resp.headers = {"Content-Type": "application/json"}
        resp.json.return_value = {"text": "hello"}
        mock_client.post_multipart.return_value = resp
        out = AugmentAPI(mock_client).parse_text(path, response_format="json")
        assert out.text == "hello"

    def test_parse_text_plain(self, mock_client):
        resp = MagicMock()
        resp.headers = {"Content-Type": "text/plain"}
        resp.text = "plain"
        mock_client.post_multipart.return_value = resp
        out = AugmentAPI(mock_client).parse_text(b"abc", filename="a.bin")
        assert out.text == "plain"

    def test_build_multipart_variants(self, tmp_path):
        files, form = _build_file_multipart(
            b"x", field_name="file", filename="f.bin", extra_fields={"flag": True, "off": False, "skip": None}
        )
        assert files["file"][0] == "f.bin"
        assert form["flag"] == "true"
        assert form["off"] == "false"
        assert "skip" not in form

        p = tmp_path / "a.pdf"
        p.write_bytes(b"%PDF")
        files, _ = _build_file_multipart(p, field_name="file", filename=None)
        assert files["file"][0] == "a.pdf"

        with pytest.raises(FileNotFoundError):
            _build_file_multipart(tmp_path / "missing", field_name="file", filename=None)

        bio = io.BytesIO(b"bytes")
        files, _ = _build_file_multipart(bio, field_name="file", filename=None)
        assert files["file"][1] == b"bytes"

        sio = io.StringIO("text")
        files, _ = _build_file_multipart(sio, field_name="file", filename="t.txt")
        assert files["file"][1] == b"text"

        with pytest.raises(TypeError):
            _build_file_multipart(123, field_name="file", filename=None)  # type: ignore[arg-type]


class TestCryptoAPI:
    def test_networks(self, mock_client):
        mock_client.get.return_value.json.return_value = {"networks": ["base"]}
        assert CryptoAPI(mock_client).networks()["networks"] == ["base"]
        mock_client.get.assert_called_once_with(CryptoEndpoints.NETWORKS)

    def test_rpc_single_and_batch(self, mock_client):
        mock_client.post.return_value.json.return_value = {"result": "0x1"}
        api = CryptoAPI(mock_client)
        api.rpc("base", method="eth_blockNumber", extra=1)
        path = CryptoEndpoints.RPC.format(network="base")
        payload = mock_client.post.call_args.kwargs["data"]
        assert payload["method"] == "eth_blockNumber"
        assert payload["params"] == []
        assert payload["extra"] == 1

        api.rpc("base", batch=[{"jsonrpc": "2.0", "id": 1, "method": "eth_chainId", "params": []}])
        assert isinstance(mock_client.post.call_args.kwargs["data"], list)

    def test_rpc_validation(self, mock_client):
        with pytest.raises(ValueError):
            CryptoAPI(mock_client).rpc("")
        with pytest.raises(ValueError):
            CryptoAPI(mock_client).rpc("base")


class TestResponsesAPI:
    def test_create_and_stream(self, mock_client):
        mock_client.post.return_value.json.return_value = {"id": "resp_1"}
        api = ResponsesAPI(mock_client)
        out = api.create(
            "llama-3.3-70b",
            "hi",
            include=["reasoning"],
            max_output_tokens=10,
            temperature=0.2,
            top_p=0.9,
            fallbacks=["a"],
            reasoning={"effort": "low"},
            tools=[],
            tool_choice="auto",
            web_search=True,
            venice_parameters={"enable_web_search": "off"},
            custom=1,
        )
        assert out.id == "resp_1"
        assert out.raw["id"] == "resp_1"
        data = mock_client.post.call_args.kwargs["data"]
        assert data["custom"] == 1
        assert mock_client.post.call_args.args[0] == ChatEndpoints.RESPONSES

        mock_client.stream.return_value = iter([{"type": "chunk"}])
        gen = api.create("m", "hi", stream=True)
        assert list(gen)[0]["type"] == "chunk"

    def test_empty_model(self, mock_client):
        with pytest.raises(ValueError):
            ResponsesAPI(mock_client).create("", "hi")


class TestX402API:
    def test_balance_topup_transactions(self, mock_client):
        mock_client.get.return_value.json.return_value = {"balance": 1}
        mock_client.post.return_value.json.return_value = {"ok": True}
        api = X402API(mock_client)
        assert api.balance("0xabc").balance == 1
        api.top_up("sig", body={"amount": 1})
        assert mock_client.post.call_args.kwargs["headers"]["PAYMENT-SIGNATURE"] == "sig"
        result = api.top_up("sig")
        assert result.raw.get("ok") is True
        assert mock_client.post.call_args.kwargs["data"] == {}
        txns = api.transactions("0xabc", params={"limit": 1})
        assert txns.wallet_address == "0xabc"
        assert "0xabc" in mock_client.get.call_args.args[0]

    def test_validation(self, mock_client):
        with pytest.raises(ValueError):
            X402API(mock_client).balance("")
        with pytest.raises(ValueError):
            X402API(mock_client).top_up("")
        with pytest.raises(ValueError):
            X402API(mock_client).transactions("")


class TestTEEAPI:
    def test_attestation_and_signature_success(self, mock_client):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"ok": True}
        mock_client.post.return_value = resp
        api = TEEAPI(mock_client)
        assert api.attestation(model="m")["ok"] is True
        assert api.signature(payload="x")["ok"] is True

    def test_attestation_error_json(self, mock_client):
        resp = MagicMock()
        resp.status_code = 400
        resp.json.return_value = {"error": "bad"}
        mock_client.post.return_value = resp
        with pytest.raises(VeniceAPIError):
            TEEAPI(mock_client).attestation()

    def test_attestation_error_non_json(self, mock_client):
        resp = MagicMock()
        resp.status_code = 500
        resp.json.side_effect = ValueError("no json")
        mock_client.post.return_value = resp
        with pytest.raises(VeniceAPIError):
            TEEAPI(mock_client).attestation()

    def test_signature_error_paths(self, mock_client):
        resp = MagicMock()
        resp.status_code = 400
        resp.json.return_value = {"error": "bad"}
        mock_client.post.return_value = resp
        with pytest.raises(VeniceAPIError):
            TEEAPI(mock_client).signature()
        resp.json.side_effect = ValueError("x")
        with pytest.raises(VeniceAPIError):
            TEEAPI(mock_client).signature()
