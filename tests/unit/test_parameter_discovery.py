"""Parameter discovery helpers for music (quote grind) and image (model_spec)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from venice_sdk.audio import MusicAPI
from venice_sdk.errors import VeniceAPIError, AudioGenerationError
from venice_sdk.images import ImageAPI, get_image_model_constraints


class TestMusicGetValidParameters:
    def test_discovers_duration_and_instrumental_grid(self):
        mock_client = MagicMock()

        def post_side_effect(endpoint, data=None, **kwargs):
            payload = data or {}
            duration = payload.get("duration_seconds")
            force = payload.get("force_instrumental")
            resp = MagicMock()
            if duration in (30, 60) and force in (True, False):
                resp.json.return_value = {"quote": 0.2}
                return resp
            if duration == 30 and "force_instrumental" not in payload:
                resp.json.return_value = {"quote": 0.2}
                return resp
            raise VeniceAPIError("invalid", status_code=400)

        mock_client.post.side_effect = post_side_effect
        api = MusicAPI(mock_client)
        valid = api.get_valid_parameters(model="elevenlabs-music", prompt="probe")

        assert 30 in valid["duration_seconds"]
        assert 60 in valid["duration_seconds"]
        assert True in valid["force_instrumental"]
        assert False in valid["force_instrumental"]
        assert {"duration_seconds": 30, "force_instrumental": True} in valid["combinations"]
        assert {"duration_seconds": 30} in valid["combinations"]
        assert api._validate_with_quote("m", "p", duration_seconds=999) is False

    def test_validate_with_quote_swallows_audio_error(self):
        mock_client = MagicMock()
        api = MusicAPI(mock_client)
        api.quote = MagicMock(side_effect=AudioGenerationError("nope"))  # type: ignore[method-assign]
        assert api._validate_with_quote("m", "p") is False


class TestImageModelConstraints:
    def test_reads_model_spec_aliases_and_nested(self):
        mock_client = MagicMock()
        mock_client.get.return_value.json.return_value = {
            "data": [
                {
                    "id": "img-1",
                    "type": "image",
                    "model_spec": {
                        "aspectRatios": ["1:1", "16:9"],
                        "capabilities": {"supportsInpaint": True},
                        "constraints": {
                            "resolutions": ["1k", "2k"],
                            "style_presets": ["cinematic"],
                        },
                        "supportedSizes": ["1024x1024"],
                    },
                }
            ]
        }
        api = ImageAPI(mock_client)
        out = api.get_model_constraints("img-1")
        assert out["model_id"] == "img-1"
        assert out["type"] == "image"
        assert out["aspect_ratio"] == ["1:1", "16:9"]
        assert out["resolution"] == ["1k", "2k"]
        assert out["style_preset"] == ["cinematic"]
        assert out["size"] == ["1024x1024"]
        assert out["capabilities"]["supportsInpaint"] is True

    def test_empty_spec_and_convenience(self):
        mock_client = MagicMock()
        mock_client.get.return_value.json.return_value = {
            "data": [{"id": "img-2", "type": "image", "model_spec": "bad"}]
        }
        api = ImageAPI(mock_client)
        out = api.get_model_constraints("img-2")
        assert out["aspect_ratio"] == []
        assert out["resolution"] == []

        with pytest.raises(ValueError):
            api.get_model_constraints("")

        mock_client.get.return_value.json.return_value = {
            "data": [{"id": "img-3", "type": "image", "model_spec": {"aspect_ratios": ["9:16"]}}]
        }
        wrapped = get_image_model_constraints("img-3", client=mock_client)
        assert wrapped["aspect_ratio"] == ["9:16"]

        mock_client.get.return_value.json.return_value = {
            "data": [
                {
                    "id": "img-4",
                    "type": "image",
                    "model_spec": {"resolutions": ("720p", "1080p")},
                }
            ]
        }
        assert ImageAPI(mock_client).get_model_constraints("img-4")["resolution"] == [
            "720p",
            "1080p",
        ]
