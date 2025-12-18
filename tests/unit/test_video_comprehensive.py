"""
Comprehensive unit tests for the video module.
"""

import base64
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import pytest
from venice_sdk.video import (
    VideoMetadata,
    VideoJob,
    VideoQuote,
    VideoAPI,
)
from venice_sdk.errors import VeniceAPIError, VideoGenerationError
from venice_sdk.endpoints import VideoEndpoints


class TestVideoMetadataComprehensive:
    """Comprehensive test suite for VideoMetadata class."""

    def test_video_metadata_initialization(self):
        """Test VideoMetadata initialization with all parameters."""
        metadata = VideoMetadata(
            duration=5.5,
            resolution="1080p",
            fps=30,
            format="mp4",
            file_size=1024000
        )
        
        assert metadata.duration == 5.5
        assert metadata.resolution == "1080p"
        assert metadata.fps == 30
        assert metadata.format == "mp4"
        assert metadata.file_size == 1024000

    def test_video_metadata_initialization_with_defaults(self):
        """Test VideoMetadata initialization with default values."""
        metadata = VideoMetadata()
        
        assert metadata.duration is None
        assert metadata.resolution is None
        assert metadata.fps is None
        assert metadata.format is None
        assert metadata.file_size is None

    def test_video_metadata_equality(self):
        """Test VideoMetadata equality comparison."""
        meta1 = VideoMetadata(duration=5.0, resolution="1080p")
        meta2 = VideoMetadata(duration=5.0, resolution="1080p")
        meta3 = VideoMetadata(duration=3.0, resolution="720p")
        
        assert meta1 == meta2
        assert meta1 != meta3

    def test_video_metadata_string_representation(self):
        """Test VideoMetadata string representation."""
        metadata = VideoMetadata(duration=5.0, resolution="1080p")
        meta_str = str(metadata)
        
        assert "VideoMetadata" in meta_str


