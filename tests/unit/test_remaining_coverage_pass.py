"""Focused regression tests for branches not exercised by the main suites."""

import base64
import json
from datetime import datetime
from pathlib import Path, PosixPath
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from venice_sdk import cli
from venice_sdk.account import APIKeysAPI, AccountManager, BillingAPI, RateLimits, UsageInfo
from venice_sdk.characters import Character, CharactersAPI
from venice_sdk.chat import ChatAPI
from venice_sdk.client import HTTPClient
from venice_sdk.config import Config, _get_global_config_path, load_config
from venice_sdk.errors import APIKeyError, RateLimitError, VeniceAPIError, handle_api_error
from venice_sdk.images import (
    ImageAPI, ImageEditAPI, ImageEditResult, ImageGenerationError, ImageStylesAPI,
    ImageUpscaleAPI, ImageUpscaleResult, edit_image, generate_image, upscale_image,
)
from venice_sdk.metrics import RateLimitMetrics
from venice_sdk.models import _build_model_from_data
from venice_sdk.models_advanced import (
    ModelRecommendationEngine, ModelTraits, ModelsCompatibilityAPI, ModelsTraitsAPI,
    _to_temperature_range,
)
from venice_sdk.video import VideoAPI, VideoGenerationError, VideoJob
import venice_sdk.config as sdk_config


def response(payload=None, *, status=200, headers=None, content=b"", text=""):
    result = MagicMock()
    result.status_code = status
    result.headers = headers or {}
    result.content = content
    result.text = text
    result.json.return_value = payload if payload is not None else {}
    return result


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"prompt": ""}, "Prompt cannot be empty"),
        ({"prompt": "x", "n": 0}, "n must be between"),
        ({"prompt": "x", "size": "bad"}, "Invalid size"),
        ({"prompt": "x", "quality": "bad"}, "Invalid quality"),
        ({"prompt": "x", "response_format": "bad"}, "Invalid response_format"),
    ],
)
def test_image_generate_validation_branches(kwargs, message):
    with pytest.raises(ValueError, match=message):
        ImageAPI(MagicMock()).generate(**kwargs)


@pytest.mark.parametrize("result_class", [ImageEditResult, ImageUpscaleResult])
def test_image_result_data_url_save(result_class, tmp_path):
    destination = tmp_path / "image.bin"
    saved = result_class(url="data:image/png;base64," + base64.b64encode(b"pixels").decode()).save(destination)
    assert saved.read_bytes() == b"pixels"


def test_image_edit_helpers_and_convenience_list_unwrap(tmp_path):
    client = MagicMock()
    binary = response(headers={"Content-Type": "image/png"}, content=b"edited")
    client.post.return_value = binary
    api = ImageEditAPI(client)
    assert api.multi_edit([b"a", "https://example.test/b.png"], "edit").b64_json
    assert api.remove_background(image_url="https://example.test/image.png").b64_json
    with pytest.raises(ValueError, match="1 to 3"):
        api.multi_edit([], "edit")
    with pytest.raises(ValueError, match="either"):
        api.remove_background()
    with pytest.raises(ValueError, match="only one"):
        api.remove_background(b"a", "https://example.test/a.png")
    # A JSON/non-image reply exercises the endpoint's defensive fallback.
    client.post.return_value = response({"error": "rejected"}, headers={"Content-Type": "application/json"})
    with pytest.raises(ImageGenerationError, match="non-image"):
        api.multi_edit([b"a"], "edit")

    generated, edited, upscaled = object(), object(), object()
    with patch("venice_sdk.images.ImageAPI.generate", return_value=[generated]):
        assert generate_image("x", client=client) is generated
    with patch("venice_sdk.images.ImageEditAPI.edit", return_value=[edited]):
        assert edit_image(b"x", "edit", client=client) is edited
    with patch("venice_sdk.images.ImageUpscaleAPI.upscale", return_value=upscaled):
        assert upscale_image(b"x", client=client) is upscaled


def test_image_upscale_url_encode_and_style_string_format():
    client = MagicMock()
    with patch("venice_sdk.images.requests.get", return_value=response(content=b"source")):
        assert ImageUpscaleAPI(client)._encode_image("https://example.test/i.png") == base64.b64encode(b"source").decode()
    with pytest.raises(ValueError):
        ImageUpscaleAPI(client)._encode_image(1)
    client.get.return_value = response({"data": ["Oil Paint"]})
    style = ImageStylesAPI(client).list_styles()[0]
    assert (style.id, style.description) == ("oil_paint", "Image style: Oil Paint")


