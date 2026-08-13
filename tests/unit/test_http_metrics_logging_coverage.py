"""Coverage-focused tests for HTTPClient multipart, retries, streaming, metrics, logging."""

from __future__ import annotations

import io
import json
import logging
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
import requests

from venice_sdk.client import HTTPClient, HTTPClientManager, get_http_client_manager
from venice_sdk.config import Config
from venice_sdk.errors import VeniceAPIError, VeniceConnectionError, RateLimitError
from venice_sdk.logging_config import StructuredFormatter, setup_logging
from venice_sdk.metrics import RateLimitMetrics, RateLimitEvent
from venice_sdk import _http


@pytest.fixture
def cfg():
    return Config(
        api_key="k" * 32,
        base_url="https://api.venice.ai/api/v1",
        timeout=5,
        max_retries=3,
        retry_delay=0,
        retry_backoff_factor=0.5,
        retry_status_codes=[429, 500, 502, 503, 504],
    )


@pytest.fixture
def client(cfg):
    return HTTPClient(cfg, enable_metrics=True)


def _resp(status=200, payload=None, headers=None, text=""):
    r = MagicMock()
    r.status_code = status
    r.headers = headers or {}
    if payload is not None:
        r.json.return_value = payload
    else:
        r.json.side_effect = ValueError("no json")
    r.text = text
    r.iter_lines.return_value = []
    return r


class TestHTTPClientCoverage:
    def test_post_multipart_restores_content_type(self, client):
        assert client.session.headers.get("Content-Type") == "application/json"
        ok = _resp(200, {"ok": True})
        with patch.object(client.session, "request", return_value=ok) as req:
            out = client.post_multipart("/audio/transcriptions", files={"file": ("a.wav", b"x")}, form_data={"model": "m"})
            assert out.json()["ok"] is True
            kwargs = req.call_args.kwargs
            assert kwargs["files"]["file"][0] == "a.wav"
            assert kwargs["data"]["model"] == "m"
            assert "json" not in kwargs
        assert client.session.headers.get("Content-Type") == "application/json"

    def test_post_multipart_no_prior_content_type(self, client):
        client.session.headers.pop("Content-Type", None)
        ok = _resp(200, {"ok": True})
        with patch.object(client.session, "request", return_value=ok):
            client.post_multipart("/x", files={"file": ("a", b"1")})
        # may or may not restore; ensure no crash

    def test_json_list_body(self, client):
        ok = _resp(200, [{"id": 1}])
        with patch.object(client.session, "request", return_value=ok) as req:
            client.post("/crypto/rpc/base", data=[{"jsonrpc": "2.0", "id": 1, "method": "eth_chainId", "params": []}])
            assert isinstance(req.call_args.kwargs["json"], list)

    def test_max_retries_clamp_and_default_timeout(self, cfg):
        cfg.max_retries = 0
        cfg.timeout = 9
        c = HTTPClient(cfg)
        ok = _resp(200, {})
        with patch.object(c.session, "request", return_value=ok) as req:
            c.get("/models")
            assert req.call_args.kwargs["timeout"] == 9

    def test_connection_error(self, client):
        with patch.object(client.session, "request", side_effect=requests.exceptions.ConnectionError("boom")):
            with pytest.raises(VeniceConnectionError):
                client.get("/models")

    def test_429_retry_then_success(self, client):
        limited = _resp(429, {"error": {"message": "slow"}}, headers={"Retry-After": "0", "X-RateLimit-Remaining": "0"})
        ok = _resp(200, {"ok": True})
        with patch.object(client.session, "request", side_effect=[limited, ok]):
            with patch("venice_sdk.client.time.sleep"):
                assert client.get("/x").json()["ok"] is True

    def test_429_invalid_retry_after_and_backoff(self, client):
        limited = _resp(429, {"error": "rate"}, headers={"Retry-After": "soon"})
        ok = _resp(200, {})
        client.config.retry_delay = 1
        client.config.retry_backoff_factor = 2
        with patch.object(client.session, "request", side_effect=[limited, ok]):
            with patch("venice_sdk.client.time.sleep") as sleep:
                client.get("/x")
                assert sleep.called

    def test_error_string_and_non_json(self, client):
        bad = _resp(400, None, text="nope")
        with patch.object(client.session, "request", return_value=bad):
            with pytest.raises(VeniceAPIError):
                client.get("/x")
        bad2 = _resp(400, {"error": "plain string"})
        with patch.object(client.session, "request", return_value=bad2):
            with pytest.raises(VeniceAPIError):
                client.get("/x")

    def test_429_exhausts_retries_records_metrics(self, client):
        limited = _resp(
            429,
            {"error": {"message": "rl"}},
            headers={"Retry-After": "1", "x-ratelimit-remaining": "2", "X-Request-ID": "rid"},
        )
        client.config.max_retries = 1
        with patch.object(client.session, "request", return_value=limited):
            with patch("venice_sdk.client.time.sleep"):
                with pytest.raises(RateLimitError):
                    client.post("/chat/completions", data={"a": 1})
        assert client.metrics is not None
        assert len(client.metrics.events) >= 1

    def test_stream_sse_paths(self, client):
        lines = [
            b"data: {\"chunk\": \"a\"}\n",
            b"data: {\"b\": 1}\n",
            b"data: [DONE]\n",
            b": comment\n",
            b"data: not-json\n",
            b"{\"legacy\": true}\n",
            b"\n",
        ]
        resp = _resp(200, {})
        resp.iter_lines.return_value = lines
        with patch.object(client.session, "request", return_value=resp):
            chunks = list(client.stream("/chat/completions", data={"m": 1}))
        assert any("chunk" in c or "b" in c or "legacy" in c for c in chunks)

    def test_wrappers_and_make_request(self, client):
        ok = _resp(200, {"ok": True})
        with patch.object(client.session, "request", return_value=ok):
            assert client.get("/a").json()["ok"]
            assert client.delete("/a").json()["ok"]
            assert client._make_request("POST", "/a", data={"x": 1}).json()["ok"]
            list(client._make_request("POST", "/a", data={"x": 1}, stream=True))

    def test_manager(self, cfg):
        mgr = HTTPClientManager()
        c1 = mgr.get_client(cfg)
        c2 = mgr.get_client(cfg)
        assert c1 is c2
        mgr.clear(cfg)
        c3 = mgr.get_client(cfg, force_refresh=True)
        assert c3 is not None
        mgr.set_builder(lambda c: HTTPClient(c, enable_metrics=False))
        c4 = mgr.get_client(cfg, force_refresh=True)
        assert c4.metrics is None
        get_http_client_manager()