class TestVideoJobComprehensive:
    """Comprehensive test suite for VideoJob class."""

    def test_video_job_initialization(self):
        """Test VideoJob initialization with all parameters."""
        metadata = VideoMetadata(duration=5.0, resolution="1080p")
        job = VideoJob(
            job_id="job_123",
            status="completed",
            created_at="2024-01-01T00:00:00Z",
            started_at="2024-01-01T00:00:01Z",
            completed_at="2024-01-01T00:00:10Z",
            estimated_completion_time="2024-01-01T00:00:10Z",
            estimated_time_remaining=5,
            queue_position=1,
            video_url="https://example.com/video.mp4",
            video_id="video_456",
            progress=100.0,
            error=None,
            error_code=None,
            model="kling-2.6-pro-text-to-video",
            metadata=metadata
        )
        
        assert job.job_id == "job_123"
        assert job.status == "completed"
        assert job.video_url == "https://example.com/video.mp4"
        assert job.progress == 100.0
        assert job.metadata == metadata

    def test_video_job_initialization_with_defaults(self):
        """Test VideoJob initialization with default values."""
        job = VideoJob(job_id="job_123", status="queued")
        
        assert job.job_id == "job_123"
        assert job.status == "queued"
        assert job.created_at is None
        assert job.video_url is None
        assert job.metadata is None

    def test_is_completed(self):
        """Test is_completed method."""
        completed_job = VideoJob(job_id="job_123", status="completed")
        queued_job = VideoJob(job_id="job_456", status="queued")
        
        assert completed_job.is_completed() is True
        assert queued_job.is_completed() is False

    def test_is_failed(self):
        """Test is_failed method."""
        failed_job = VideoJob(job_id="job_123", status="failed")
        queued_job = VideoJob(job_id="job_456", status="queued")
        
        assert failed_job.is_failed() is True
        assert queued_job.is_failed() is False

    def test_is_processing(self):
        """Test is_processing method."""
        queued_job = VideoJob(job_id="job_123", status="queued")
        processing_job = VideoJob(job_id="job_456", status="processing")
        completed_job = VideoJob(job_id="job_789", status="completed")
        
        assert queued_job.is_processing() is True
        assert processing_job.is_processing() is True
        assert completed_job.is_processing() is False

    def test_download_success(self, tmp_path):
        """Test successful video download."""
        job = VideoJob(
            job_id="job_123",
            status="completed",
            video_url="https://example.com/video.mp4"
        )
        
        with patch('venice_sdk.video.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"fake video data"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            output_path = tmp_path / "video.mp4"
            saved_path = job.download(output_path)
            
            assert saved_path == output_path
            assert output_path.exists()
            assert output_path.read_bytes() == b"fake video data"
            mock_get.assert_called_once_with("https://example.com/video.mp4", timeout=300)

    def test_download_with_string_path(self, tmp_path):
        """Test download with string path."""
        job = VideoJob(
            job_id="job_123",
            status="completed",
            video_url="https://example.com/video.mp4"
        )
        
        with patch('venice_sdk.video.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"fake video data"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            output_path = str(tmp_path / "video.mp4")
            saved_path = job.download(output_path)
            
            assert isinstance(saved_path, Path)
            assert saved_path.exists()

    def test_download_not_completed(self):
        """Test download when job is not completed."""
        job = VideoJob(job_id="job_123", status="processing")
        
        with pytest.raises(VideoGenerationError, match="Cannot download video: job status is 'processing'"):
            job.download("video.mp4")

    def test_download_no_video_url_or_file_path(self):
        """Test download when neither video URL nor file path is available."""
        job = VideoJob(job_id="job_123", status="completed", video_url=None, video_file_path=None)
        
        with pytest.raises(VideoGenerationError, match="No video URL or file path available for download"):
            job.download("video.mp4")

    def test_download_request_exception(self):
        """Test download when request fails."""
        job = VideoJob(
            job_id="job_123",
            status="completed",
            video_url="https://example.com/video.mp4"
        )
        
        with patch('venice_sdk.video.requests.get') as mock_get:
            import requests
            mock_get.side_effect = requests.RequestException("Network error")
            
            with pytest.raises(VideoGenerationError, match="Failed to download video"):
                job.download("video.mp4")

    def test_get_video_data_success(self):
        """Test getting video data successfully."""
        job = VideoJob(
            job_id="job_123",
            status="completed",
            video_url="https://example.com/video.mp4"
        )
        
        with patch('venice_sdk.video.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"fake video data"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            data = job.get_video_data()
            
            assert data == b"fake video data"
            mock_get.assert_called_once_with("https://example.com/video.mp4", timeout=300)

    def test_get_video_data_not_completed(self):
        """Test get_video_data when job is not completed."""
        job = VideoJob(job_id="job_123", status="processing")
        
        with pytest.raises(VideoGenerationError, match="Cannot get video data: job status is 'processing'"):
            job.get_video_data()

    def test_get_video_data_no_url_or_file_path(self):
        """Test get_video_data when neither URL nor file path is available."""
        job = VideoJob(job_id="job_123", status="completed", video_url=None, video_file_path=None)
        
        with pytest.raises(VideoGenerationError, match="No video URL or file path available"):
            job.get_video_data()

    def test_get_video_data_request_exception(self):
        """Test get_video_data when request fails."""
        job = VideoJob(
            job_id="job_123",
            status="completed",
            video_url="https://example.com/video.mp4"
        )
        
        with patch('venice_sdk.video.requests.get') as mock_get:
            import requests
            mock_get.side_effect = requests.RequestException("Network error")
            
            with pytest.raises(VideoGenerationError, match="Failed to download video"):
                job.get_video_data()

    def test_video_job_equality(self):
        """Test VideoJob equality comparison."""
        job1 = VideoJob(job_id="job_123", status="completed")
        job2 = VideoJob(job_id="job_123", status="completed")
        job3 = VideoJob(job_id="job_456", status="queued")
        
        assert job1 == job2
        assert job1 != job3

    def test_video_job_string_representation(self):
        """Test VideoJob string representation."""
        job = VideoJob(job_id="job_123", status="completed")
        job_str = str(job)
        
        assert "VideoJob" in job_str


class TestVideoQuoteComprehensive:
    """Comprehensive test suite for VideoQuote class."""

    def test_video_quote_initialization(self):
        """Test VideoQuote initialization with all parameters."""
        quote = VideoQuote(
            estimated_cost=0.50,
            currency="USD",
            estimated_duration=120,
            pricing_breakdown={"base": 0.30, "duration": 0.20},
            cost_components=[{"name": "base", "cost": 0.30}],
            pricing_model="per_second",
            minimum_cost=0.10,
            maximum_cost=1.00
        )
        
        assert quote.estimated_cost == 0.50
        assert quote.currency == "USD"
        assert quote.estimated_duration == 120
        assert quote.pricing_breakdown == {"base": 0.30, "duration": 0.20}
        assert quote.cost_components == [{"name": "base", "cost": 0.30}]
        assert quote.pricing_model == "per_second"
        assert quote.minimum_cost == 0.10
        assert quote.maximum_cost == 1.00

    def test_video_quote_initialization_with_defaults(self):
        """Test VideoQuote initialization with default values."""
        quote = VideoQuote(estimated_cost=0.50, currency="USD")
        
        assert quote.estimated_cost == 0.50
        assert quote.currency == "USD"
        assert quote.estimated_duration is None
        assert quote.pricing_breakdown is None

    def test_video_quote_equality(self):
        """Test VideoQuote equality comparison."""
        quote1 = VideoQuote(estimated_cost=0.50, currency="USD")
        quote2 = VideoQuote(estimated_cost=0.50, currency="USD")
        quote3 = VideoQuote(estimated_cost=1.00, currency="USD")
        
        assert quote1 == quote2
        assert quote1 != quote3

    def test_video_quote_string_representation(self):
        """Test VideoQuote string representation."""
        quote = VideoQuote(estimated_cost=0.50, currency="USD")
        quote_str = str(quote)
        
        assert "VideoQuote" in quote_str


class TestVideoAPIComprehensive:
    """Comprehensive test suite for VideoAPI class."""

    def test_video_api_initialization(self, mock_client):
        """Test VideoAPI initialization."""
        api = VideoAPI(mock_client)
        assert api.client == mock_client

    def test_encode_image_from_path(self, tmp_path):
        """Test encoding image from file path."""
        image_path = tmp_path / "test.png"
        image_data = b"fake image data"
        image_path.write_bytes(image_data)
        
        api = VideoAPI(MagicMock())
        encoded = api._encode_image(image_path)
        
        assert encoded.startswith("data:image/png;base64,")
        decoded = base64.b64decode(encoded.split(",")[1])
        assert decoded == image_data

    def test_encode_image_from_string_path(self, tmp_path):
        """Test encoding image from string path."""
        image_path = tmp_path / "test.png"
        image_data = b"fake image data"
        image_path.write_bytes(image_data)
        
        api = VideoAPI(MagicMock())
        encoded = api._encode_image(str(image_path))
        
        assert encoded.startswith("data:image/png;base64,")

    def test_encode_image_from_bytes(self):
        """Test encoding image from bytes."""
        image_data = b"fake image data"
        
        api = VideoAPI(MagicMock())
        encoded = api._encode_image(image_data)
        
        assert encoded.startswith("data:image/png;base64,")
        decoded = base64.b64decode(encoded.split(",")[1])
        assert decoded == image_data

    def test_encode_image_from_url(self):
        """Test encoding image from URL."""
        image_url = "https://example.com/image.png"
        
        api = VideoAPI(MagicMock())
        encoded = api._encode_image(image_url)
        
        assert encoded == image_url

    def test_encode_image_from_data_uri(self):
        """Test encoding image from data URI."""
        data_uri = "data:image/png;base64,dGVzdA=="
        
        api = VideoAPI(MagicMock())
        encoded = api._encode_image(data_uri)
        
        assert encoded == data_uri

    def test_encode_image_file_not_found(self):
        """Test encoding image when file doesn't exist."""
        api = VideoAPI(MagicMock())
        
        with pytest.raises(VideoGenerationError, match="Image file not found"):
            api._encode_image("nonexistent.png")

    def test_encode_image_invalid_type(self):
        """Test encoding image with invalid type."""
        api = VideoAPI(MagicMock())
        
        with pytest.raises(VideoGenerationError, match="Invalid image type"):
            api._encode_image(12345)

    def test_queue_text_to_video_success(self, mock_client):
        """Test successful text-to-video queue."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "job_id": "job_123",
            "status": "queued",
            "created_at": "2024-01-01T00:00:00Z"
        }
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        job = api.queue(
            model="kling-2.6-pro-text-to-video",
            prompt="A beautiful sunset",
            duration=5,
            resolution="1080p"
        )
        
        assert job.job_id == "job_123"
        assert job.status == "queued"
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == VideoEndpoints.QUEUE
        assert call_args[1]["data"]["model"] == "kling-2.6-pro-text-to-video"
        assert call_args[1]["data"]["prompt"] == "A beautiful sunset"

    def test_queue_image_to_video_success(self, mock_client, tmp_path):
        """Test successful image-to-video queue."""
        image_path = tmp_path / "test.png"
        image_path.write_bytes(b"fake image")
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "job_id": "job_123",
            "status": "queued"
        }
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        job = api.queue(
            model="kling-2.6-pro-image-to-video",
            image=image_path,
            prompt="Animate this",
            duration=3
        )
        
        assert job.job_id == "job_123"
        call_args = mock_client.post.call_args
        assert "image_url" in call_args[1]["data"]
        assert call_args[1]["data"]["image_url"].startswith("data:image/png;base64,")

    def test_queue_with_all_parameters(self, mock_client):
        """Test queue with all optional parameters."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "job_id": "job_123",
            "status": "queued"
        }
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        job = api.queue(
            model="kling-2.6-pro-text-to-video",
            prompt="Test prompt",
            duration=5,
            resolution="1080p",
            audio=True,
            seed=42,
            negative_prompt="blurry",
            aspect_ratio="16:9",
            fps=30,
            motion_bucket_id=127,
            guidance_scale=7.5,
            custom_param="value"
        )
        
        assert job.job_id == "job_123"
        call_args = mock_client.post.call_args
        data = call_args[1]["data"]
        assert data["audio"] is True
        assert data["seed"] == 42
        assert data["negative_prompt"] == "blurry"
        assert data["aspect_ratio"] == "16:9"
        assert data["fps"] == 30
        assert data["motion_bucket_id"] == 127
        assert data["guidance_scale"] == 7.5
        assert data["custom_param"] == "value"

    def test_queue_with_metadata(self, mock_client):
        """Test queue response with metadata."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "job_id": "job_123",
            "status": "queued",
            "metadata": {
                "duration": 5.0,
                "resolution": "1080p",
                "fps": 30,
                "format": "mp4",
                "file_size": 1024000
            }
        }
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        job = api.queue(
            model="kling-2.6-pro-text-to-video",
            prompt="Test"
        )
        
        assert job.metadata is not None
        assert job.metadata.duration == 5.0
        assert job.metadata.resolution == "1080p"

    def test_queue_no_prompt_or_image(self, mock_client):
        """Test queue without prompt or image."""
        api = VideoAPI(mock_client)
        
        with pytest.raises(VideoGenerationError, match="Either 'prompt' \\(for text-to-video\\) or 'image' \\(for image-to-video\\) must be provided"):
            api.queue(model="kling-2.6-pro-text-to-video")

    def test_queue_with_queue_id(self, mock_client):
        """Test queue when API returns queue_id instead of job_id."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "queue_id": "queue_123",
            "status": "queued",
            "created_at": "2024-01-01T00:00:00Z"
        }
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        job = api.queue(
            model="kling-2.6-pro-text-to-video",
            prompt="A beautiful sunset"
        )
        
        assert job.job_id == "queue_123"
        assert job.status == "queued"

    def test_queue_prefers_job_id_over_queue_id(self, mock_client):
        """Test queue prefers job_id when both are present."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "job_id": "job_123",
            "queue_id": "queue_123",
            "status": "queued"
        }
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        job = api.queue(
            model="kling-2.6-pro-text-to-video",
            prompt="Test"
        )
        
        assert job.job_id == "job_123"

    def test_queue_no_job_id(self, mock_client):
        """Test queue when no job_id is returned."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "queued"}
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        
        with pytest.raises(VideoGenerationError, match="No job_id returned from queue endpoint"):
            api.queue(model="kling-2.6-pro-text-to-video", prompt="Test")

    def test_queue_api_error(self, mock_client):
        """Test queue when API returns error."""
        mock_client.post.side_effect = VeniceAPIError("API Error", status_code=400)
        
        api = VideoAPI(mock_client)
        
        with pytest.raises(VeniceAPIError):
            api.queue(model="kling-2.6-pro-text-to-video", prompt="Test")

    def test_queue_generic_exception(self, mock_client):
        """Test queue when generic exception occurs."""
        mock_client.post.side_effect = Exception("Network error")
        
        api = VideoAPI(mock_client)
        
        with pytest.raises(VideoGenerationError, match="Failed to queue video generation"):
            api.queue(model="kling-2.6-pro-text-to-video", prompt="Test")

    def test_queue_with_parameter_validation_success(self, mock_client):
        """Test queue with parameter validation when parameters are valid."""
        # Mock quote response (validation succeeds)
        mock_quote_response = MagicMock()
        mock_quote_response.json.return_value = {
            "estimated_cost": 0.50,
            "currency": "USD"
        }
        
        # Mock queue response
        mock_queue_response = MagicMock()
        mock_queue_response.json.return_value = {
            "job_id": "job_123",
            "status": "queued"
        }
        
        # First call is quote (validation), second is queue
        mock_client.post.side_effect = [mock_quote_response, mock_queue_response]
        
        api = VideoAPI(mock_client)
        job = api.queue(
            model="kling-2.6-pro-text-to-video",
            prompt="Test",
            duration=5,
            aspect_ratio="16:9",
            validate_parameters=True
        )
        
        assert job.job_id == "job_123"
        assert mock_client.post.call_count == 2  # Quote + Queue

    def test_queue_with_parameter_validation_failure(self, mock_client):
        """Test queue with parameter validation when parameters are invalid."""
        # Mock quote response (validation fails with 400 error)
        from venice_sdk.errors import VeniceAPIError
        mock_client.post.side_effect = VeniceAPIError("Invalid parameters", status_code=400)
        
        api = VideoAPI(mock_client)
        
        with pytest.raises(VideoGenerationError, match="Invalid parameter combination"):
            api.queue(
                model="kling-2.6-pro-text-to-video",
                prompt="Test",
                duration=6,  # Invalid duration
                aspect_ratio="16:9",
                validate_parameters=True
            )

    def test_validate_with_quote_success(self, mock_client):
        """Test _validate_with_quote when parameters are valid."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "estimated_cost": 0.50,
            "currency": "USD"
        }
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        result = api._validate_with_quote(
            model="kling-2.6-pro-text-to-video",
            prompt="Test",
            duration=5,
            aspect_ratio="16:9"
        )
        
        assert result is True
        mock_client.post.assert_called_once()

    def test_validate_with_quote_failure(self, mock_client):
        """Test _validate_with_quote when parameters are invalid."""
        from venice_sdk.errors import VeniceAPIError
        mock_client.post.side_effect = VeniceAPIError("Invalid parameters", status_code=400)
        
        api = VideoAPI(mock_client)
        result = api._validate_with_quote(
            model="kling-2.6-pro-text-to-video",
            prompt="Test",
            duration=6,  # Invalid
            aspect_ratio="16:9"
        )
        
        assert result is False

    def test_get_valid_parameters(self, mock_client):
        """Test get_valid_parameters discovers valid combinations."""
        # Mock responses: some combinations valid, some invalid
        def mock_post_side_effect(*args, **kwargs):
            mock_response = MagicMock()
            data = kwargs.get("data", {})
            duration = data.get("duration")
            aspect_ratio = data.get("aspect_ratio", "16:9")
            
            # Simulate: 4s, 8s, 12s are valid; others invalid
            # 16:9, 9:16 are valid; others invalid
            if duration in ["4s", "8s", "12s"] and aspect_ratio in ["16:9", "9:16"]:
                mock_response.json.return_value = {"estimated_cost": 0.50, "currency": "USD"}
            else:
                from venice_sdk.errors import VeniceAPIError
                raise VeniceAPIError("Invalid", status_code=400)
            
            return mock_response
        
        mock_client.post.side_effect = mock_post_side_effect
        
        api = VideoAPI(mock_client)
        valid = api.get_valid_parameters(
            model="sora-2-text-to-video",
            prompt="Test"
        )
        
        assert "duration" in valid
        assert "aspect_ratio" in valid
        assert isinstance(valid["duration"], list)
        assert isinstance(valid["aspect_ratio"], list)

    def test_retrieve_success(self, mock_client):
        """Test successful video retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "job_id": "job_123",
            "status": "completed",
            "video_url": "https://example.com/video.mp4",
            "progress": 100.0,
            "created_at": "2024-01-01T00:00:00Z",
            "completed_at": "2024-01-01T00:00:10Z"
        }
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        job = api.retrieve("job_123")
        
        assert job.job_id == "job_123"
        assert job.status == "completed"
        assert job.video_url == "https://example.com/video.mp4"
        assert job.progress == 100.0
        mock_client.post.assert_called_once_with(
            VideoEndpoints.RETRIEVE,
            data={"queue_id": "job_123"}
        )

    def test_retrieve_with_metadata(self, mock_client):
        """Test retrieve with metadata."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "job_id": "job_123",
            "status": "completed",
            "metadata": {
                "duration": 5.0,
                "resolution": "1080p"
            }
        }
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        job = api.retrieve("job_123")
        
        assert job.metadata is not None
        assert job.metadata.duration == 5.0

    def test_retrieve_empty_job_id(self, mock_client):
        """Test retrieve with empty job_id."""
        api = VideoAPI(mock_client)
        
        with pytest.raises(VideoGenerationError, match="job_id is required"):
            api.retrieve("")

    def test_retrieve_api_error(self, mock_client):
        """Test retrieve when API returns error."""
        mock_client.post.side_effect = VeniceAPIError("API Error", status_code=404)
        
        api = VideoAPI(mock_client)
        
        with pytest.raises(VeniceAPIError):
            api.retrieve("job_123")

    def test_retrieve_generic_exception(self, mock_client):
        """Test retrieve when generic exception occurs."""
        mock_client.post.side_effect = Exception("Network error")
        
        api = VideoAPI(mock_client)
        
        with pytest.raises(VideoGenerationError, match="Failed to retrieve video job"):
            api.retrieve("job_123")

    def test_retrieve_binary_video_response(self, mock_client, tmp_path):
        """Test retrieve when API returns binary video file instead of JSON."""
        # Mock binary video response (MP4 file)
        mock_response = MagicMock()
        mock_response.headers = {'Content-Type': 'video/mp4'}
        # MP4 file signature: ftyp box
        mp4_data = b'\x00\x00\x00\x20ftypisom\x00\x00\x02\x00' + b'x' * 1000
        mock_response.content = mp4_data
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        job = api.retrieve("job_123")
        
        assert job.job_id == "job_123"
        assert job.status == "completed"
        assert job.video_file_path is not None
        assert Path(job.video_file_path).exists()
        assert Path(job.video_file_path).read_bytes() == mp4_data

    def test_retrieve_binary_video_response_octet_stream(self, mock_client):
        """Test retrieve when API returns binary with application/octet-stream content type."""
        mock_response = MagicMock()
        mock_response.headers = {'Content-Type': 'application/octet-stream'}
        mp4_data = b'\x00\x00\x00\x20ftypisom\x00\x00\x02\x00' + b'x' * 1000
        mock_response.content = mp4_data
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        job = api.retrieve("job_123")
        
        assert job.status == "completed"
        assert job.video_file_path is not None

    def test_retrieve_binary_video_fallback_detection(self, mock_client):
        """Test retrieve fallback detection when Content-Type is missing but content is MP4."""
        mock_response = MagicMock()
        mock_response.headers = {'Content-Type': 'application/json'}  # Wrong content type
        # MP4 file signature
        mp4_data = b'\x00\x00\x00\x20ftypisom\x00\x00\x02\x00' + b'x' * 2000
        mock_response.content = mp4_data
        # Make json() raise JSONDecodeError
        import json
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        job = api.retrieve("job_123")
        
        assert job.status == "completed"
        assert job.video_file_path is not None

    def test_video_job_download_from_file_path(self, tmp_path):
        """Test VideoJob.download() when video_file_path is set."""
        # Create a test video file
        video_file = tmp_path / "test_video.mp4"
        video_data = b"fake video data"
        video_file.write_bytes(video_data)
        
        job = VideoJob(
            job_id="job_123",
            status="completed",
            video_file_path=video_file
        )
        
        output_path = tmp_path / "output.mp4"
        result = job.download(output_path)
        
        assert result == output_path
        assert output_path.exists()
        assert output_path.read_bytes() == video_data

    def test_video_job_get_video_data_from_file_path(self, tmp_path):
        """Test VideoJob.get_video_data() when video_file_path is set."""
        video_file = tmp_path / "test_video.mp4"
        video_data = b"fake video data"
        video_file.write_bytes(video_data)
        
        job = VideoJob(
            job_id="job_123",
            status="completed",
            video_file_path=video_file
        )
        
        data = job.get_video_data()
        assert data == video_data

    @patch('venice_sdk.video.time.sleep')
    def test_wait_for_completion_success(self, mock_sleep, mock_client):
        """Test waiting for completion successfully."""
        # First call: processing, second call: completed
        mock_responses = [
            MagicMock(json=lambda: {"job_id": "job_123", "status": "processing", "progress": 50.0}),
            MagicMock(json=lambda: {"job_id": "job_123", "status": "completed", "video_url": "https://example.com/video.mp4"})
        ]
        mock_client.post.side_effect = mock_responses
        
        api = VideoAPI(mock_client)
        job = api.wait_for_completion("job_123", poll_interval=1)
        
        assert job.status == "completed"
        assert job.video_url == "https://example.com/video.mp4"
        assert mock_client.post.call_count == 2
        mock_sleep.assert_called_once_with(1)

    @patch('venice_sdk.video.time.sleep')
    def test_wait_for_completion_with_callback(self, mock_sleep, mock_client):
        """Test waiting for completion with callback."""
        callback_calls = []
        
        def callback(job):
            callback_calls.append(job.status)
        
        mock_responses = [
            MagicMock(json=lambda: {"job_id": "job_123", "status": "processing"}),
            MagicMock(json=lambda: {"job_id": "job_123", "status": "completed"})
        ]
        mock_client.post.side_effect = mock_responses
        
        api = VideoAPI(mock_client)
        job = api.wait_for_completion("job_123", poll_interval=1, callback=callback)
        
        assert len(callback_calls) == 2
        assert callback_calls[0] == "processing"
        assert callback_calls[1] == "completed"

    @patch('venice_sdk.video.time.sleep')
    def test_wait_for_completion_callback_exception(self, mock_sleep, mock_client):
        """Test wait_for_completion when callback raises exception."""
        def callback(job):
            raise ValueError("Callback error")
        
        mock_responses = [
            MagicMock(json=lambda: {"job_id": "job_123", "status": "processing"}),
            MagicMock(json=lambda: {"job_id": "job_123", "status": "completed"})
        ]
        mock_client.post.side_effect = mock_responses
        
        api = VideoAPI(mock_client)
        # Should not raise, just log warning
        job = api.wait_for_completion("job_123", poll_interval=1, callback=callback)
        assert job.status == "completed"

    @patch('venice_sdk.video.time.sleep')
    @patch('venice_sdk.video.time.time')
    def test_wait_for_completion_timeout(self, mock_time, mock_sleep, mock_client):
        """Test wait_for_completion with timeout."""
        mock_time.side_effect = [0, 600]  # Start at 0, check at 600 seconds
        mock_response = MagicMock()
        mock_response.json.return_value = {"job_id": "job_123", "status": "processing"}
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        
        with pytest.raises(VideoGenerationError, match="Timeout waiting for video generation"):
            api.wait_for_completion("job_123", poll_interval=1, max_wait_time=500)

    @patch('venice_sdk.video.time.sleep')
    def test_wait_for_completion_failed(self, mock_sleep, mock_client):
        """Test wait_for_completion when job fails."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "job_id": "job_123",
            "status": "failed",
            "error": "Generation failed"
        }
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        
        with pytest.raises(VideoGenerationError, match="Video generation failed: Generation failed"):
            api.wait_for_completion("job_123", poll_interval=1)

    @patch('venice_sdk.video.time.sleep')
    def test_wait_for_completion_failed_no_error_message(self, mock_sleep, mock_client):
        """Test wait_for_completion when job fails without error message."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"job_id": "job_123", "status": "failed"}
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        
        with pytest.raises(VideoGenerationError, match="Video generation failed: Unknown error"):
            api.wait_for_completion("job_123", poll_interval=1)

    def test_quote_text_to_video_success(self, mock_client):
        """Test successful text-to-video quote."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "estimated_cost": 0.50,
            "currency": "USD",
            "estimated_duration": 120,
            "pricing_breakdown": {"base": 0.30, "duration": 0.20}
        }
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        quote = api.quote(
            model="kling-2.6-pro-text-to-video",
            prompt="A beautiful sunset",
            duration=5,
            resolution="1080p"
        )
        
        assert quote.estimated_cost == 0.50
        assert quote.currency == "USD"
        assert quote.estimated_duration == 120
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == VideoEndpoints.QUOTE
        assert call_args[1]["data"]["model"] == "kling-2.6-pro-text-to-video"

    def test_quote_with_all_parameters(self, mock_client):
        """Test quote with all optional parameters."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "estimated_cost": 0.50,
            "currency": "USD"
        }
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        quote = api.quote(
            model="kling-2.6-pro-text-to-video",
            prompt="Test",
            duration=5,
            resolution="1080p",
            audio=True,
            seed=42,
            negative_prompt="blurry",
            aspect_ratio="16:9",
            fps=30,
            motion_bucket_id=127,
            guidance_scale=7.5
        )
        
        assert quote.estimated_cost == 0.50
        call_args = mock_client.post.call_args
        data = call_args[1]["data"]
        assert data["audio"] is True
        assert data["seed"] == 42

    def test_quote_no_prompt_or_image(self, mock_client):
        """Test quote without prompt or image."""
        api = VideoAPI(mock_client)
        
        with pytest.raises(VideoGenerationError, match="Either 'prompt' \\(for text-to-video\\) or 'image' \\(for image-to-video\\) must be provided"):
            api.quote(model="kling-2.6-pro-text-to-video")

    def test_quote_api_error(self, mock_client):
        """Test quote when API returns error."""
        mock_client.post.side_effect = VeniceAPIError("API Error", status_code=400)
        
        api = VideoAPI(mock_client)
        
        with pytest.raises(VeniceAPIError):
            api.quote(model="kling-2.6-pro-text-to-video", prompt="Test")

    def test_quote_generic_exception(self, mock_client):
        """Test quote when generic exception occurs."""
        mock_client.post.side_effect = Exception("Network error")
        
        api = VideoAPI(mock_client)
        
        with pytest.raises(VideoGenerationError, match="Failed to get video quote"):
            api.quote(model="kling-2.6-pro-text-to-video", prompt="Test")

    @patch('venice_sdk.video.VideoAPI.wait_for_completion')
    @patch('venice_sdk.video.VideoAPI.queue')
    def test_complete_success(self, mock_queue, mock_wait, mock_client):
        """Test successful complete (synchronous generation)."""
        queued_job = VideoJob(job_id="job_123", status="queued")
        completed_job = VideoJob(
            job_id="job_123",
            status="completed",
            video_url="https://example.com/video.mp4"
        )
        
        mock_queue.return_value = queued_job
        mock_wait.return_value = completed_job
        
        api = VideoAPI(mock_client)
        result = api.complete(
            model="kling-2.6-pro-text-to-video",
            prompt="Test prompt",
            duration=5,
            timeout=900
        )
        
        assert result.status == "completed"
        mock_queue.assert_called_once()
        mock_wait.assert_called_once_with("job_123", max_wait_time=900)

    @patch('venice_sdk.video.VideoAPI.wait_for_completion')
    @patch('venice_sdk.video.VideoAPI.queue')
    def test_complete_with_all_parameters(self, mock_queue, mock_wait, mock_client):
        """Test complete with all parameters."""
        queued_job = VideoJob(job_id="job_123", status="queued")
        completed_job = VideoJob(job_id="job_123", status="completed")
        
        mock_queue.return_value = queued_job
        mock_wait.return_value = completed_job
        
        api = VideoAPI(mock_client)
        result = api.complete(
            model="kling-2.6-pro-text-to-video",
            prompt="Test",
            duration=5,
            resolution="1080p",
            audio=True,
            seed=42,
            timeout=600
        )
        
        assert result.status == "completed"
        # Verify all parameters passed to queue
        queue_call = mock_queue.call_args
        assert queue_call[1]["model"] == "kling-2.6-pro-text-to-video"
        assert queue_call[1]["prompt"] == "Test"
        assert queue_call[1]["duration"] == 5
        assert queue_call[1]["audio"] is True
        assert queue_call[1]["seed"] == 42

    @patch('venice_sdk.video.VideoAPI.queue')
    def test_complete_queue_fails(self, mock_queue, mock_client):
        """Test complete when queue fails."""
        mock_queue.side_effect = VideoGenerationError("Queue failed")
        
        api = VideoAPI(mock_client)
        
        with pytest.raises(VideoGenerationError, match="Queue failed"):
            api.complete(model="kling-2.6-pro-text-to-video", prompt="Test")

    @patch('venice_sdk.video.VideoAPI.wait_for_completion')
    @patch('venice_sdk.video.VideoAPI.queue')
    def test_complete_wait_fails(self, mock_queue, mock_wait, mock_client):
        """Test complete when wait_for_completion fails."""
        queued_job = VideoJob(job_id="job_123", status="queued")
        mock_queue.return_value = queued_job
        mock_wait.side_effect = VideoGenerationError("Wait failed")
        
        api = VideoAPI(mock_client)
        
        with pytest.raises(VideoGenerationError, match="Wait failed"):
            api.complete(model="kling-2.6-pro-text-to-video", prompt="Test")

    @patch('venice_sdk.video.time.sleep')
    def test_wait_for_completion_no_timeout(self, mock_sleep, mock_client):
        """Test wait_for_completion without timeout."""
        mock_responses = [
            MagicMock(json=lambda: {"job_id": "job_123", "status": "processing"}),
            MagicMock(json=lambda: {"job_id": "job_123", "status": "completed"})
        ]
        mock_client.post.side_effect = mock_responses
        
        api = VideoAPI(mock_client)
        job = api.wait_for_completion("job_123", poll_interval=1, max_wait_time=None)
        
        assert job.status == "completed"

    def test_queue_with_partial_metadata(self, mock_client):
        """Test queue response with partial metadata."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "job_id": "job_123",
            "status": "queued",
            "metadata": {
                "duration": 5.0
                # Missing other fields
            }
        }
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        job = api.queue(
            model="kling-2.6-pro-text-to-video",
            prompt="Test"
        )
        
        assert job.metadata is not None
        assert job.metadata.duration == 5.0
        assert job.metadata.resolution is None

    def test_retrieve_with_partial_metadata(self, mock_client):
        """Test retrieve with partial metadata."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "job_id": "job_123",
            "status": "completed",
            "metadata": {
                "fps": 30
                # Missing other fields
            }
        }
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        job = api.retrieve("job_123")
        
        assert job.metadata is not None
        assert job.metadata.fps == 30
        assert job.metadata.duration is None

    def test_retrieve_without_metadata(self, mock_client):
        """Test retrieve without metadata field."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "job_id": "job_123",
            "status": "completed"
        }
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        job = api.retrieve("job_123")
        
        assert job.metadata is None

    def test_queue_without_metadata(self, mock_client):
        """Test queue response without metadata."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "job_id": "job_123",
            "status": "queued"
        }
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        job = api.queue(
            model="kling-2.6-pro-text-to-video",
            prompt="Test"
        )
        
        assert job.metadata is None

    def test_complete_default_timeout(self, mock_client):
        """Test complete with default timeout."""
        with patch('venice_sdk.video.VideoAPI.wait_for_completion') as mock_wait, \
             patch('venice_sdk.video.VideoAPI.queue') as mock_queue:
            queued_job = VideoJob(job_id="job_123", status="queued")
            completed_job = VideoJob(job_id="job_123", status="completed")
            
            mock_queue.return_value = queued_job
            mock_wait.return_value = completed_job
            
            api = VideoAPI(mock_client)
            result = api.complete(
                model="kling-2.6-pro-text-to-video",
                prompt="Test"
            )
            
            assert result.status == "completed"
            # Should use default timeout of 900
            mock_wait.assert_called_once_with("job_123", max_wait_time=900)

    def test_download_data_uri(self, tmp_path):
        """Test download from data URI (should not happen but test edge case)."""
        job = VideoJob(
            job_id="job_123",
            status="completed",
            video_url="data:video/mp4;base64,ZGF0YQ=="
        )
        
        output_path = tmp_path / "video.mp4"
        # Data URIs can't be downloaded with requests.get, so this should raise an error
        with pytest.raises(VideoGenerationError, match="Failed to download video"):
            job.download(output_path)

    def test_get_video_data_data_uri(self):
        """Test get_video_data from data URI."""
        job = VideoJob(
            job_id="job_123",
            status="completed",
            video_url="data:video/mp4;base64,ZGF0YQ=="
        )
        
        with patch('venice_sdk.video.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"data"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            data = job.get_video_data()
            assert data == b"data"

    def test_wait_for_completion_immediate_completion(self, mock_client):
        """Test wait_for_completion when job is already completed."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "job_id": "job_123",
            "status": "completed",
            "video_url": "https://example.com/video.mp4"
        }
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        job = api.wait_for_completion("job_123", poll_interval=1)
        
        assert job.status == "completed"
        assert mock_client.post.call_count == 1  # Should only call once

    def test_wait_for_completion_multiple_polls(self, mock_client):
        """Test wait_for_completion with multiple polling cycles."""
        with patch('venice_sdk.video.time.sleep') as mock_sleep:
            mock_responses = [
                MagicMock(json=lambda: {"job_id": "job_123", "status": "queued"}),
                MagicMock(json=lambda: {"job_id": "job_123", "status": "processing", "progress": 25.0}),
                MagicMock(json=lambda: {"job_id": "job_123", "status": "processing", "progress": 75.0}),
                MagicMock(json=lambda: {"job_id": "job_123", "status": "completed", "video_url": "https://example.com/video.mp4"})
            ]
            mock_client.post.side_effect = mock_responses
            
            api = VideoAPI(mock_client)
            job = api.wait_for_completion("job_123", poll_interval=1)
            
            assert job.status == "completed"
            assert mock_client.post.call_count == 4
            assert mock_sleep.call_count == 3  # Should sleep 3 times (between 4 calls)

    def test_quote_with_image(self, mock_client, tmp_path):
        """Test quote with image parameter."""
        image_path = tmp_path / "test.png"
        image_path.write_bytes(b"fake image")
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "estimated_cost": 0.50,
            "currency": "USD"
        }
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        quote = api.quote(
            model="kling-2.6-pro-image-to-video",
            image=image_path,
            prompt="Animate this"
        )
        
        assert quote.estimated_cost == 0.50
        call_args = mock_client.post.call_args
        assert "image_url" in call_args[1]["data"]
        assert call_args[1]["data"]["image_url"].startswith("data:image/png;base64,")

    def test_quote_with_image_url(self, mock_client):
        """Test quote with image URL."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "estimated_cost": 0.50,
            "currency": "USD"
        }
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        quote = api.quote(
            model="kling-2.6-pro-image-to-video",
            image="https://example.com/image.png",
            prompt="Animate this"
        )
        
        assert quote.estimated_cost == 0.50
        call_args = mock_client.post.call_args
        assert call_args[1]["data"]["image_url"] == "https://example.com/image.png"

    def test_quote_with_image_bytes(self, mock_client):
        """Test quote with image bytes."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "estimated_cost": 0.50,
            "currency": "USD"
        }
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        quote = api.quote(
            model="kling-2.6-pro-image-to-video",
            image=b"fake image data",
            prompt="Animate this"
        )
        
        assert quote.estimated_cost == 0.50
        call_args = mock_client.post.call_args
        assert call_args[1]["data"]["image_url"].startswith("data:image/png;base64,")

    def test_queue_with_image_bytes(self, mock_client):
        """Test queue with image bytes."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "job_id": "job_123",
            "status": "queued"
        }
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        job = api.queue(
            model="kling-2.6-pro-image-to-video",
            image=b"fake image data",
            prompt="Animate this"
        )
        
        assert job.job_id == "job_123"
        call_args = mock_client.post.call_args
        assert call_args[1]["data"]["image_url"].startswith("data:image/png;base64,")

    def test_queue_with_image_url(self, mock_client):
        """Test queue with image URL."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "job_id": "job_123",
            "status": "queued"
        }
        mock_client.post.return_value = mock_response
        
        api = VideoAPI(mock_client)
        job = api.queue(
            model="kling-2.6-pro-image-to-video",
            image="https://example.com/image.png",
            prompt="Animate this"
        )
        
        assert job.job_id == "job_123"
        call_args = mock_client.post.call_args
        assert call_args[1]["data"]["image_url"] == "https://example.com/image.png"

    def test_complete_with_image(self, mock_client, tmp_path):
        """Test complete with image parameter."""
        image_path = tmp_path / "test.png"
        image_path.write_bytes(b"fake image")
        
        with patch('venice_sdk.video.VideoAPI.wait_for_completion') as mock_wait, \
             patch('venice_sdk.video.VideoAPI.queue') as mock_queue:
            queued_job = VideoJob(job_id="job_123", status="queued")
            completed_job = VideoJob(job_id="job_123", status="completed")
            
            mock_queue.return_value = queued_job
            mock_wait.return_value = completed_job
            
            api = VideoAPI(mock_client)
            result = api.complete(
                model="kling-2.6-pro-image-to-video",
                image=image_path,
                prompt="Animate this"
            )
            
            assert result.status == "completed"
            queue_call = mock_queue.call_args
            assert "image" in queue_call[1]
            assert queue_call[1]["image"] == image_path