def test_streaming_response_error_metrics_and_legacy_lines():
    cfg = Config("key", max_retries=1)
    client = HTTPClient(cfg)
    client.metrics = MagicMock()
    failing = response({"error": "slow down"}, status=429,
                       headers={"Retry-After": "3", "X-RateLimit-Remaining": "bad"})
    failing.url = "https://api.test/stream"
    with pytest.raises(RateLimitError) as raised:
        list(client._handle_streaming_response(failing))
    assert raised.value.context["stream"] is True
    client.metrics.record_rate_limit.assert_called_once()

    stream = response(status=200)
    stream.iter_lines.return_value = [b"", b'{"chunk":{"a":1}}', b'{"plain":2}', b"not-json", b"data: [DONE]"]
    assert list(client._handle_streaming_response(stream)) == [{"a": 1}, {"plain": 2}]


def test_streaming_response_non_json_error_payload():
    client = HTTPClient(Config("key"))
    bad = response(status=500, text="gateway")
    bad.json.side_effect = ValueError("bad json")
    with pytest.raises(VeniceAPIError, match="gateway"):
        list(client._handle_streaming_response(bad))


def test_account_key_edge_cases_and_manager_proxies():
    client = MagicMock()
    api = APIKeysAPI(client)
    client.get.return_value = response({"nope": True})
    assert api.get("missing") is None
    client.get.side_effect = VeniceAPIError("not found")
    assert api.get("missing") is None
    client.get.side_effect = None
    client.post.return_value = response({"data": {}})
    with pytest.raises(APIKeyError, match="parse"):
        api.create("name")
    client.delete.return_value = response({"success": True})
    assert api.delete("id") is True
    with pytest.raises(APIKeyError, match="not supported"):
        api.update("id")

    keys, billing = MagicMock(), MagicMock()
    manager = AccountManager(keys, billing)
    keys.get_rate_limits.side_effect = APIKeyError("nope")
    keys.list.side_effect = APIKeyError("nope")
    billing.get_usage.side_effect = VeniceAPIError("nope")
    assert manager.get_account_summary()["status"] == "basic_access"
    assert manager.check_rate_limit_status()["status"] == "unknown"
    billing.get_usage.side_effect = None
    assert manager.get_rate_limit_logs(limit=2) == keys.get_rate_limits_log.return_value
    assert manager.get_usage_info() == billing.get_usage.return_value
    assert manager.get_model_usage() == billing.get_usage_by_model.return_value
    assert manager.get_billing_summary() == billing.get_billing_summary.return_value


def test_account_billing_dict_usage_and_datetime_fallbacks():
    client = MagicMock()
    client.get.return_value = response({"data": {"total_usage": "2", "usage_by_model": {"a": {"requests": "1", "tokens": "2", "cost": "3"}}}})
    usage = BillingAPI(client).get_usage()
    assert usage.total_usage == 2 and usage.usage_by_model["a"]["tokens"] == 2
    assert APIKeysAPI(client)._parse_datetime("bad") is None
    assert BillingAPI(client)._parse_datetime("2024-01-01 01:02:03").year == 2024


