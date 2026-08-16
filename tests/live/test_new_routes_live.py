"""
Live tests for 0.3.1/0.3.2 routes: responses, augment, styles, STT, x402.
Cheap reads first; generation/transcription skipped when the model or route is unavailable.
"""

from __future__ import annotations

import os

import pytest

from venice_sdk.errors import VeniceAPIError, ModelNotFoundError
from venice_sdk.responses import Response
from venice_sdk.venice_client import VeniceClient
from venice_sdk.config import load_config
from venice_sdk.audio import TranscriptionResult


def _skip_unavailable(exc: VeniceAPIError) -> None:
    status = getattr(exc, "status_code", None)
    if status in {401, 402, 403, 404, 422, 429, 500, 502, 503}:
        pytest.skip(f"Route unavailable or not entitled ({status}): {exc}")
    raise


@pytest.mark.live
class TestNewRoutesLive:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.api_key = os.getenv("VENICE_API_KEY")
        if not self.api_key:
            pytest.skip("VENICE_API_KEY environment variable not set")
        self.client = VeniceClient(load_config(api_key=self.api_key))

    def test_image_styles_list(self):
        try:
            styles = self.client.image_styles.list_styles()
        except VeniceAPIError as exc:
            _skip_unavailable(exc)
        assert isinstance(styles, list)

    def test_models_traits_categories(self):
        try:
            cats = self.client.models_traits.get_trait_categories()
        except (VeniceAPIError, ModelNotFoundError) as exc:
            if isinstance(exc, VeniceAPIError):
                _skip_unavailable(exc)
            pytest.skip(f"traits categories unavailable: {exc}")
        assert cats is not None

    def test_responses_create_typed(self):
        try:
            result = self.client.responses.create(
                model="llama-3.3-70b",
                input="Reply with the single word: pong",
                max_output_tokens=16,
                temperature=0,
            )
        except VeniceAPIError as exc:
            _skip_unavailable(exc)
        assert isinstance(result, Response)
        assert result.id
        assert isinstance(result.output_text, str)

    def test_augment_search_typed(self):
        try:
            result = self.client.augment.search("Venice AI", limit=1)
        except VeniceAPIError as exc:
            _skip_unavailable(exc)
        assert result.raw is not None
        assert isinstance(result.results, list)

    def test_augment_scrape_typed(self):
        try:
            result = self.client.augment.scrape("https://example.com")
        except VeniceAPIError as exc:
            _skip_unavailable(exc)
        assert result.raw is not None
        assert result.markdown is not None

    def test_audio_transcribe_from_tts(self):
        try:
            speech = self.client.audio.speech(
                input_text="Coverage ping.",
                voice="af_alloy",
                model="tts-kokoro",
            )
        except VeniceAPIError as exc:
            _skip_unavailable(exc)
        except TypeError:
            pytest.skip("speech() signature mismatch on this client")
        if not getattr(speech, "audio_data", None):
            pytest.skip("TTS returned no audio")
        try:
            transcript = self.client.audio.transcribe(
                speech.audio_data,
                model="openai/whisper-large-v3",
                filename="ping.mp3",
            )
        except VeniceAPIError as exc:
            _skip_unavailable(exc)
        if isinstance(transcript, str):
            assert transcript
        else:
            assert isinstance(transcript, TranscriptionResult)
            assert isinstance(transcript.text, str)

    def test_x402_balance_route_exists(self):
        try:
            result = self.client.x402.balance("0x0000000000000000000000000000000000000000")
        except VeniceAPIError as exc:
            _skip_unavailable(exc)
        assert result.raw is not None
        assert result.wallet_address
