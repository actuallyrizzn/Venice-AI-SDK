"""
Venice AI SDK - Voice changer (speech-to-speech).

Async family matching music/video: quote / queue / retrieve / complete.
Queue accepts either a multipart ``file`` or a JSON ``audio_url``, not both.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Union

from .audio import AudioResult
from .augment import _build_file_multipart
from .client import HTTPClient
from .endpoints import VoiceChangerEndpoints
from .errors import AudioGenerationError, VeniceAPIError

logger = logging.getLogger(__name__)

JSONDict = Dict[str, Any]
AudioSource = Union[str, Path, BinaryIO, bytes]


@dataclass
class VoiceChangerJob:
    """Result of queuing a voice-changer conversion."""

    queue_id: str
    model: str
    status: str
    duration_seconds: Optional[float] = None


class VoiceChangerAPI:
    """Speech-to-speech conversion via ``/audio/voice-changer/*``."""

    def __init__(self, client: HTTPClient):
        self.client = client

    def quote(
        self,
        model: str,
        duration_seconds: Union[int, str],
        **kwargs: Any,
    ) -> JSONDict:
        """
        Price a conversion of ``duration_seconds`` (no job is created).

        Voice changer is billed in whole-minute tiers of source length.
        """
        if not model:
            raise ValueError("model is required")
        if duration_seconds in (None, "", 0, "0"):
            raise ValueError("duration_seconds is required")
        data: JSONDict = {
            "model": model,
            "duration_seconds": duration_seconds,
            **kwargs,
        }
        response = self.client.post(VoiceChangerEndpoints.QUOTE, data=data)
        return response.json()

    def queue(
        self,
        model: str,
        *,
        file: Optional[AudioSource] = None,
        audio_url: Optional[str] = None,
        voice: Optional[str] = None,
        remove_background_noise: Optional[bool] = None,
        seed: Optional[int] = None,
        filename: Optional[str] = None,
        **kwargs: Any,
    ) -> VoiceChangerJob:
        """
        Queue a conversion. Supply **exactly one** of ``file`` or ``audio_url``.

        A queued conversion has already been charged — do not retry on a lost
        response; poll :meth:`retrieve` instead.
        """
        if not model:
            raise ValueError("model is required")
        has_file = file is not None
        has_url = bool(audio_url and str(audio_url).strip())
        if has_file == has_url:
            raise ValueError("supply exactly one of file or audio_url")

        extra: JSONDict = {"model": model, **kwargs}
        if voice is not None:
            extra["voice"] = voice
        if remove_background_noise is not None:
            extra["remove_background_noise"] = remove_background_noise
        if seed is not None:
            extra["seed"] = seed

        if has_url:
            extra["audio_url"] = str(audio_url).strip()
            response = self.client.post(VoiceChangerEndpoints.QUEUE, data=extra)
        else:
            files, form = _build_file_multipart(
                file,
                field_name="file",
                filename=filename,
                extra_fields=extra,
            )
            response = self.client.post_multipart(
                VoiceChangerEndpoints.QUEUE,
                files=files,
                form_data=form or None,
            )
        return _job_from_payload(response.json(), fallback_model=model)

    def retrieve(
        self,
        model: str,
        queue_id: str,
        **kwargs: Any,
    ) -> Union[JSONDict, AudioResult]:
        """Poll a job. Returns JSON while processing, :class:`AudioResult` when done."""
        if not model:
            raise ValueError("model is required")
        if not queue_id:
            raise ValueError("queue_id is required")
        data: JSONDict = {"model": model, "queue_id": queue_id, **kwargs}
        response = self.client.post(VoiceChangerEndpoints.RETRIEVE, data=data)
        content_type = (response.headers.get("Content-Type") or "").lower()
        if "audio/" in content_type:
            fmt = "mp3"
            if "wav" in content_type:
                fmt = "wav"
            elif "flac" in content_type:
                fmt = "flac"
            return AudioResult(audio_data=response.content, format=fmt)
        result = response.json()
        try:
            status_i = int(getattr(response, "status_code", 200) or 200)
        except (TypeError, ValueError):
            status_i = 200
        if status_i >= 400:
            raise AudioGenerationError(
                result.get("error", "Retrieve failed") if isinstance(result, dict) else "Retrieve failed"
            )
        return result

    def cleanup(self, queue_id: str, model: str, **kwargs: Any) -> JSONDict:
        """Mark a finished conversion complete (``POST /audio/voice-changer/complete``)."""
        if not queue_id:
            raise AudioGenerationError("queue_id is required")
        if not model:
            raise AudioGenerationError("model is required")
        data: JSONDict = {"queue_id": queue_id, "model": model, **kwargs}
        try:
            response = self.client.post(VoiceChangerEndpoints.COMPLETE, data=data)
            return response.json() if hasattr(response, "json") else {}
        except VeniceAPIError:
            raise
        except Exception as exc:
            raise AudioGenerationError(f"Failed to complete voice-changer job: {exc}") from exc

    def complete(
        self,
        model: str,
        *,
        file: Optional[AudioSource] = None,
        audio_url: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> AudioResult:
        """Queue a conversion and wait for the audio bytes."""
        job = self.queue(model, file=file, audio_url=audio_url, **kwargs)
        wait = 5
        deadline = time.time() + (timeout if timeout is not None else (self.client.config.timeout or 300))
        while True:
            result = self.retrieve(model=model, queue_id=job.queue_id)
            if isinstance(result, AudioResult):
                return result
            if isinstance(result, dict) and result.get("status") not in ("QUEUED", "PROCESSING"):
                raise AudioGenerationError(f"Job ended with status: {result.get('status', 'unknown')}")
            if time.time() > deadline:
                raise AudioGenerationError("Voice changer timed out")
            time.sleep(wait)

    def _validate_with_quote(self, model: str, duration_seconds: Union[int, str]) -> bool:
        try:
            self.quote(model=model, duration_seconds=duration_seconds)
            return True
        except (VeniceAPIError, AudioGenerationError, ValueError):
            return False

    def get_valid_parameters(self, model: str) -> JSONDict:
        """
        Probe ``/audio/voice-changer/quote`` over common source durations.

        Returns ``duration_seconds`` plus ``combinations`` (same shape idea as
        music/video parameter discovery). Quote is free; queue is not.
        """
        common_durations: List[Union[int, str]] = [10, 30, 60, 90, 120, 180]
        combinations: List[JSONDict] = []
        valid_durations: List[Union[int, str]] = []
        for duration in common_durations:
            if self._validate_with_quote(model, duration):
                combinations.append({"duration_seconds": duration})
                valid_durations.append(duration)
        return {
            "duration_seconds": valid_durations,
            "combinations": combinations,
        }


def _job_from_payload(result: Any, fallback_model: str) -> VoiceChangerJob:
    if not isinstance(result, dict):
        raise AudioGenerationError("Invalid voice-changer queue response")
    queue_id = result.get("queue_id")
    if not queue_id:
        raise AudioGenerationError("Voice-changer queue response missing queue_id")
    duration = result.get("duration_seconds")
    return VoiceChangerJob(
        queue_id=str(queue_id),
        model=str(result.get("model") or fallback_model),
        status=str(result.get("status") or "QUEUED"),
        duration_seconds=float(duration) if isinstance(duration, (int, float)) else None,
    )