class TestMetricsAndLogging:
    def test_metrics_full(self):
        m = RateLimitMetrics()
        m.record_rate_limit("/a", 429, retry_after=2, remaining_requests=1, method="POST")
        m.record_rate_limit("/a", 429, retry_after=None, method="GET")
        m.record_rate_limit("/b", 429, retry_after=1)
        assert m.get_usage_stats()["/a"] >= 1
        assert len(m.get_rate_limit_events()) >= 2
        assert len(m.get_rate_limit_events("/a")) >= 1
        assert m.get_endpoint_summary("/a")["total_events"] >= 1
        assert m.get_endpoint_summary("/missing") is None
        summary = m.get_rate_limit_summary()
        assert "total_events" in summary
        m.clear()
        assert m.events == []

    def test_structured_formatter_and_setup_logging(self):
        fmt = StructuredFormatter(datefmt="%Y-%m-%d")
        record = logging.LogRecord("venice_sdk", logging.INFO, __file__, 1, "hi", (), None)
        assert '"message": "hi"' in fmt.format(record)
        try:
            raise RuntimeError("x")
        except RuntimeError:
            record.exc_info = sys_exc_info()
        # without exc via formatException path
        record2 = logging.LogRecord("venice_sdk", logging.ERROR, __file__, 1, "err", (), None)
        try:
            raise ValueError("boom")
        except ValueError:
            import sys
            record2.exc_info = sys.exc_info()
        assert "exc_info" in fmt.format(record2)

        logger = setup_logging(level=logging.DEBUG, structured=True, stream=io.StringIO(), force=True)
        logger.info("structured")
        logger = setup_logging(level=logging.WARNING, structured=False, stream=io.StringIO(), force=True)
        logger.warning("plain")
        # existing handlers path
        setup_logging(level=logging.ERROR, force=False)


def sys_exc_info():
    import sys
    return sys.exc_info()


class TestHttpHelpers:
    def test_shared_http_client_helpers(self, cfg):
        _http.reset_shared_http_client()
        with patch("venice_sdk._http._http_client_manager.get_client", return_value=HTTPClient(cfg)):
            c = _http.get_shared_http_client()
            assert c is not None
        custom = HTTPClient(cfg)
        _http.set_shared_http_client(custom)
        assert _http.get_shared_http_client() is custom
        assert _http.ensure_http_client(custom) is custom
        assert _http.ensure_http_client(None) is custom
        factory_client = HTTPClient(cfg, enable_metrics=False)

        def factory():
            return factory_client

        assert _http.get_shared_http_client(factory=factory) is factory_client
        assert _http.get_shared_http_client(factory=factory) is factory_client
        _http.reset_shared_http_client()
        with patch("venice_sdk._http.VeniceClient", create=True):
            pass
        # default factory path via manager builder
        with patch("venice_sdk.venice_client.VeniceClient") as VC:
            vc = MagicMock()
            vc.http_client = HTTPClient(cfg)
            VC.return_value = vc
            built = _http._default_http_client_factory(cfg)
            assert built is vc.http_client
        with patch("venice_sdk.venice_client.VeniceClient") as VC:
            VC.return_value = HTTPClient(cfg)
            assert isinstance(_http._default_http_client_factory(cfg), HTTPClient)
        with patch("venice_sdk.venice_client.VeniceClient") as VC:
            VC.return_value = MagicMock(http_client="mock")
            assert _http._default_http_client_factory(cfg) is not None
        _http.reset_shared_http_client()
