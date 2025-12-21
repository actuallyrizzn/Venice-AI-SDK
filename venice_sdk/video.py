"""
Venice AI SDK - Video Generation Module

This module provides text-to-video and image-to-video generation capabilities
using the Venice AI API's async queue system.
"""

from __future__ import annotations

import base64
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import requests

from .client import HTTPClient
from .errors import VeniceAPIError, VideoGenerationError
from .endpoints import VideoEndpoints
from ._http import ensure_http_client

logger = logging.getLogger(__name__)


@dataclass
class VideoMetadata:
    """Metadata about a generated video."""
    duration: Optional[float] = None
    resolution: Optional[str] = None
    fps: Optional[int] = None
    format: Optional[str] = None
    file_size: Optional[int] = None


@dataclass
class VideoJob:
    """Represents a video generation job."""
    job_id: str
    status: str
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    estimated_completion_time: Optional[str] = None
    estimated_time_remaining: Optional[int] = None
    queue_position: Optional[int] = None
    video_url: Optional[str] = None
    video_id: Optional[str] = None
    video_file_path: Optional[Union[str, Path]] = None  # Path to video file when returned directly
    progress: Optional[float] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    model: Optional[str] = None  # Store model for retrieve() calls
    metadata: Optional[VideoMetadata] = None
    
    def is_completed(self) -> bool:
        """Check if the job is completed."""
        return self.status == "completed"
    
    def is_failed(self) -> bool:
        """Check if the job failed."""
        return self.status == "failed"
    
    def is_processing(self) -> bool:
        """Check if the job is still processing."""
        return self.status in ("queued", "processing")
    
    def download(self, path: Union[str, Path]) -> Path:
        """
        Download the generated video to a file.
        
        Args:
            path: Path where to save the video file
            
        Returns:
            Path to the saved file
            
        Raises:
            VideoGenerationError: If video is not ready or download fails
        """
        if not self.is_completed():
            raise VideoGenerationError(
                f"Cannot download video: job status is '{self.status}' (expected 'completed')"
            )
        
        path = Path(path)
        
        # If video was returned directly as a file, copy it
        if self.video_file_path:
            try:
                import shutil
                source_path = Path(self.video_file_path)
                if not source_path.exists():
                    raise VideoGenerationError(f"Video file not found at {source_path}")
                shutil.copy2(source_path, path)
                logger.info("Video copied successfully from %s to %s", source_path, path)
                return path
            except (OSError, IOError) as e:
                raise VideoGenerationError(f"Failed to copy video file: {e}") from e
        
        # Otherwise, download from URL
        if not self.video_url:
            raise VideoGenerationError("No video URL or file path available for download")
        
        try:
            response = requests.get(self.video_url, timeout=300)  # 5 minute timeout for large files
            response.raise_for_status()
            path.write_bytes(response.content)
            logger.info("Video downloaded successfully to %s", path)
            return path
        except requests.RequestException as e:
            raise VideoGenerationError(f"Failed to download video: {e}") from e
    
    def get_video_data(self) -> bytes:
        """
        Get the raw video data as bytes.
        
        Returns:
            Video file data as bytes
            
        Raises:
            VideoGenerationError: If video is not ready or download fails
        """
        if not self.is_completed():
            raise VideoGenerationError(
                f"Cannot get video data: job status is '{self.status}' (expected 'completed')"
            )
        
        # If video was returned directly as a file, read it
        if self.video_file_path:
            try:
                return Path(self.video_file_path).read_bytes()
            except (OSError, IOError) as e:
                raise VideoGenerationError(f"Failed to read video file: {e}") from e
        
        # Otherwise, download from URL
        if not self.video_url:
            raise VideoGenerationError("No video URL or file path available")
        
        try:
            response = requests.get(self.video_url, timeout=300)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            raise VideoGenerationError(f"Failed to download video: {e}") from e


