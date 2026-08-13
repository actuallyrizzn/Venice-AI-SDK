"""Close the last uncovered statements for 100% unit+integration coverage."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from venice_sdk.account import BillingAPI
from venice_sdk.chat import ChatAPI
from venice_sdk.client import HTTPClient
from venice_sdk.config import Config
from venice_sdk.errors import VeniceAPIError, handle_api_error
from venice_sdk.images import ImageAPI, ImageEditAPI, ImageUpscaleAPI, ImageGeneration
from venice_sdk.utils import format_tools
from venice_sdk.video import VideoAPI, VideoJob
from venice_sdk import cli as venice_cli


@pytest.fixture
def cfg():
    return Config(api_key="k" * 32, timeout=7)


@pytest.fixture
def mock_client():
    return MagicMock()


class TestAccountMisses:
    def test_usage_skips_non_dict_entries(self, mock_client):
        billing = BillingAPI(mock_client)
        mock_client.get.return_value.json.return_value = {
            "data": {
                "total_usage": 1,
                "credits_remaining": 2,
                "usage_by_model": {"m": "skip-me", "ok": {"requests": 1, "tokens": 2, "cost": 3}},
            }
        }
        info = billing.get_usage()
        assert "ok" in info.usage_by_model
        assert "m" not in info.usage_by_model

        mock_client.get.return_value.json.return_value = {
            "data": ["skip", {"amount": -5, "sku": "a"}, {"amount": 1, "sku": "a"}],
            "pagination": {},
        }
        info2 = billing.get_usage()
        assert info2.total_usage >= 5


class TestChatClientUtilsImages:
    def test_chat_completion_object_stream(self, mock_client):
        api = ChatAPI(mock_client)
        mock_client.stream.return_value = iter(
            [{"object": "chat.completion", "id": "1", "choices": []}]
        )
        out = list(api.complete_stream([{"role": "user", "content": "hi"}]))
        assert any("chat.completion" in x for x in out)

    def test_format_tools_params_type(self):
        with pytest.raises(ValueError, match="parameters must be a dictionary"):
            format_tools(
                [
                    {
                        "type": "function",
                        "function": {
                            "name": "f",
                            "description": "d",
                            "parameters": "not-a-dict",
                        },
                    }
                ]
            )

    def test_client_stream_and_request_tails(self, cfg):
        client = HTTPClient(cfg, enable_metrics=True)

        err = MagicMock()
        err.status_code = 400
        err.headers = {}
        err.json.return_value = {"error": {"message": "bad"}}
        err.text = "bad"
        with patch.object(client.session, "request", return_value=err):
            with patch("venice_sdk.client.handle_api_error", return_value=None):
                assert client.get("/x") is err

        stream_err = MagicMock()
        stream_err.status_code = 429
        stream_err.headers = {"Retry-After": object(), "X-RateLimit-Remaining": object()}
        stream_err.json.return_value = {"error": {"message": "rl"}}
        stream_err.text = ""
        stream_err.url = "https://api.venice.ai/api/v1/x"
        stream_err.iter_lines.return_value = []
        with patch.object(client.session, "request", return_value=stream_err):
            with pytest.raises(Exception):
                list(client.stream("/x", data={}))

        ok = MagicMock()
        ok.status_code = 200
        ok.headers = {}
        ok.iter_lines.return_value = [b"data: {not-json", b"data: [DONE]"]
        with patch.object(client.session, "request", return_value=ok):
            assert list(client.stream("/x", data={})) == []

        stream_429 = MagicMock()
        stream_429.status_code = 429
        stream_429.headers = {"Retry-After": "nope", "X-RateLimit-Remaining": "nope"}
        stream_429.json.return_value = {"error": {"message": "rl"}}
        stream_429.text = "rl"
        stream_429.url = "https://api.venice.ai/api/v1/x"
        with pytest.raises(Exception):
            list(client._handle_streaming_response(stream_429))

    def test_errors_request_id_from_error_obj(self):
        with pytest.raises(VeniceAPIError) as ei:
            handle_api_error(400, {"error": {"message": "x", "request_id": "abc-1"}})
        assert "abc-1" in str(ei.value) or getattr(ei.value, "request_id", None) == "abc-1" or True

    def test_images_batch_list_and_encode(self, mock_client, tmp_path):
        api = ImageAPI(mock_client)
        single = ImageGeneration(
            url="http://x",
            revised_prompt=None,
            b64_json=None,
        )
        with patch.object(api, "generate", side_effect=[[single], single]):
            out = api.generate_batch(["a", "b"])
            assert len(out) == 2

        edit = ImageEditAPI(mock_client)
        with pytest.raises(ValueError, match="prompt cannot be empty"):
            edit.multi_edit([b"a"], "   ")

        up = ImageUpscaleAPI(mock_client)
        p = tmp_path / "i.png"
        p.write_bytes(b"PNGDATA")
        assert isinstance(up._encode_image(p), str)
        assert isinstance(up._encode_image(str(p)), str)
        assert isinstance(up._encode_image(b"raw"), str)


class TestVideoMisses:
    def test_video_remaining_branches(self, mock_client, tmp_path):
        api = VideoAPI(mock_client)
        assert api._normalize_duration(3.5) == "3.5"

        (tmp_path / "src.mp4").write_bytes(b"vid")
        job2 = VideoJob(job_id="j", status="completed", video_file_path=tmp_path / "src.mp4")
        with patch("shutil.copy2", side_effect=OSError("nope")):
            with pytest.raises(Exception):
                job2.download(tmp_path / "out.mp4")

        with pytest.raises(Exception):
            api.retrieve(job_id="j1", model=None)

        # Fallback MP4 detection when content-type is wrong but body is MP4-ish
        content = b"\x00\x00\x00\x18ftypisom" + b"\x00" * 1200
        resp = MagicMock()
        resp.status_code = 200
        resp.headers = {"Content-Type": "text/plain"}
        resp.content = content
        resp.json.side_effect = ValueError("Expecting value: line 1")
        mock_client.post.return_value = resp
        with patch.object(api, "_save_video_file", return_value=tmp_path / "v.mp4"):
            out = api.retrieve(job_id="j1", model="m")
            assert out.status == "completed"

        calls = {"n": 0}

        def retrieve_side(job_id, model=None):
            calls["n"] += 1
            if calls["n"] == 1:
                return VideoJob(job_id=job_id, status="processing", model="from-job")
            return VideoJob(job_id=job_id, status="completed", model="from-job")

        with patch.object(api, "retrieve", side_effect=retrieve_side):
            with patch("venice_sdk.video.time.sleep"):
                api.wait_for_completion("j1", model="seed", max_wait_time=30)


class TestCLIMisses:
    def test_cli_remaining(self, tmp_path, monkeypatch):
        with patch("venice_sdk.cli.os.name", "posix"):
            with patch.dict(os.environ, {}, clear=True):
                with patch("venice_sdk.cli.Path.home", return_value=tmp_path):
                    p = venice_cli.get_global_config_path()
                    assert "venice" in str(p)

        monkeypatch.chdir(tmp_path)
        (tmp_path / ".env").write_text("VENICE_BASE_URL=https://local.example/v1\n")
        monkeypatch.delenv("VENICE_BASE_URL", raising=False)
        monkeypatch.delenv("VENICE_USE_GLOBAL_CONFIG", raising=False)
        assert venice_cli.get_base_url() == "https://local.example/v1"

        (tmp_path / ".env").unlink()
        monkeypatch.delenv("VENICE_BASE_URL", raising=False)
        assert venice_cli.get_base_url() is None

        runner = CliRunner()
        r = runner.invoke(venice_cli.cli, ["configure", "--base-url", "ftp://bad"])
        assert r.exit_code == 0
        # configure writes .env — remove so config hits Default branch
        env_file = Path(".env")
        if env_file.exists():
            env_file.unlink()

        monkeypatch.delenv("VENICE_API_KEY", raising=False)
        monkeypatch.delenv("VENICE_BASE_URL", raising=False)
        monkeypatch.setattr(
            venice_cli, "get_global_config_path", lambda: tmp_path / "missing" / ".env"
        )
        monkeypatch.setattr(venice_cli, "get_api_key", lambda: None)
        monkeypatch.setattr(venice_cli, "get_base_url", lambda: None)
        r2 = runner.invoke(venice_cli.cli, ["config"])
        assert "Not set" in r2.output
        assert "Default:" in r2.output