def test_cli_commands_fallbacks_and_paths(monkeypatch, tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem():
        monkeypatch.delenv("VENICE_API_KEY", raising=False)
        monkeypatch.delenv("VENICE_BASE_URL", raising=False)
        assert runner.invoke(cli.cli, ["status"]).exit_code == 0
        assert "No API key" in runner.invoke(cli.cli, ["status"]).output
        assert "No configuration option" in runner.invoke(cli.cli, ["configure"]).output
        configured = runner.invoke(cli.cli, ["configure", "--base-url", "http://example.test"])
        assert configured.exit_code == 0 and "insecure" in configured.output
        authenticated = runner.invoke(cli.cli, ["auth", "abcdefghijk"])
        assert authenticated.exit_code == 0
        assert "Local (.env)" in runner.invoke(cli.cli, ["config"]).output
        assert cli.get_api_key() == "abcdefghijk"
        assert cli.get_base_url() == "http://example.test"
    env = tmp_path / ".env"
    git = tmp_path / ".git"
    git.mkdir()
    cli.warn_about_secrets(env)
    with pytest.MonkeyPatch.context() as local:
        local.setattr(cli, "Path", PosixPath)
        local.setattr(cli.os, "name", "nt")
        local.setenv("APPDATA", str(tmp_path / "appdata"))
        assert "venice" in str(cli.get_global_config_path())


def test_config_global_platform_and_load_paths(monkeypatch, tmp_path):
    with pytest.MonkeyPatch.context() as local:
        local.setattr(sdk_config, "Path", PosixPath)
        local.setattr(sdk_config.os, "name", "nt")
        local.setenv("APPDATA", str(tmp_path))
        assert _get_global_config_path() == tmp_path / "venice" / ".env"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    assert _get_global_config_path() == tmp_path / "xdg" / "venice" / ".env"
    assert Config("a") != "a"
    with pytest.MonkeyPatch.context() as local:
        local.chdir(tmp_path)
        local.delenv("VENICE_API_KEY", raising=False)
        (tmp_path / ".env").write_text("VENICE_API_KEY=from-file\n")
        assert load_config().api_key == "from-file"


def test_error_payload_context_and_default_message():
    with pytest.raises(VeniceAPIError) as raised:
        handle_api_error(400, {"details": {"field": ["invalid"]}, "error": {"message": " "}, "retry_after": "bad"})
    assert raised.value.context["details"]["field"] == ["invalid"]
    with pytest.raises(VeniceAPIError, match="Request failed with status 400"):
        handle_api_error(400, {"error": {"message": " "}})
    with pytest.raises(VeniceAPIError):
        handle_api_error(400, ["bad"])


def test_metrics_empty_endpoint_and_export():
    metrics = RateLimitMetrics()
    assert metrics.get_rate_limit_summary()["total_events"] == 0
    assert metrics.get_endpoint_summary("missing") is None
    metrics.record_rate_limit("a", 429, retry_after=None, method="GET")
    assert metrics.get_endpoint_summary("a")["average_retry_after"] is None
    assert json.loads(metrics.export_events("json"))[0]["endpoint"] == "a"


def test_models_defensive_payload_branches():
    with pytest.raises(VeniceAPIError):
        _build_model_from_data([])
    with pytest.raises(VeniceAPIError):
        _build_model_from_data({"id": "x"})
    model = _build_model_from_data({"id": "x", "type": "text", "model_spec": {"availableContextTokens": "bad"}})
    assert model.capabilities.available_context_tokens == 0


def test_models_advanced_remaining_branches():
    assert _to_temperature_range(["bad", 1]) is None
    traits_client = MagicMock()
    traits_client.get.return_value = response({"data": [{"id": "m", "model_spec": {"traits": [1, {"fast": True}]}}]})
    traits = ModelsTraitsAPI(traits_client)
    assert traits.get_traits()["m"].traits["1"] == 1
    assert traits.get_best_models_for_task("unmapped task") == []
    assert traits._parse_model_traits("m", {"temperature_range": [0, 1]}).temperature_range == (0.0, 1.0)
    compatibility = ModelsCompatibilityAPI(MagicMock())
    with patch.object(compatibility, "get_mapping", side_effect=RuntimeError()):
        assert "openai" in compatibility.get_available_providers()
    engine = ModelRecommendationEngine(MagicMock(), MagicMock())
    engine.traits_api.get_best_models_for_task.return_value = []
    assert engine.recommend_models("task") == []
    trait = ModelTraits("m", {"cap": "yes"}, {"cost_level": "low", "speed": "high", "quality": "high"})
    engine.traits_api.get_best_models_for_task.return_value = ["m"]
    assert engine._calculate_recommendation_score(trait, "task", {"cap": "yes"}, "low", "balanced") > 10


def test_chat_stream_helpers_cover_optional_and_empty_choices():
    client = MagicMock()
    client.stream.return_value = [
        {"object": "chat.completion.chunk", "id": "x"},
        {"object": "other"},
    ]
    api = ChatAPI(client)
    output = list(api.complete_stream([{"role": "user", "content": "hi"}], tools=[{"type": "function"}], venice_parameters={"a": 1}))
    assert output[-1] == "data: [DONE]\n\n"
    assert list(api._stream_text_chunks(iter([{}, {"choices": [{"delta": {"content": "yes"}}]}]))) == ["yes"]


def test_video_job_and_wait_error_branches(tmp_path):
    with pytest.raises(VideoGenerationError):
        VideoJob("x", "queued").download(tmp_path / "out.mp4")
    completed = VideoJob("x", "completed", video_file_path=tmp_path / "missing.mp4")
    with pytest.raises(VideoGenerationError, match="not found"):
        completed.download(tmp_path / "out.mp4")
    with pytest.raises(VideoGenerationError):
        completed.get_video_data()

    api = VideoAPI(MagicMock())
    assert api._normalize_duration(None) is None and api._normalize_duration(5) == "5s"
    with pytest.raises(VideoGenerationError, match="not found"):
        api._encode_image(tmp_path / "none.png")
    with pytest.raises(VideoGenerationError, match="required"):
        api.wait_for_completion("job")
    api.retrieve = MagicMock(return_value=VideoJob("job", "failed", error="broken"))
    with pytest.raises(VideoGenerationError, match="broken"):
        api.wait_for_completion("job", model="m", poll_interval=0)


def test_video_retrieve_json_error_and_callback_exception():
    client = MagicMock()
    bad = response(headers={"Content-Type": "application/json"}, content=b"small")
    bad.json.side_effect = ValueError("invalid")
    client.post.return_value = bad
    with pytest.raises(VideoGenerationError, match="parse"):
        VideoAPI(client).retrieve("job", model="m")
    api = VideoAPI(client)
    api.retrieve = MagicMock(return_value=VideoJob("job", "completed"))
    assert api.wait_for_completion("job", model="m", callback=lambda _: (_ for _ in ()).throw(RuntimeError())) .is_completed()


def test_characters_list_capabilities_and_empty_get():
    assert Character("id", "name", "slug", "description", "prompt", capabilities=["vision"]).has_capability("vision")
    client = MagicMock()
    client.get.return_value = response({"data": []})
    assert CharactersAPI(client).get("missing") is None