@dataclass
class VideoQuote:
    """Represents a video generation price quote."""
    estimated_cost: float
    currency: str
    estimated_duration: Optional[int] = None
    pricing_breakdown: Optional[Dict[str, Any]] = None
    cost_components: Optional[List[Dict[str, Any]]] = None
    pricing_model: Optional[str] = None
    minimum_cost: Optional[float] = None
    maximum_cost: Optional[float] = None


class VideoAPI:
    """Video generation API client."""
    
    def __init__(self, client: HTTPClient):
        """
        Initialize the video API client.
        
        Args:
            client: HTTP client for making requests
        """
        self.client = client
    
    def _normalize_duration(self, duration: Union[int, str, None]) -> Optional[str]:
        """
        Normalize duration to API format.

        Args:
            duration: Duration as integer (seconds) or string (e.g., "5s")

        Returns:
            Duration string in format "Xs" or None

        Note:
            Supported duration values vary by model. Common values include:
            - "4s", "8s", "12s" (e.g., sora-2-text-to-video)
            - "5s", "10s" (some older models)
            Use validate_parameters=True in queue() to validate before queueing.
        """
        if duration is None:
            return None
        if isinstance(duration, str):
            # If already in string format, return as-is
            return duration
        if isinstance(duration, int):
            # Convert integer to string format (e.g., 5 -> "5s")
            return f"{duration}s"
        return str(duration)
    
    def _save_video_file(self, video_data: bytes, job_id: str) -> Path:
        """
        Save binary video data to a temporary file.
        
        Args:
            video_data: Binary video file data
            job_id: Job ID for filename
            
        Returns:
            Path to the saved video file
        """
        import tempfile
        temp_dir = Path(tempfile.gettempdir()) / "venice_sdk_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename with job_id
        video_path = temp_dir / f"video_{job_id[:8]}.mp4"
        video_path.write_bytes(video_data)
        logger.info("Video file saved to %s (%d bytes)", video_path, len(video_data))
        return video_path
    
    def _encode_image(self, image: Union[str, bytes, Path]) -> str:
        """
        Encode image to base64 data URI.
        
        Args:
            image: Image path, URL, or bytes
            
        Returns:
            Base64-encoded data URI string
        """
        if isinstance(image, str):
            if image.startswith(('http://', 'https://')):
                # It's a URL, return as-is
                return image
            elif image.startswith('data:'):
                # Already a data URI
                return image
            else:
                # Assume it's a file path
                image_path = Path(image)
                if not image_path.exists():
                    raise VideoGenerationError(f"Image file not found: {image}")
                image_data = image_path.read_bytes()
        elif isinstance(image, bytes):
            image_data = image
        elif isinstance(image, Path):
            if not image.exists():
                raise VideoGenerationError(f"Image file not found: {image}")
            image_data = image.read_bytes()
        else:
            raise VideoGenerationError(f"Invalid image type: {type(image)}")
        
        # Encode to base64
        b64_data = base64.b64encode(image_data).decode('utf-8')
        # Assume PNG format if we can't determine
        return f"data:image/png;base64,{b64_data}"
    
    def _validate_with_quote(
        self,
        model: str,
        prompt: Optional[str] = None,
        image: Optional[Union[str, bytes, Path]] = None,
        duration: Optional[Union[int, str]] = None,
        resolution: Optional[str] = None,
        audio: bool = False,
        seed: Optional[int] = None,
        negative_prompt: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        fps: Optional[int] = None,
        motion_bucket_id: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        **kwargs: Any
    ) -> bool:
        """
        Validate parameters using the quote API (free).
        
        Args:
            Same as queue() method parameters
            
        Returns:
            True if parameters are valid, False otherwise
        """
        try:
            self.quote(
                model=model,
                prompt=prompt,
                image=image,
                duration=duration,
                resolution=resolution,
                audio=audio,
                seed=seed,
                negative_prompt=negative_prompt,
                aspect_ratio=aspect_ratio,
                fps=fps,
                motion_bucket_id=motion_bucket_id,
                guidance_scale=guidance_scale,
                **kwargs
            )
            return True
        except (VeniceAPIError, VideoGenerationError):
            return False
    
    def get_valid_parameters(
        self,
        model: str,
        prompt: Optional[str] = None,
        image: Optional[Union[str, bytes, Path]] = None,
    ) -> Dict[str, Any]:
        """
        Discover valid duration and aspect_ratio combinations for a model.
        
        This method tries common parameter combinations and returns valid ones.
        Uses the free quote API for validation.
        
        Args:
            model: Video model ID
            prompt: Text prompt (required for text-to-video)
            image: Image file (required for image-to-video)
            
        Returns:
            Dictionary with 'duration' and 'aspect_ratio' keys containing lists of valid values
            
        Example:
            >>> valid = video.get_valid_parameters("sora-2-text-to-video", prompt="test")
            >>> print(valid)
            {'duration': ['4s', '8s', '12s'], 'aspect_ratio': ['16:9', '9:16']}
        """
        common_durations = ["4s", "5s", "6s", "8s", "10s", "12s"]
        common_aspect_ratios = ["16:9", "9:16", "1:1", "4:3"]
        
        valid_durations = []
        valid_aspect_ratios = []
        
        # Test each duration with a common aspect ratio
        test_aspect_ratio = "16:9"
        for duration in common_durations:
            if self._validate_with_quote(
                model=model,
                prompt=prompt,
                image=image,
                duration=duration,
                aspect_ratio=test_aspect_ratio,
            ):
                valid_durations.append(duration)
        
        # Test each aspect ratio with a valid duration (or first common one)
        test_duration = valid_durations[0] if valid_durations else common_durations[0]
        for aspect_ratio in common_aspect_ratios:
            if self._validate_with_quote(
                model=model,
                prompt=prompt,
                image=image,
                duration=test_duration,
                aspect_ratio=aspect_ratio,
            ):
                valid_aspect_ratios.append(aspect_ratio)
        
        return {
            "duration": valid_durations,
            "aspect_ratio": valid_aspect_ratios,
        }
    
    def queue(
        self,
        model: str,
        prompt: Optional[str] = None,
        image: Optional[Union[str, bytes, Path]] = None,
        duration: Optional[Union[int, str]] = None,
        resolution: Optional[str] = None,
        audio: bool = False,
        seed: Optional[int] = None,
        negative_prompt: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        fps: Optional[int] = None,
        motion_bucket_id: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        validate_parameters: bool = False,
        **kwargs: Any
    ) -> VideoJob:
        """
        Queue a video generation job.
        
        Args:
            model: Video model ID (e.g., "kling-2.6-pro-text-to-video")
            prompt: Text description of the video (required for text-to-video)
            image: Image file path, URL, or bytes (required for image-to-video)
            duration: Video duration in seconds
            resolution: Video resolution (e.g., "720p", "1080p", "4k")
            audio: Whether to include audio
            seed: Random seed for reproducibility
            negative_prompt: Text describing what should not appear
            aspect_ratio: Desired aspect ratio (e.g., "16:9", "9:16")
            fps: Frames per second
            motion_bucket_id: Motion intensity for image-to-video (1-127)
            guidance_scale: How closely to follow the prompt
            validate_parameters: If True, validate parameters using quote API before queueing (default: False)
            **kwargs: Additional parameters
            
        Returns:
            VideoJob with job_id and initial status
            
        Raises:
            VideoGenerationError: If request fails or parameters are invalid
            
        Note:
            Some models require both `duration` and `aspect_ratio` parameters. While the
            `quote()` method accepts these as optional, the `queue()` endpoint requires both
            for certain models. Use `validate_parameters=True` to validate parameter combinations
            before queueing (uses free quote API), or `get_valid_parameters()` to discover
            valid combinations for a model.
        """
        # Validate that either prompt or image is provided
        if not prompt and not image:
            raise VideoGenerationError("Either 'prompt' (for text-to-video) or 'image' (for image-to-video) must be provided")
        
        # Optional parameter validation using quote API
        if validate_parameters:
            if not self._validate_with_quote(
                model=model,
                prompt=prompt,
                image=image,
                duration=duration,
                resolution=resolution,
                audio=audio,
                seed=seed,
                negative_prompt=negative_prompt,
                aspect_ratio=aspect_ratio,
                fps=fps,
                motion_bucket_id=motion_bucket_id,
                guidance_scale=guidance_scale,
                **kwargs
            ):
                raise VideoGenerationError(
                    "Invalid parameter combination for model. Use get_valid_parameters() "
                    "to discover valid duration and aspect_ratio combinations."
                )
        
        data: Dict[str, Any] = {
            "model": model,
            **kwargs
        }
        # Only include audio if explicitly set to True (some models don't support audio parameter)
        if audio:
            data["audio"] = audio
        
        if prompt:
            data["prompt"] = prompt
        if image:
            # For image-to-video, API expects image_url instead of image
            encoded_image = self._encode_image(image)
            data["image_url"] = encoded_image
        if duration is not None:
            data["duration"] = self._normalize_duration(duration)
        if resolution:
            data["resolution"] = resolution
        if seed is not None:
            data["seed"] = seed
        if negative_prompt:
            data["negative_prompt"] = negative_prompt
        if aspect_ratio:
            data["aspect_ratio"] = aspect_ratio
        if fps is not None:
            data["fps"] = fps
        if motion_bucket_id is not None:
            data["motion_bucket_id"] = motion_bucket_id
        if guidance_scale is not None:
            data["guidance_scale"] = guidance_scale
        
        logger.debug(
            "Queueing video generation (model=%s, has_prompt=%s, has_image=%s, duration=%s, resolution=%s)",
            model,
            bool(prompt),
            bool(image),
            data.get("duration"),
            resolution,
        )
        
        try:
            # Use extended timeout for queue operations (video generation can take time to queue)
            # Default is 30s, but queue operations may need 60-120s in high load scenarios
            # Use 120s timeout to prevent premature timeouts that could cause retries and duplicate charges
            # CRITICAL: Extended timeout prevents timeout->retry->duplicate charge scenarios
            response = self.client.post(VideoEndpoints.QUEUE, data=data, timeout=120)
            result = response.json()
            
            # Build metadata if present
            metadata = None
            if "metadata" in result:
                meta_data = result["metadata"]
                metadata = VideoMetadata(
                    duration=meta_data.get("duration"),
                    resolution=meta_data.get("resolution"),
                    fps=meta_data.get("fps"),
                    format=meta_data.get("format"),
                    file_size=meta_data.get("file_size"),
                )
            
            # Handle both job_id and queue_id for backward compatibility
            job_id_value = result.get("job_id") or result.get("queue_id", "")
            
            job = VideoJob(
                job_id=job_id_value,
                status=result.get("status", "queued"),
                created_at=result.get("created_at"),
                estimated_completion_time=result.get("estimated_completion_time"),
                queue_position=result.get("queue_position"),
                model=model,
                metadata=metadata,
            )
            
            if not job.job_id:
                raise VideoGenerationError("No job_id returned from queue endpoint")
            
            logger.info("Video generation queued: job_id=%s", job.job_id)
            return job
            
        except VeniceAPIError:
            raise
        except Exception as e:
            raise VideoGenerationError(f"Failed to queue video generation: {e}") from e
    
    def retrieve(self, job_id: str, model: Optional[str] = None) -> VideoJob:
        """
        Retrieve the status and result of a video generation job.
        
        Args:
            job_id: The job ID from the queue response
            model: The model ID used for the job (required by API). If not provided,
                   will attempt to retrieve from the job if available.
            
        Returns:
            VideoJob with current status and results if completed
            
        Raises:
            VideoGenerationError: If request fails or job not found
        """
        if not job_id:
            raise VideoGenerationError("job_id is required")
        
        # API requires both queue_id and model
        data = {"queue_id": job_id}
        if model:
            data["model"] = model
        
        logger.debug("Retrieving video job: job_id=%s, model=%s", job_id, model)
        
        try:
            # If model not provided but we have it from a previous job, try to use it
            # But API requires it, so we must have it
            if not model:
                raise VideoGenerationError(
                    "Model parameter is required for retrieve(). "
                    "Pass the model parameter or use wait_for_completion() which handles this automatically."
                )
            
            response = self.client.post(VideoEndpoints.RETRIEVE, data=data)
            
            # Check if response is binary video file instead of JSON
            content_type = response.headers.get('Content-Type', '').lower()
            content = response.content
            
            # Check for binary video response
            is_video_response = False
            if 'video' in content_type or 'application/octet-stream' in content_type:
                is_video_response = True
            elif len(content) > 1000:  # Large response might be video
                # Check for MP4 magic bytes (ftyp box)
                if content[:4] in (b'\x00\x00\x00\x18', b'\x00\x00\x00 ', b'\x00\x00\x00\x20'):
                    # Check for 'ftyp' at offset 4 (MP4 file signature)
                    if len(content) > 8 and content[4:8] == b'ftyp':
                        is_video_response = True
            
            if is_video_response:
                # API returned video file directly - save it and return completed job
                logger.info("API returned video file directly (Content-Type: %s, size: %d bytes)", 
                           content_type or 'unknown', len(content))
                video_path = self._save_video_file(content, job_id)
                return VideoJob(
                    job_id=job_id,
                    status='completed',
                    video_file_path=video_path,
                    model=None,  # Model not available in binary response
                )
            
            # Normal JSON response
            try:
                result = response.json()
            except (ValueError, requests.exceptions.JSONDecodeError) as json_error:
                # If JSON parsing fails, check if it might be a video file we missed
                error_str = str(json_error)
                if ("Expecting value" in error_str or "JSONDecodeError" in error_str) and len(content) > 1000:
                    # Check for MP4 magic bytes as fallback
                    if content[:4] in (b'\x00\x00\x00\x18', b'\x00\x00\x00 ', b'\x00\x00\x00\x20'):
                        if len(content) > 8 and content[4:8] == b'ftyp':
                            logger.info("Detected binary video response (MP4 magic bytes, fallback detection)")
                            video_path = self._save_video_file(content, job_id)
                            return VideoJob(
                                job_id=job_id,
                                status='completed',
                                video_file_path=video_path,
                                model=None,
                            )
                raise VideoGenerationError(f"Failed to parse response as JSON: {json_error}") from json_error
            
            # Build metadata if present
            metadata = None
            if "metadata" in result:
                meta_data = result["metadata"]
                metadata = VideoMetadata(
                    duration=meta_data.get("duration"),
                    resolution=meta_data.get("resolution"),
                    fps=meta_data.get("fps"),
                    format=meta_data.get("format"),
                    file_size=meta_data.get("file_size"),
                )
            
            job = VideoJob(
                job_id=result.get("job_id", job_id),
                status=result.get("status", "unknown"),
                created_at=result.get("created_at"),
                started_at=result.get("started_at"),
                completed_at=result.get("completed_at"),
                estimated_time_remaining=result.get("estimated_time_remaining"),
                video_url=result.get("video_url"),
                video_id=result.get("video_id"),
                progress=result.get("progress"),
                error=result.get("error"),
                error_code=result.get("error_code"),
                model=result.get("model"),
                metadata=metadata,
            )
            
            logger.debug("Video job status: job_id=%s, status=%s, progress=%s", job_id, job.status, job.progress)
            return job
            
        except VeniceAPIError:
            raise
        except Exception as e:
            raise VideoGenerationError(f"Failed to retrieve video job: {e}") from e
    
    def wait_for_completion(
        self,
        job_id: str,
        poll_interval: int = 5,
        max_wait_time: Optional[int] = None,
        callback: Optional[Callable[[VideoJob], None]] = None,
        model: Optional[str] = None
    ) -> VideoJob:
        """
        Poll for job completion until it finishes or fails.
        
        Args:
            job_id: The job ID to wait for
            poll_interval: Seconds between polls (default: 5)
            max_wait_time: Maximum seconds to wait (None for no limit)
            callback: Optional callback function called with VideoJob on each poll
            model: The model ID used for the job (required for retrieve calls)
            
        Returns:
            VideoJob when completed or failed
            
        Raises:
            VideoGenerationError: If job fails or timeout is reached
        """
        start_time = time.time()
        poll_count = 0
        
        logger.info("Waiting for video generation to complete: job_id=%s", job_id)
        
        # Track model for retrieve calls
        stored_model = model
        
        while True:
            # Use stored model or model from job if available
            retrieve_model = stored_model
            if not retrieve_model:
                # Try to get model from a previous retrieve if we have it cached
                # For now, we require model parameter
                if not retrieve_model:
                    raise VideoGenerationError(
                        "Model parameter is required for wait_for_completion(). "
                        "Pass the model used when queueing the job."
                    )
            
            job = self.retrieve(job_id, model=retrieve_model)
            # Update stored model from job response if available
            if job.model and not stored_model:
                stored_model = job.model
            poll_count += 1
            
            if callback:
                try:
                    callback(job)
                except Exception as e:
                    logger.warning("Callback raised exception: %s", e)
            
            if job.is_completed():
                logger.info("Video generation completed: job_id=%s (polls=%s)", job_id, poll_count)
                return job
            
            if job.is_failed():
                error_msg = job.error or "Unknown error"
                raise VideoGenerationError(f"Video generation failed: {error_msg}")
            
            # Check timeout
            if max_wait_time:
                elapsed = time.time() - start_time
                if elapsed >= max_wait_time:
                    raise VideoGenerationError(
                        f"Timeout waiting for video generation (waited {elapsed:.0f}s, max={max_wait_time}s)"
                    )
            
            # Wait before next poll
            time.sleep(poll_interval)
    
    def quote(
        self,
        model: str,
        prompt: Optional[str] = None,
        image: Optional[Union[str, bytes, Path]] = None,
        duration: Optional[Union[int, str]] = None,
        resolution: Optional[str] = None,
        audio: bool = False,
        seed: Optional[int] = None,
        negative_prompt: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        fps: Optional[int] = None,
        motion_bucket_id: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        **kwargs: Any
    ) -> VideoQuote:
        """
        Get a price quote for video generation.
        
        Args:
            model: Video model ID
            prompt: Text description of the video (required for text-to-video)
            image: Image file path, URL, or bytes (required for image-to-video)
            duration: Video duration in seconds (optional for quote, but may be required for queue)
            resolution: Video resolution
            audio: Whether to include audio
            seed: Random seed
            negative_prompt: Text describing what should not appear
            aspect_ratio: Desired aspect ratio (optional for quote, but may be required for queue)
            fps: Frames per second
            motion_bucket_id: Motion intensity for image-to-video
            guidance_scale: How closely to follow the prompt
            **kwargs: Additional parameters
            
        Returns:
            VideoQuote with estimated cost and duration
            
        Raises:
            VideoGenerationError: If request fails or parameters are invalid
            
        Note:
            The quote API accepts optional parameters, but the queue API may require both
            `duration` and `aspect_ratio` for certain models. Use `validate_parameters=True`
            in `queue()` or `get_valid_parameters()` to discover required parameters for a model.
        """
        # Validate that either prompt or image is provided
        if not prompt and not image:
            raise VideoGenerationError("Either 'prompt' (for text-to-video) or 'image' (for image-to-video) must be provided")
        
        data: Dict[str, Any] = {
            "model": model,
            **kwargs
        }
        # Only include audio if explicitly set to True (some models don't support audio parameter)
        if audio:
            data["audio"] = audio
        
        if prompt:
            data["prompt"] = prompt
        if image:
            # For image-to-video, API expects image_url instead of image
            encoded_image = self._encode_image(image)
            data["image_url"] = encoded_image
        if duration is not None:
            data["duration"] = self._normalize_duration(duration)
        if resolution:
            data["resolution"] = resolution
        if seed is not None:
            data["seed"] = seed
        if negative_prompt:
            data["negative_prompt"] = negative_prompt
        if aspect_ratio:
            data["aspect_ratio"] = aspect_ratio
        if fps is not None:
            data["fps"] = fps
        if motion_bucket_id is not None:
            data["motion_bucket_id"] = motion_bucket_id
        if guidance_scale is not None:
            data["guidance_scale"] = guidance_scale
        
        logger.debug("Getting video generation quote: model=%s", model)
        
        try:
            response = self.client.post(VideoEndpoints.QUOTE, data=data)
            result = response.json()
            
            # API returns "quote" field, but we also support "estimated_cost" for backward compatibility
            estimated_cost = result.get("quote") or result.get("estimated_cost", 0.0)
            
            quote = VideoQuote(
                estimated_cost=estimated_cost,
                currency=result.get("currency", "USD"),
                estimated_duration=result.get("estimated_duration"),
                pricing_breakdown=result.get("pricing_breakdown"),
                cost_components=result.get("cost_components"),
                pricing_model=result.get("pricing_model"),
                minimum_cost=result.get("minimum_cost"),
                maximum_cost=result.get("maximum_cost"),
            )
            
            logger.debug("Video quote: cost=%s %s", quote.estimated_cost, quote.currency)
            return quote
            
        except VeniceAPIError:
            raise
        except Exception as e:
            raise VideoGenerationError(f"Failed to get video quote: {e}") from e
    
    def complete(
        self,
        model: str,
        prompt: Optional[str] = None,
        image: Optional[Union[str, bytes, Path]] = None,
        duration: Optional[Union[int, str]] = None,
        resolution: Optional[str] = None,
        audio: bool = False,
        seed: Optional[int] = None,
        negative_prompt: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        fps: Optional[int] = None,
        motion_bucket_id: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        timeout: int = 900,  # 15 minutes default
        **kwargs: Any
    ) -> VideoJob:
        """
        Generate a video synchronously (queue and wait for completion).
        
        This method combines queue and retrieve in a single call, waiting for
        the video to be generated before returning. For production use, consider
        using the async queue/retrieve pattern instead.
        
        Args:
            model: Video model ID
            prompt: Text description of the video (required for text-to-video)
            image: Image file path, URL, or bytes (required for image-to-video)
            duration: Video duration in seconds
            resolution: Video resolution
            audio: Whether to include audio
            seed: Random seed
            negative_prompt: Text describing what should not appear
            aspect_ratio: Desired aspect ratio
            fps: Frames per second
            motion_bucket_id: Motion intensity for image-to-video
            guidance_scale: How closely to follow the prompt
            timeout: Maximum seconds to wait (default: 900 = 15 minutes)
            **kwargs: Additional parameters
            
        Returns:
            VideoJob when completed
            
        Raises:
            VideoGenerationError: If generation fails or timeout is reached
        """
        # Queue the job
        job = self.queue(
            model=model,
            prompt=prompt,
            image=image,
            duration=duration,
            resolution=resolution,
            audio=audio,
            seed=seed,
            negative_prompt=negative_prompt,
            aspect_ratio=aspect_ratio,
            fps=fps,
            motion_bucket_id=motion_bucket_id,
            guidance_scale=guidance_scale,
            **kwargs
        )
        
        # Wait for completion (pass model for retrieve calls)
        # Job already has model stored, but pass it explicitly for clarity
        return self.wait_for_completion(job.job_id, max_wait_time=timeout, model=job.model or model)

