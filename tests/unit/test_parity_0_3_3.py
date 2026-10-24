"""0.3.3 parity: decisions, voice changer, models type filter, billing history, chat file parts."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from venice_sdk.account import BillingAPI, _billing_timestamp
from venice_sdk.audio import AudioResult
from venice_sdk.chat import ChatAPI
from venice_sdk.decisions import DecisionAnswer, DecisionResult, DecisionsAPI, _empty_state
from venice_sdk.endpoints import DecisionsEndpoints, VoiceChangerEndpoints, AccountEndpoints
from venice_sdk.errors import AudioGenerationError, VeniceAPIError
from venice_sdk.models import ModelsAPI, ModelCapabilities, _build_model_from_data
from venice_sdk.voice_changer import VoiceChangerAPI, VoiceChangerJob, _job_from_payload


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.config.timeout = 30
    return client


class TestDecisionsAPI:
    def test_create_parses_noul_choice_score(self, mock_client):
        mock_client.post.return_value.json.return_value = {
            "model": "jev-latest",
            "answers": {
                "is_urgent": {"type": "noul", "noul": 0.92},
                "bucket": {
                    "type": "choice",
                    "choice": "p0",
                    "probabilities": {"p0": 0.8, "p1": 0.2},
                    "confidence": 0.7,
                },
                "severity": {
                    "type": "score",
                    "score": 2.4,
                    "legend": {"1": "low", "3": "high"},
                    "probabilities": {"1": 0.2, "3": 0.8},
                    "confidence": 0.6,
                },
            },
            "usage": {"input_tokens": 10, "output_tokens": 2},
        }
        api = DecisionsAPI(mock_client)
        out = api.create(
            "Help!",
            {"is_urgent": {"type": "noul", "instructions": "urgent?"}},
            images=["data:image/png;base64,xx"],
            foo="bar",
        )
        assert out.model == "jev-latest"
        assert out.noul("is_urgent") == 0.92
        assert out.picked("bucket") == "p0"
        assert out.answers["severity"].score == 2.4
        assert out.usage["input_tokens"] == 10
        assert out.raw["model"] == "jev-latest"
        mock_client.post.assert_called_once()
        assert mock_client.post.call_args.args[0] == DecisionsEndpoints.DECISIONS
        body = mock_client.post.call_args.kwargs["data"]
        assert body["images"][0].startswith("data:image")
        assert body["foo"] == "bar"

    def test_systemone_alias_and_validation(self, mock_client):
        mock_client.post.return_value.json.return_value = {"model": "clef", "answers": {}}
        api = DecisionsAPI(mock_client)
        out = api.systemone({"ticket": 1}, {"q": {"type": "noul", "instructions": "x"}}, model="clef")
        assert isinstance(out, DecisionResult)
        assert mock_client.post.call_args.args[0] == DecisionsEndpoints.SYSTEMONE
        with pytest.raises(ValueError, match="model is required"):
            api.create("s", {"q": {"type": "noul"}}, model="")
        with pytest.raises(ValueError, match="questions"):
            api.create("s", {})
        with pytest.raises(ValueError, match="state"):
            api.create("  ", {"q": {"type": "noul"}})
        with pytest.raises(ValueError, match="state"):
            api.create([], {"q": {"type": "noul"}})

    def test_from_dict_shapes(self):
        weird = DecisionResult.from_dict("x")
        assert weird.model == ""
        assert weird.answers == {}
        answer = DecisionAnswer.from_dict("bare")
        assert answer.type == "unknown"
        empty = DecisionAnswer.from_dict({"type": "noul", "noul": "nope"})
        assert empty.noul is None
        assert _empty_state(None) is True
        assert _empty_state({"a": 1}) is False
        assert _empty_state(1) is False
        assert DecisionResult.from_dict({"answers": {"a": {"type": "noul", "noul": 1}}}).noul("missing") is None
        assert DecisionResult.from_dict({"answers": {"a": {"type": "choice", "choice": "x"}}}).picked("missing") is None


class TestVoiceChangerAPI:
    def test_quote_queue_url_and_file(self, mock_client):
        mock_client.post.return_value.json.return_value = {"quote": 0.35, "duration_seconds": 60}
        api = VoiceChangerAPI(mock_client)
        quoted = api.quote("elevenlabs-voice-changer", 60)
        assert quoted["quote"] == 0.35
        assert mock_client.post.call_args.args[0] == VoiceChangerEndpoints.QUOTE

        mock_client.post.return_value.json.return_value = {
            "queue_id": "q1",
            "model": "elevenlabs-voice-changer",
            "status": "QUEUED",
            "duration_seconds": 52,
        }
        job = api.queue("elevenlabs-voice-changer", audio_url="https://ex.com/a.mp3", voice="Aria", seed=1)
        assert job.queue_id == "q1"
        assert job.duration_seconds == 52
        assert mock_client.post.call_args.args[0] == VoiceChangerEndpoints.QUEUE

        resp = MagicMock()
        resp.json.return_value = {"queue_id": "q2", "status": "QUEUED"}
        mock_client.post_multipart.return_value = resp
        job2 = api.queue("elevenlabs-voice-changer", file=b"wav", filename="a.wav", remove_background_noise=True)
        assert job2.queue_id == "q2"

    def test_queue_validation_and_job_parse(self, mock_client):
        api = VoiceChangerAPI(mock_client)
        with pytest.raises(ValueError, match="model"):
            api.quote("", 10)
        with pytest.raises(ValueError, match="duration"):
            api.quote("m", 0)
        with pytest.raises(ValueError, match="exactly one"):
            api.queue("m")
        with pytest.raises(ValueError, match="exactly one"):
            api.queue("m", file=b"x", audio_url="https://x")
        with pytest.raises(ValueError, match="model"):
            api.queue("", audio_url="https://x")
        with pytest.raises(AudioGenerationError):
            _job_from_payload("nope", "m")
        with pytest.raises(AudioGenerationError, match="queue_id"):
            _job_from_payload({}, "m")

    def test_retrieve_audio_and_json_and_cleanup(self, mock_client):
        api = VoiceChangerAPI(mock_client)
        audio = MagicMock()
        audio.headers = {"Content-Type": "audio/wav"}
        audio.content = b"WAV"
        audio.status_code = 200
        mock_client.post.return_value = audio
        out = api.retrieve("m", "q")
        assert isinstance(out, AudioResult)
        assert out.format == "wav"

        flac = MagicMock()
        flac.headers = {"Content-Type": "audio/flac"}
        flac.content = b"FLAC"
        flac.status_code = 200
        mock_client.post.return_value = flac
        assert api.retrieve("m", "q").format == "flac"

        json_resp = MagicMock()
        json_resp.headers = {"Content-Type": "application/json"}
        json_resp.status_code = 200
        json_resp.json.return_value = {"status": "PROCESSING"}
        mock_client.post.return_value = json_resp
        assert api.retrieve("m", "q")["status"] == "PROCESSING"

        err = MagicMock()
        err.headers = {"Content-Type": "application/json"}
        err.status_code = 400
        err.json.return_value = {"error": "bad id"}
        mock_client.post.return_value = err
        with pytest.raises(AudioGenerationError, match="bad id"):
            api.retrieve("m", "q")

        mock_client.post.return_value.json.return_value = {"ok": True}
        assert api.cleanup("q", "m")["ok"] is True
        with pytest.raises(AudioGenerationError, match="queue_id"):
            api.cleanup("", "m")
        with pytest.raises(AudioGenerationError, match="model"):
            api.cleanup("q", "")
        with pytest.raises(ValueError):
            api.retrieve("", "q")
        with pytest.raises(ValueError):
            api.retrieve("m", "")

    def test_complete_wait_timeout_and_bad_status(self, mock_client):
        api = VoiceChangerAPI(mock_client)
        with patch.object(api, "queue", return_value=VoiceChangerJob("q", "m", "QUEUED")):
            with patch.object(api, "retrieve", return_value=AudioResult(b"x", "mp3")):
                with patch("venice_sdk.voice_changer.time.sleep"):
                    assert isinstance(api.complete("m", audio_url="https://x", timeout=None), AudioResult)

        with patch.object(api, "queue", return_value=VoiceChangerJob("q", "m", "QUEUED")):
            with patch.object(api, "retrieve", return_value={"status": "FAILED"}):
                with pytest.raises(AudioGenerationError, match="FAILED"):
                    api.complete("m", audio_url="https://x", timeout=5)

        with patch.object(api, "queue", return_value=VoiceChangerJob("q", "m", "QUEUED")):
            with patch.object(api, "retrieve", return_value={"status": "PROCESSING"}):
                with patch("venice_sdk.voice_changer.time.time", side_effect=[0, 0.5, 10]):
                    with patch("venice_sdk.voice_changer.time.sleep") as slept:
                        with pytest.raises(AudioGenerationError, match="timed out"):
                            api.complete("m", audio_url="https://x", timeout=1)
                        slept.assert_called()

    def test_get_valid_parameters(self, mock_client):
        api = VoiceChangerAPI(mock_client)

        def post_side_effect(endpoint, data=None, **kwargs):
            duration = (data or {}).get("duration_seconds")
            if duration in (30, 60):
                resp = MagicMock()
                resp.json.return_value = {"quote": 0.2, "duration_seconds": duration}
                return resp
            raise VeniceAPIError("nope", status_code=400)

        mock_client.post.side_effect = post_side_effect
        valid = api.get_valid_parameters("elevenlabs-voice-changer")
        assert 30 in valid["duration_seconds"]
        assert 60 in valid["duration_seconds"]
        assert {"duration_seconds": 30} in valid["combinations"]
        assert api._validate_with_quote("m", 999) is False


class TestModelsTypeAndCapabilities:
    def test_list_passes_type_query(self, mock_client):
        mock_client.get.return_value.json.return_value = {"data": [{"id": "jev-latest", "type": "decision"}]}
        api = ModelsAPI(mock_client)
        rows = api.list(type="decision")
        assert rows[0]["id"] == "jev-latest"
        mock_client.get.assert_called_once_with("models", params={"type": "decision"})

    def test_capabilities_from_spec(self):
        model = _build_model_from_data(
            {
                "id": "m1",
                "type": "text",
                "name": "M",
                "model_spec": {
                    "capabilities": {
                        "supportsFunctionCalling": True,
                        "supportsWebSearch": False,
                        "supportsVideoInput": True,
                        "supportsAudioInput": True,
                        "supportsReasoning": True,
                        "supportsE2EE": True,
                        "supportsXSearch": True,
                        "supportsMultipleImages": True,
                    },
                    "availableContextTokens": 8000,
                },
            }
        )
        caps = model.capabilities
        assert caps.supports_video_input is True
        assert caps.supports_audio_input is True
        assert caps.supports_reasoning is True
        assert caps.supports_e2ee is True
        assert caps.supports_x_search is True
        assert caps.supports_multiple_images is True
        legacy = ModelCapabilities(True, False, 4096)
        assert legacy.supports_video_input is False


class TestBillingTimestampAndHistoryCursor:
    def test_billing_timestamp_z_and_aware(self):
        naive = datetime(2026, 9, 16, 0, 0, 0)
        assert _billing_timestamp(naive) == "2026-09-16T00:00:00Z"
        already = datetime(2026, 9, 16, 0, 0, 0, tzinfo=timezone.utc)
        out = _billing_timestamp(already)
        assert "2026-09-16" in out
        zulu = datetime.fromisoformat("2026-09-16T00:00:00+00:00")
        assert _billing_timestamp(zulu)

        class _ZStamp:
            tzinfo = timezone.utc

            def isoformat(self):
                return "2026-09-16T00:00:00Z"

        class _zStamp:
            tzinfo = timezone.utc

            def isoformat(self):
                return "2026-09-16T00:00:00z"

        assert _billing_timestamp(_ZStamp()) == "2026-09-16T00:00:00Z"
        assert _billing_timestamp(_zStamp()) == "2026-09-16T00:00:00z"

    def test_get_usage_next_cursor(self, mock_client):
        mock_client.get.return_value.json.return_value = {
            "data": [{"sku": "x", "amount": -1, "units": 1}],
            "nextCursor": "abc",
        }
        api = BillingAPI(mock_client)
        usage = api.get_usage()
        assert usage.pagination["nextCursor"] == "abc"
        mock_client.get.assert_called_once()
        assert mock_client.get.call_args.args[0] == AccountEndpoints.BILLING_USAGE_HISTORY


class TestChatFilePart:
    def test_file_part_accepted(self, mock_client):
        mock_client.post.return_value.json.return_value = {"id": "c"}
        ChatAPI(mock_client).complete(
            [{"role": "user", "content": [{"type": "file", "file": {"filename": "a.pdf"}}]}],
            model="m",
        )
        sent = mock_client.post.call_args.kwargs["data"]["messages"][0]["content"][0]
        assert sent["type"] == "file"
        with pytest.raises(ValueError, match="unsupported type"):
            ChatAPI(mock_client).complete(
                [{"role": "user", "content": [{"type": "not-a-real-part"}]}],
                model="m",
            )


class TestVoiceChangerCleanupException:
    def test_cleanup_wraps_unexpected(self, mock_client):
        api = VoiceChangerAPI(mock_client)
        mock_client.post.side_effect = RuntimeError("boom")
        with pytest.raises(AudioGenerationError, match="Failed to complete"):
            api.cleanup("q", "m")
        mock_client.post.side_effect = VeniceAPIError("nope", status_code=400)
        with pytest.raises(VeniceAPIError):
            api.cleanup("q", "m")


class TestRetrieveErrorNonDict:
    def test_retrieve_non_dict_error(self, mock_client):
        api = VoiceChangerAPI(mock_client)
        err = MagicMock()
        err.headers = {"Content-Type": "application/json"}
        err.status_code = 500
        err.json.return_value = "oops"
        mock_client.post.return_value = err
        with pytest.raises(AudioGenerationError, match="Retrieve failed"):
            api.retrieve("m", "q")

        mock = MagicMock()
        mock.headers = {"Content-Type": "application/json"}
        mock.status_code = "not-an-int"
        mock.json.return_value = {"status": "QUEUED"}
        mock_client.post.return_value = mock
        assert api.retrieve("m", "q")["status"] == "QUEUED"
