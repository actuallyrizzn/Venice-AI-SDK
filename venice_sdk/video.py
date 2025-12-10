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
    progress: Optional[float] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    model: Optional[str] = None
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
        
        if not self.video_url:
            raise VideoGenerationError("No video URL available for download")
        
        path = Path(path)
        
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
        
        if not self.video_url:
            raise VideoGenerationError("No video URL available")
        
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
            API currently only supports "5s" or "10s". Other values will be
            converted but may be rejected by the API.
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
            **kwargs: Additional parameters
            
        Returns:
            VideoJob with job_id and initial status
            
        Raises:
            VideoGenerationError: If request fails or parameters are invalid
        """
        # Validate that either prompt or image is provided
        if not prompt and not image:
            raise VideoGenerationError("Either 'prompt' (for text-to-video) or 'image' (for image-to-video) must be provided")
        
        data: Dict[str, Any] = {
            "model": model,
            "audio": audio,
            **kwargs
        }
        
        if prompt:
            data["prompt"] = prompt
        if image:
            data["image"] = self._encode_image(image)
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
            response = self.client.post(VideoEndpoints.QUEUE, data=data)
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
            
            job = VideoJob(
                job_id=result.get("job_id", ""),
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
    
    def retrieve(self, job_id: str) -> VideoJob:
        """
        Retrieve the status and result of a video generation job.
        
        Args:
            job_id: The job ID from the queue response
            
        Returns:
            VideoJob with current status and results if completed
            
        Raises:
            VideoGenerationError: If request fails or job not found
        """
        if not job_id:
            raise VideoGenerationError("job_id is required")
        
        data = {"job_id": job_id}
        
        logger.debug("Retrieving video job: job_id=%s", job_id)
        
        try:
            response = self.client.post(VideoEndpoints.RETRIEVE, data=data)
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
        callback: Optional[Callable[[VideoJob], None]] = None
    ) -> VideoJob:
        """
        Poll for job completion until it finishes or fails.
        
        Args:
            job_id: The job ID to wait for
            poll_interval: Seconds between polls (default: 5)
            max_wait_time: Maximum seconds to wait (None for no limit)
            callback: Optional callback function called with VideoJob on each poll
            
        Returns:
            VideoJob when completed or failed
            
        Raises:
            VideoGenerationError: If job fails or timeout is reached
        """
        start_time = time.time()
        poll_count = 0
        
        logger.info("Waiting for video generation to complete: job_id=%s", job_id)
        
        while True:
            job = self.retrieve(job_id)
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
            duration: Video duration in seconds
            resolution: Video resolution
            audio: Whether to include audio
            seed: Random seed
            negative_prompt: Text describing what should not appear
            aspect_ratio: Desired aspect ratio
            fps: Frames per second
            motion_bucket_id: Motion intensity for image-to-video
            guidance_scale: How closely to follow the prompt
            **kwargs: Additional parameters
            
        Returns:
            VideoQuote with estimated cost and duration
            
        Raises:
            VideoGenerationError: If request fails or parameters are invalid
        """
        # Validate that either prompt or image is provided
        if not prompt and not image:
            raise VideoGenerationError("Either 'prompt' (for text-to-video) or 'image' (for image-to-video) must be provided")
        
        data: Dict[str, Any] = {
            "model": model,
            "audio": audio,
            **kwargs
        }
        
        if prompt:
            data["prompt"] = prompt
        if image:
            # For image-to-video, API expects image_url instead of image
            encoded_image = self._encode_image(image)
            # If it's a URL, use image_url, otherwise use image
            if encoded_image.startswith(('http://', 'https://')):
                data["image_url"] = encoded_image
            else:
                # For base64 data URIs, use image_url as well
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
            
            quote = VideoQuote(
                estimated_cost=result.get("estimated_cost", 0.0),
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
        
        # Wait for completion
        return self.wait_for_completion(job.job_id, max_wait_time=timeout)

