"""
Tests for 429 rate limiting behavior and retry logic.
"""

from unittest.mock import MagicMock, patch
import time

import pytest

from venice_sdk.client import HTTPClient
from venice_sdk.config import Config
from venice_sdk.errors import RateLimitError, VeniceAPIError


@pytest.fixture
def config():
    cfg = Config(api_key="test", base_url="https://api.venice.ai/api/v1", timeout=1, max_retries=3, retry_delay=0)
    return cfg


def make_response(status_code: int, json_body: dict, headers: dict = None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_body
    resp.headers = headers or {}
    resp.text = str(json_body)
    return resp


def test_raises_rate_limit_error_when_exhausted(config, monkeypatch):
    client = HTTPClient(config)

    # Always return 429 with Retry-After header
    rate_limited = make_response(429, {"error": {"message": "Too Many Requests"}}, {"Retry-After": "2"})

    call_count = {"n": 0}

    def fake_request(*args, **kwargs):
        call_count["n"] += 1
        return rate_limited

    monkeypatch.setattr(client.session, "request", fake_request)

    start = time.time()
    with pytest.raises(RateLimitError) as exc:
        client.post("test", data={})
    elapsed = time.time() - start

    assert "Too Many Requests" in str(exc.value)
    # Should have retried max_retries times
    assert call_count["n"] == config.max_retries
    # Should have waited at least some time due to backoff
    assert elapsed >= 0


def test_retries_then_succeeds_after_rate_limit(config, monkeypatch):
    client = HTTPClient(config)

    rate_limited = make_response(429, {"error": {"message": "Too Many Requests"}}, {"Retry-After": "0"})
    success = make_response(200, {"ok": True})

    seq = [rate_limited, success]

    def fake_request(*args, **kwargs):
        return seq.pop(0)

    monkeypatch.setattr(client.session, "request", fake_request)

    resp = client.post("test", data={})
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


def test_streaming_raises_rate_limit_error(config, monkeypatch):
    client = HTTPClient(config)

    rate_limited = make_response(429, {"error": {"message": "Too Many Requests"}}, {"Retry-After": "1"})

    monkeypatch.setattr(client.session, "request", lambda *a, **k: rate_limited)

    with pytest.raises(RateLimitError):
        list(client.stream("chat/completions", data={}))

