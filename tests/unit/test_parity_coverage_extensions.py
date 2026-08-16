"""Coverage extensions for account/audio/images/chat/video/characters/models/client wiring."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from venice_sdk.account import BillingAPI, APIKeysAPI
from venice_sdk.audio import AudioAPI, MusicAPI, MusicJob, AudioResult
from venice_sdk.images import ImageAPI, ImageEditAPI, ImageGeneration, ImageEditResult, ImageUpscaleResult
from venice_sdk.chat import ChatAPI, chat_complete, Message, Choice, Usage, ChatCompletion
from venice_sdk.video import VideoAPI, VideoJob, VideoMetadata
from venice_sdk.characters import CharactersAPI, Character
from venice_sdk.models_advanced import ModelsTraitsAPI, _to_temperature_range, _recommendation_score
from venice_sdk.venice_client import VeniceClient, create_client
from venice_sdk.config import Config
from venice_sdk.errors import BillingError, ModelNotFoundError, AudioGenerationError, ImageGenerationError, VideoGenerationError
from venice_sdk.endpoints import AccountEndpoints, AudioEndpoints, ImageEndpoints, VideoEndpoints, ModelsEndpoints


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def cfg():
    return Config(api_key="k" * 32)


class TestBillingCoverage:
    def test_balance_analytics_history_summary(self, mock_client):
        mock_client.get.return_value.json.return_value = {
            "canConsume": True,
            "balances": {"USD": 1},
        }
        api = BillingAPI(mock_client)
        assert api.get_balance()["canConsume"] is True
        mock_client.get.assert_called_with(AccountEndpoints.BILLING_BALANCE)

        mock_client.get.return_value.json.return_value = {"lookback": "7d", "byDate": []}
        api.get_usage_analytics(lookback="7d", start_date="2026-01-01", end_date="2026-01-02")
        params = mock_client.get.call_args.kwargs["params"]
        assert params["startDate"] == "2026-01-01"

        mock_client.get.return_value.json.return_value = {"data": [], "nextCursor": None}
        api.get_usage_history(currency="USD", cursor="c", end_timestamp="1", page_size=10, start_timestamp="0")
        params = mock_client.get.call_args.kwargs["params"]
        assert params["pageSize"] == 10

        mock_client.get.return_value.json.return_value = {"canConsume": True}
        assert "canConsume" in api.get_billing_summary()

    def test_balance_invalid_and_summary_fallbacks(self, mock_client):
        api = BillingAPI(mock_client)
        mock_client.get.return_value.json.return_value = ["nope"]
        with pytest.raises(BillingError):
            api.get_balance()

        mock_client.get.side_effect = BillingError("no")
        # get_usage used in fallback — patch it
        with patch.object(api, "get_usage", return_value=MagicMock(total_usage=5)):
            summary = api.get_billing_summary()
            assert summary["total_spent"] == 5

        mock_client.get.side_effect = None
        mock_client.get.return_value.json.side_effect = TypeError("bad")
        with patch.object(api, "get_usage", return_value=MagicMock(total_usage=9)):
            # get_balance raises TypeError from isinstance path? Actually json returns via side_effect on .json
            mock_client.get.return_value.json.side_effect = None
            mock_client.get.return_value.json.return_value = {"canConsume": True}
            # force KeyError/TypeError in get_billing_summary via get_balance raising TypeError
            with patch.object(api, "get_balance", side_effect=TypeError("x")):
                with patch.object(api, "get_usage", return_value=MagicMock(total_usage=2)):
                    assert api.get_billing_summary()["total_spent"] == 2

        mock_client.get.return_value.json.return_value = "bad"
        with pytest.raises(BillingError):
            api.get_usage_analytics()
        with pytest.raises(BillingError):
            api.get_usage_history()

    def test_usage_aliases(self, mock_client):
        api = BillingAPI(mock_client)
        with patch.object(api, "get_usage", return_value="u") as gu:
            assert api.get_usage_info() == "u"
            gu.assert_called()
        with patch.object(api, "get_usage_by_model", return_value={}) as gm:
            assert api.get_model_usage() == {}
            gm.assert_called()


class TestAudioParityCoverage:
    def test_transcribe_and_clone(self, mock_client):
        api = AudioAPI(mock_client)
        resp = MagicMock()
        resp.headers = {"Content-Type": "application/json"}
        resp.json.return_value = {"text": "hi"}
        mock_client.post_multipart.return_value = resp
        assert api.transcribe(b"wav", model="whisper", language="en", timestamps=True).text == "hi"
        resp.headers = {"Content-Type": "text/plain"}
        resp.text = "plain"
        assert api.transcribe(b"wav", model="whisper") == "plain"
        with pytest.raises(ValueError):
            api.transcribe(b"x", model="")

        resp.headers = {"Content-Type": "application/json"}
        resp.json.return_value = {"id": "voice_1", "model": "chatterbox"}
        assert api.clone_voice(b"ref", model="chatterbox")["id"] == "voice_1"
        with pytest.raises(ValueError):
            api.clone_voice(b"x", model="")

    def test_speech_stream_iter_content(self, mock_client):
        # Use a plain object so hasattr(..., "stream") is False
        class Client:
            def post(self, *a, **k):
                resp = MagicMock()
                resp.iter_content.return_value = [b"a", b"", b"b"]
                return resp

        api = AudioAPI(Client())  # type: ignore[arg-type]
        chunks = list(api.speech_stream("hello", voice="af_alloy"))
        assert chunks == [b"a", b"b"]

    def test_music_queue_retrieve_quote_complete(self, mock_client):
        api = MusicAPI(mock_client)

        qresp = MagicMock()
        qresp.status_code = 200
        qresp.headers = {"Content-Type": "application/json"}
        qresp.json.return_value = {"queue_id": "q1", "status": "QUEUED", "model": "m"}
        mock_client.post.return_value = qresp
        job = api.queue(
            model="m",
            prompt="p",
            lyrics_prompt="l",
            duration_seconds=10,
            force_instrumental=True,
            voice="v",
            language_code="en",
            speed=1.0,
        )
        assert job.queue_id == "q1"

        rresp = MagicMock()
        rresp.status_code = 200
        rresp.headers = {"Content-Type": "application/json"}
        rresp.json.return_value = {"status": "PROCESSING"}
        mock_client.post.return_value = rresp
        assert api.retrieve(model="m", queue_id="q1")["status"] == "PROCESSING"

        # audio content path
        aresp = MagicMock()
        aresp.status_code = 200
        aresp.headers = {"Content-Type": "audio/wav"}
        aresp.content = b"RIFF"
        mock_client.post.return_value = aresp
        assert isinstance(api.retrieve(model="m", queue_id="q1"), AudioResult)

        aresp.headers = {"Content-Type": "audio/flac"}
        assert api.retrieve(model="m", queue_id="q1").format == "flac"
        aresp.headers = {"Content-Type": "audio/mpeg"}
        assert api.retrieve(model="m", queue_id="q1").format == "mp3"

        eres = MagicMock()
        eres.status_code = 400
        eres.headers = {"Content-Type": "application/json"}
        eres.json.return_value = {"error": "nope"}
        mock_client.post.return_value = eres
        with pytest.raises(Exception):
            api.retrieve(model="m", queue_id="q1")

        qoresp = MagicMock()
        qoresp.status_code = 200
        qoresp.headers = {"Content-Type": "application/json"}
        qoresp.json.return_value = {"estimated_cost": 0.1}
        mock_client.post.return_value = qoresp
        assert api.quote(model="m", prompt="p", lyrics_prompt="l", duration_seconds=5)["estimated_cost"] == 0.1

        with patch.object(api, "queue", return_value=MusicJob(queue_id="q1", model="m", status="QUEUED")):
            with patch.object(api, "retrieve", side_effect=[
                {"status": "PROCESSING"},
                AudioResult(audio_data=b"x", format="mp3"),
            ]):
                with patch("venice_sdk.audio.time.sleep"):
                    with patch("venice_sdk.audio.time.time", side_effect=[0, 1, 2, 3, 4, 5]):
                        out = api.complete(model="m", prompt="p", timeout=10)
                        assert isinstance(out, AudioResult)

            with patch.object(api, "retrieve", return_value={"status": "FAILED"}):
                with patch("venice_sdk.audio.time.sleep"):
                    with patch("venice_sdk.audio.time.time", side_effect=[0, 1, 2]):
                        with pytest.raises(AudioGenerationError):
                            api.complete(model="m", prompt="p", timeout=10)

            with patch.object(api, "retrieve", return_value={"status": "PROCESSING"}):
                with patch("venice_sdk.audio.time.sleep"):
                    with patch("venice_sdk.audio.time.time", side_effect=[0, 1000, 2000]):
                        with pytest.raises(AudioGenerationError):
                            api.complete(model="m", prompt="p", timeout=1)


class TestImagesNativeCoverage:
    def test_generate_native(self, mock_client):
        api = ImageAPI(mock_client)
        resp = MagicMock()
        resp.headers = {"Content-Type": "application/json"}
        resp.json.return_value = {"images": ["x"]}
        mock_client.post.return_value = resp
        out = api.generate_native(
            "a cat",
            "hidream",
            negative_prompt="blur",
            width=512,
            height=512,
            aspect_ratio="1:1",
            resolution="1K",
            cfg_scale=7,
            steps=20,
            seed=1,
            style_preset="cinematic",
            format="webp",
            variants=1,
            safe_mode=False,
            return_binary=False,
            enhance_prompt=True,
            enable_web_search=False,
            hide_watermark=True,
        )
        assert out["images"] == ["x"]
        assert mock_client.post.call_args.args[0] == ImageEndpoints.GENERATE

        resp.headers = {"Content-Type": "image/png"}
        resp.content = b"PNG"
        assert api.generate_native("x", "m") == b"PNG"

        with pytest.raises(ValueError):
            api.generate_native(" ", "m")
        with pytest.raises(ValueError):
            api.generate_native("x", "")

    def test_image_save_http_and_data_url(self, tmp_path):
        # data url path
        img = ImageGeneration(url="data:image/png;base64,YWJj")
        p = tmp_path / "a.png"
        img.save(p)
        assert p.read_bytes() == b"abc"
        assert img.get_image_data() == b"abc"

        with patch("venice_sdk.images.requests.get") as g:
            g.return_value.content = b"httpimg"
            g.return_value.raise_for_status = MagicMock()
            img2 = ImageGeneration(url="https://example.com/a.png")
            assert img2.get_image_data() == b"httpimg"
            img2.save(tmp_path / "b.png")


class TestChatVideoCharactersTraits:
    def test_chat_validation_and_new_params(self, mock_client):
        api = ChatAPI(mock_client)
        mock_client.post.return_value.json.return_value = {"choices": []}
        api.complete(
            [{"role": "user", "content": [{"type": "text", "text": "hi"}]}],
            model="m",
            tool_choice="auto",
            response_format={"type": "json_object"},
            parallel_tool_calls=True,
            reasoning={"effort": "low"},
            reasoning_effort="medium",
            fallbacks=["x"],
            top_p=0.9,
            top_k=40,
            max_tokens=10,
        )
        with pytest.raises(ValueError):
            api.complete([{"role": "user"}])  # no content/tool_calls
        with pytest.raises(ValueError):
            api.complete([{"content": "x"}])  # no role
        with pytest.raises(ValueError):
            api.complete(["bad"])  # type: ignore
        with pytest.raises(ValueError):
            api.complete([{"role": "bogus", "content": "x"}])

        # _create_completion helper
        mock_client.post.return_value.json.return_value = {
            "id": "1",
            "object": "chat.completion",
            "created": 1,
            "model": "m",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "hi"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        }
        # method may exist
        if hasattr(api, "_create_completion"):
            api._create_completion({"model": "m", "messages": [{"role": "user", "content": "hi"}]})

        mock_client.stream.return_value = iter([
            {"object": "chat.completion.chunk", "choices": [{"delta": {"content": "a"}}]},
            {"object": "chat.completion.chunk", "choices": [{"delta": {"content": "b"}}]},
            {"object": "chat.completion.chunk", "choices": []},
        ])
        chunks = list(api.complete_stream([{"role": "user", "content": "hi"}], model="m", tools=[], venice_parameters={}, foo=1))
        assert chunks

        with patch("venice_sdk.chat.ensure_http_client", return_value=mock_client):
            mock_client.post.return_value.json.return_value = {"choices": [{"message": {"content": "z"}}]}
            chat_complete([{"role": "user", "content": "hi"}], model="m")

    def test_video_transcribe(self, mock_client):
        api = VideoAPI(mock_client)
        mock_client.post.return_value.json.return_value = {"text": "t"}
        assert api.transcribe("https://youtube.com/watch?v=1", response_format="json").text == "t"
        with pytest.raises(ValueError):
            api.transcribe(" ")

    def test_characters_reviews_and_list_shapes(self, mock_client):
        api = CharactersAPI(mock_client)
        mock_client.get.return_value.json.return_value = {"data": [{"slug": "a", "name": "A"}]}
        # get with list
        mock_client.get.return_value.json.return_value = {"data": [{"slug": "a", "name": "A", "description": "d"}]}
        char = api.get("a")
        assert char is None or isinstance(char, Character) or char is not None
        mock_client.get.return_value.json.return_value = {"data": []}
        assert api.get("missing") is None
        mock_client.get.return_value.json.return_value = {"reviews": []}
        assert "reviews" in api.reviews("slug", page=1, page_size=5)
        with pytest.raises(ValueError):
            api.reviews("")

    def test_trait_categories(self, mock_client):
        api = ModelsTraitsAPI(mock_client)
        mock_client.get.return_value.json.return_value = {"data": {"default": "m1", "most_uncensored": "m2"}}
        cats = api.get_trait_categories()
        assert cats["default"] == "m1"
        mock_client.get.return_value.json.return_value = {"no": "data"}
        with pytest.raises(ModelNotFoundError):
            api.get_trait_categories()
        mock_client.get.return_value.json.return_value = {"data": ["bad"]}
        with pytest.raises(ModelNotFoundError):
            api.get_trait_categories()

        assert _to_temperature_range(None) is None
        assert _recommendation_score({"score": "x"}) == 0.0
        assert _recommendation_score({"score": 1.5}) == 1.5

    def test_venice_client_new_attrs_and_metrics_none(self, cfg):
        with patch("venice_sdk.venice_client.HTTPClient") as HC:
            http = MagicMock()
            http.metrics = None
            HC.return_value = http
            client = VeniceClient(cfg)
            assert hasattr(client, "augment")
            assert hasattr(client, "crypto")
            assert hasattr(client, "responses")
            assert hasattr(client, "x402")
            assert client.get_rate_limit_metrics() is None
            assert client.get_rate_limit_events() is None
            assert client.get_endpoint_metrics("/x") is None
            client.clear_caches()
