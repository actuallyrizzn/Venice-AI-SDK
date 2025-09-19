"""
Comprehensive unit tests for the images module.
"""

import pytest
import base64
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from venice_sdk.images import (
    ImageGeneration, ImageEditResult, ImageUpscaleResult, ImageStyle,
    ImageAPI, ImageEditAPI, ImageUpscaleAPI, ImageStylesAPI,
    generate_image, edit_image, upscale_image
)
from venice_sdk.errors import VeniceAPIError, ImageGenerationError


class TestImageGenerationComprehensive:
    """Comprehensive test suite for ImageGeneration class."""

    def test_image_generation_initialization(self):
        """Test ImageGeneration initialization with all parameters."""
        image_gen = ImageGeneration(
            url="https://example.com/image.png",
            b64_json="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            revised_prompt="A beautiful sunset over mountains",
            created=1234567890
        )
        
        assert image_gen.url == "https://example.com/image.png"
        assert image_gen.b64_json == "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        assert image_gen.revised_prompt == "A beautiful sunset over mountains"
        assert image_gen.created == 1234567890

    def test_image_generation_initialization_with_defaults(self):
        """Test ImageGeneration initialization with default values."""
        image_gen = ImageGeneration()
        
        assert image_gen.url is None
        assert image_gen.b64_json is None
        assert image_gen.revised_prompt is None
        assert image_gen.created is None

    def test_save_from_url(self, tmp_path):
        """Test saving image from URL."""
        image_gen = ImageGeneration(url="https://example.com/image.png")
        
        with patch('venice_sdk.images.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"fake image data"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            output_path = tmp_path / "image.png"
            saved_path = image_gen.save(output_path)
            
            assert saved_path == output_path
            assert output_path.exists()
            assert output_path.read_bytes() == b"fake image data"

    def test_save_from_b64_json(self, tmp_path):
        """Test saving image from base64 JSON."""
        # Create a simple 1x1 PNG in base64
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
        b64_data = base64.b64encode(png_data).decode('utf-8')
        
        image_gen = ImageGeneration(b64_json=b64_data)
        
        output_path = tmp_path / "image.png"
        saved_path = image_gen.save(output_path)
        
        assert saved_path == output_path
        assert output_path.exists()
        assert output_path.read_bytes() == png_data

    def test_save_with_string_path(self, tmp_path):
        """Test saving image with string path."""
        image_gen = ImageGeneration(b64_json="dGVzdA==")  # "test" in base64
        
        output_path = str(tmp_path / "image.png")
        saved_path = image_gen.save(output_path)
        
        assert isinstance(saved_path, Path)
        assert saved_path.exists()

    def test_save_no_data_available(self):
        """Test saving image when no data is available."""
        image_gen = ImageGeneration()
        
        with pytest.raises(ImageGenerationError, match="No image data available to save"):
            image_gen.save("test.png")

    def test_get_image_data_from_url(self):
        """Test getting image data from URL."""
        image_gen = ImageGeneration(url="https://example.com/image.png")
        
        with patch('venice_sdk.images.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"fake image data"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            data = image_gen.get_image_data()
            
            assert data == b"fake image data"

    def test_get_image_data_from_b64_json(self):
        """Test getting image data from base64 JSON."""
        test_data = b"test image data"
        b64_data = base64.b64encode(test_data).decode('utf-8')
        
        image_gen = ImageGeneration(b64_json=b64_data)
        data = image_gen.get_image_data()
        
        assert data == test_data

    def test_get_image_data_no_data_available(self):
        """Test getting image data when no data is available."""
        image_gen = ImageGeneration()
        
        with pytest.raises(ImageGenerationError, match="No image data available"):
            image_gen.get_image_data()

    def test_equality(self):
        """Test ImageGeneration equality comparison."""
        img1 = ImageGeneration(url="https://example.com/image.png", created=123)
        img2 = ImageGeneration(url="https://example.com/image.png", created=123)
        img3 = ImageGeneration(url="https://example.com/other.png", created=123)
        
        assert img1 == img2
        assert img1 != img3

    def test_string_representation(self):
        """Test ImageGeneration string representation."""
        image_gen = ImageGeneration(url="https://example.com/image.png")
        img_str = str(image_gen)
        
        assert "ImageGeneration" in img_str


class TestImageEditResultComprehensive:
    """Comprehensive test suite for ImageEditResult class."""

    def test_image_edit_result_initialization(self):
        """Test ImageEditResult initialization."""
        edit_result = ImageEditResult(
            url="https://example.com/edited.png",
            b64_json="dGVzdA==",
            revised_prompt="Edited image",
            created=1234567890
        )
        
        assert edit_result.url == "https://example.com/edited.png"
        assert edit_result.b64_json == "dGVzdA=="
        assert edit_result.revised_prompt == "Edited image"
        assert edit_result.created == 1234567890

    def test_save_from_url(self, tmp_path):
        """Test saving edited image from URL."""
        edit_result = ImageEditResult(url="https://example.com/edited.png")
        
        with patch('venice_sdk.images.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"edited image data"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            output_path = tmp_path / "edited.png"
            saved_path = edit_result.save(output_path)
            
            assert saved_path == output_path
            assert output_path.exists()
            assert output_path.read_bytes() == b"edited image data"

    def test_save_from_b64_json(self, tmp_path):
        """Test saving edited image from base64 JSON."""
        test_data = b"edited image data"
        b64_data = base64.b64encode(test_data).decode('utf-8')
        
        edit_result = ImageEditResult(b64_json=b64_data)
        
        output_path = tmp_path / "edited.png"
        saved_path = edit_result.save(output_path)
        
        assert saved_path == output_path
        assert output_path.exists()
        assert output_path.read_bytes() == test_data

    def test_save_no_data_available(self):
        """Test saving edited image when no data is available."""
        edit_result = ImageEditResult()
        
        with pytest.raises(ImageGenerationError, match="No image data available to save"):
            edit_result.save("test.png")


class TestImageUpscaleResultComprehensive:
    """Comprehensive test suite for ImageUpscaleResult class."""

    def test_image_upscale_result_initialization(self):
        """Test ImageUpscaleResult initialization."""
        upscale_result = ImageUpscaleResult(
            url="https://example.com/upscaled.png",
            b64_json="dGVzdA==",
            created=1234567890
        )
        
        assert upscale_result.url == "https://example.com/upscaled.png"
        assert upscale_result.b64_json == "dGVzdA=="
        assert upscale_result.created == 1234567890

    def test_save_from_url(self, tmp_path):
        """Test saving upscaled image from URL."""
        upscale_result = ImageUpscaleResult(url="https://example.com/upscaled.png")
        
        with patch('venice_sdk.images.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"upscaled image data"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            output_path = tmp_path / "upscaled.png"
            saved_path = upscale_result.save(output_path)
            
            assert saved_path == output_path
            assert output_path.exists()
            assert output_path.read_bytes() == b"upscaled image data"

    def test_save_from_b64_json(self, tmp_path):
        """Test saving upscaled image from base64 JSON."""
        test_data = b"upscaled image data"
        b64_data = base64.b64encode(test_data).decode('utf-8')
        
        upscale_result = ImageUpscaleResult(b64_json=b64_data)
        
        output_path = tmp_path / "upscaled.png"
        saved_path = upscale_result.save(output_path)
        
        assert saved_path == output_path
        assert output_path.exists()
        assert output_path.read_bytes() == test_data

    def test_save_no_data_available(self):
        """Test saving upscaled image when no data is available."""
        upscale_result = ImageUpscaleResult()
        
        with pytest.raises(ImageGenerationError, match="No image data available to save"):
            upscale_result.save("test.png")


class TestImageStyleComprehensive:
    """Comprehensive test suite for ImageStyle class."""

    def test_image_style_initialization(self):
        """Test ImageStyle initialization with all parameters."""
        style = ImageStyle(
            id="style-123",
            name="Abstract Art",
            description="A modern abstract art style",
            category="artistic",
            preview_url="https://example.com/preview.png"
        )
        
        assert style.id == "style-123"
        assert style.name == "Abstract Art"
        assert style.description == "A modern abstract art style"
        assert style.category == "artistic"
        assert style.preview_url == "https://example.com/preview.png"

    def test_image_style_initialization_with_defaults(self):
        """Test ImageStyle initialization with default values."""
        style = ImageStyle(
            id="style-123",
            name="Abstract Art",
            description="A modern abstract art style"
        )
        
        assert style.id == "style-123"
        assert style.name == "Abstract Art"
        assert style.description == "A modern abstract art style"
        assert style.category is None
        assert style.preview_url is None

    def test_equality(self):
        """Test ImageStyle equality comparison."""
        style1 = ImageStyle("style-123", "Abstract Art", "Description")
        style2 = ImageStyle("style-123", "Abstract Art", "Description")
        style3 = ImageStyle("style-456", "Abstract Art", "Description")
        
        assert style1 == style2
        assert style1 != style3

    def test_string_representation(self):
        """Test ImageStyle string representation."""
        style = ImageStyle("style-123", "Abstract Art", "Description")
        style_str = str(style)
        
        assert "ImageStyle" in style_str


class TestImageAPIComprehensive:
    """Comprehensive test suite for ImageAPI class."""

    def test_image_api_initialization(self, mock_client):
        """Test ImageAPI initialization."""
        api = ImageAPI(mock_client)
        assert api.client == mock_client

    def test_generate_single_image(self, mock_client):
        """Test generating a single image."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "url": "https://example.com/image.png",
                    "b64_json": None,
                    "revised_prompt": "A beautiful sunset",
                    "created": 1234567890
                }
            ],
            "created": 1234567890
        }
        mock_client.post.return_value = mock_response
        
        api = ImageAPI(mock_client)
        result = api.generate("A beautiful sunset")
        
        assert isinstance(result, ImageGeneration)
        assert result.url == "https://example.com/image.png"
        assert result.revised_prompt == "A beautiful sunset"
        assert result.created == 1234567890

    def test_generate_multiple_images(self, mock_client):
        """Test generating multiple images."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "url": "https://example.com/image1.png",
                    "b64_json": None,
                    "revised_prompt": "A beautiful sunset",
                    "created": 1234567890
                },
                {
                    "url": "https://example.com/image2.png",
                    "b64_json": None,
                    "revised_prompt": "A beautiful sunset",
                    "created": 1234567890
                }
            ],
            "created": 1234567890
        }
        mock_client.post.return_value = mock_response
        
        api = ImageAPI(mock_client)
        result = api.generate("A beautiful sunset", n=2)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(img, ImageGeneration) for img in result)

    def test_generate_with_all_parameters(self, mock_client):
        """Test generating images with all parameters."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"url": "https://example.com/image.png", "b64_json": None, "revised_prompt": "A beautiful sunset", "created": 1234567890}],
            "created": 1234567890
        }
        mock_client.post.return_value = mock_response
        
        api = ImageAPI(mock_client)
        result = api.generate(
            prompt="A beautiful sunset",
            model="dall-e-3",
            n=1,
            size="1024x1024",
            quality="hd",
            style="abstract",
            response_format="url",
            user="test-user",
            custom_param="value"
        )
        
        mock_client.post.assert_called_once_with("/image/generate", data={
            "model": "dall-e-3",
            "prompt": "A beautiful sunset",
            "n": 1,
            "size": "1024x1024",
            "quality": "hd",
            "style": "abstract",
            "response_format": "url",
            "user": "test-user",
            "custom_param": "value"
        })

    def test_generate_with_b64_json_response(self, mock_client):
        """Test generating images with base64 JSON response."""
        test_data = b"fake image data"
        b64_data = base64.b64encode(test_data).decode('utf-8')
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "url": None,
                    "b64_json": b64_data,
                    "revised_prompt": "A beautiful sunset",
                    "created": 1234567890
                }
            ],
            "created": 1234567890
        }
        mock_client.post.return_value = mock_response
        
        api = ImageAPI(mock_client)
        result = api.generate("A beautiful sunset", response_format="b64_json")
        
        assert isinstance(result, ImageGeneration)
        assert result.b64_json == b64_data
        assert result.url is None

    def test_generate_invalid_response(self, mock_client):
        """Test generating images with invalid response format."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"invalid": "data"}
        mock_client.post.return_value = mock_response
        
        api = ImageAPI(mock_client)
        
        with pytest.raises(ImageGenerationError, match="Invalid response format from image generation API"):
            api.generate("A beautiful sunset")

    def test_generate_batch(self, mock_client):
        """Test generating images for multiple prompts."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"url": "https://example.com/image.png", "b64_json": None, "revised_prompt": "A beautiful sunset", "created": 1234567890}],
            "created": 1234567890
        }
        mock_client.post.return_value = mock_response
        
        api = ImageAPI(mock_client)
        prompts = ["A beautiful sunset", "A mountain landscape", "A city skyline"]
        results = api.generate_batch(prompts)
        
        assert len(results) == 3
        assert all(isinstance(img, ImageGeneration) for img in results)
        assert mock_client.post.call_count == 3

    def test_generate_batch_with_parameters(self, mock_client):
        """Test generating images for multiple prompts with parameters."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"url": "https://example.com/image.png", "b64_json": None, "revised_prompt": "A beautiful sunset", "created": 1234567890}],
            "created": 1234567890
        }
        mock_client.post.return_value = mock_response
        
        api = ImageAPI(mock_client)
        prompts = ["A beautiful sunset", "A mountain landscape"]
        results = api.generate_batch(
            prompts,
            model="dall-e-3",
            size="512x512",
            quality="standard",
            style="realistic",
            response_format="url"
        )
        
        assert len(results) == 2
        # Verify all calls used the same parameters
        for call in mock_client.post.call_args_list:
            assert call[1]["data"]["model"] == "dall-e-3"
            assert call[1]["data"]["size"] == "512x512"
            assert call[1]["data"]["quality"] == "standard"
            assert call[1]["data"]["style"] == "realistic"
            assert call[1]["data"]["response_format"] == "url"


class TestImageEditAPIComprehensive:
    """Comprehensive test suite for ImageEditAPI class."""

    def test_image_edit_api_initialization(self, mock_client):
        """Test ImageEditAPI initialization."""
        api = ImageEditAPI(mock_client)
        assert api.client == mock_client

    def test_encode_image_from_string_path(self, mock_client, tmp_path):
        """Test encoding image from string path."""
        test_data = b"fake image data"
        image_path = tmp_path / "test.png"
        image_path.write_bytes(test_data)
        
        api = ImageEditAPI(mock_client)
        encoded = api._encode_image(str(image_path))
        
        expected = base64.b64encode(test_data).decode('utf-8')
        assert encoded == expected

    def test_encode_image_from_path_object(self, mock_client, tmp_path):
        """Test encoding image from Path object."""
        test_data = b"fake image data"
        image_path = tmp_path / "test.png"
        image_path.write_bytes(test_data)
        
        api = ImageEditAPI(mock_client)
        encoded = api._encode_image(image_path)
        
        expected = base64.b64encode(test_data).decode('utf-8')
        assert encoded == expected

    def test_encode_image_from_bytes(self, mock_client):
        """Test encoding image from bytes."""
        test_data = b"fake image data"
        
        api = ImageEditAPI(mock_client)
        encoded = api._encode_image(test_data)
        
        expected = base64.b64encode(test_data).decode('utf-8')
        assert encoded == expected

    def test_encode_image_from_url(self, mock_client):
        """Test encoding image from URL."""
        test_data = b"fake image data"
        
        with patch('venice_sdk.images.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.content = test_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            api = ImageEditAPI(mock_client)
            encoded = api._encode_image("https://example.com/image.png")
            
            expected = base64.b64encode(test_data).decode('utf-8')
            assert encoded == expected

    def test_encode_image_invalid_type(self, mock_client):
        """Test encoding image with invalid type."""
        api = ImageEditAPI(mock_client)
        
        with pytest.raises(ValueError, match="Invalid image type. Expected str, bytes, or Path"):
            api._encode_image(123)

    def test_edit_single_image(self, mock_client, tmp_path):
        """Test editing a single image."""
        test_data = b"fake image data"
        image_path = tmp_path / "test.png"
        image_path.write_bytes(test_data)
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "url": "https://example.com/edited.png",
                    "b64_json": None,
                    "revised_prompt": "Edited image",
                    "created": 1234567890
                }
            ],
            "created": 1234567890
        }
        mock_client.post.return_value = mock_response
        
        api = ImageEditAPI(mock_client)
        result = api.edit(image_path, "Make it more colorful")
        
        assert isinstance(result, ImageEditResult)
        assert result.url == "https://example.com/edited.png"
        assert result.revised_prompt == "Edited image"

    def test_edit_multiple_images(self, mock_client, tmp_path):
        """Test editing multiple images."""
        test_data = b"fake image data"
        image_path = tmp_path / "test.png"
        image_path.write_bytes(test_data)
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "url": "https://example.com/edited1.png",
                    "b64_json": None,
                    "revised_prompt": "Edited image 1",
                    "created": 1234567890
                },
                {
                    "url": "https://example.com/edited2.png",
                    "b64_json": None,
                    "revised_prompt": "Edited image 2",
                    "created": 1234567890
                }
            ],
            "created": 1234567890
        }
        mock_client.post.return_value = mock_response
        
        api = ImageEditAPI(mock_client)
        result = api.edit(image_path, "Make it more colorful", n=2)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(img, ImageEditResult) for img in result)

    def test_edit_with_mask(self, mock_client, tmp_path):
        """Test editing image with mask."""
        test_data = b"fake image data"
        mask_data = b"fake mask data"
        image_path = tmp_path / "test.png"
        mask_path = tmp_path / "mask.png"
        image_path.write_bytes(test_data)
        mask_path.write_bytes(mask_data)
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"url": "https://example.com/edited.png", "b64_json": None, "revised_prompt": "Edited image", "created": 1234567890}],
            "created": 1234567890
        }
        mock_client.post.return_value = mock_response
        
        api = ImageEditAPI(mock_client)
        result = api.edit(image_path, "Make it more colorful", mask=mask_path)
        
        assert isinstance(result, ImageEditResult)
        # Verify mask was included in the request
        call_args = mock_client.post.call_args
        assert "mask" in call_args[1]["data"]

    def test_edit_with_all_parameters(self, mock_client, tmp_path):
        """Test editing image with all parameters."""
        test_data = b"fake image data"
        image_path = tmp_path / "test.png"
        image_path.write_bytes(test_data)
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"url": "https://example.com/edited.png", "b64_json": None, "revised_prompt": "Edited image", "created": 1234567890}],
            "created": 1234567890
        }
        mock_client.post.return_value = mock_response
        
        api = ImageEditAPI(mock_client)
        result = api.edit(
            image_path,
            "Make it more colorful",
            model="dall-e-2-edit",
            n=1,
            size="1024x1024",
            response_format="url",
            user="test-user",
            custom_param="value"
        )
        
        call_args = mock_client.post.call_args
        assert call_args[1]["data"]["model"] == "dall-e-2-edit"
        assert call_args[1]["data"]["size"] == "1024x1024"
        assert call_args[1]["data"]["response_format"] == "url"
        assert call_args[1]["data"]["user"] == "test-user"
        assert call_args[1]["data"]["custom_param"] == "value"

    def test_edit_invalid_response(self, mock_client, tmp_path):
        """Test editing image with invalid response format."""
        test_data = b"fake image data"
        image_path = tmp_path / "test.png"
        image_path.write_bytes(test_data)
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"invalid": "data"}
        mock_client.post.return_value = mock_response
        
        api = ImageEditAPI(mock_client)
        
        with pytest.raises(ImageGenerationError, match="Invalid response format from image edit API"):
            api.edit(image_path, "Make it more colorful")


class TestImageUpscaleAPIComprehensive:
    """Comprehensive test suite for ImageUpscaleAPI class."""

    def test_image_upscale_api_initialization(self, mock_client):
        """Test ImageUpscaleAPI initialization."""
        api = ImageUpscaleAPI(mock_client)
        assert api.client == mock_client

    def test_upscale_image(self, mock_client, tmp_path):
        """Test upscaling an image."""
        test_data = b"fake image data"
        image_path = tmp_path / "test.png"
        image_path.write_bytes(test_data)
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "url": "https://example.com/upscaled.png",
                    "b64_json": None,
                    "created": 1234567890
                }
            ],
            "created": 1234567890
        }
        mock_client.post.return_value = mock_response
        
        api = ImageUpscaleAPI(mock_client)
        result = api.upscale(image_path)
        
        assert isinstance(result, ImageUpscaleResult)
        assert result.url == "https://example.com/upscaled.png"
        assert result.created == 1234567890

    def test_upscale_with_all_parameters(self, mock_client, tmp_path):
        """Test upscaling image with all parameters."""
        test_data = b"fake image data"
        image_path = tmp_path / "test.png"
        image_path.write_bytes(test_data)
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"url": "https://example.com/upscaled.png", "b64_json": None, "created": 1234567890}],
            "created": 1234567890
        }
        mock_client.post.return_value = mock_response
        
        api = ImageUpscaleAPI(mock_client)
        result = api.upscale(
            image_path,
            model="upscaler-v2",
            scale=4,
            response_format="b64_json",
            custom_param="value"
        )
        
        call_args = mock_client.post.call_args
        assert call_args[1]["data"]["model"] == "upscaler-v2"
        assert call_args[1]["data"]["scale"] == 4
        assert call_args[1]["data"]["response_format"] == "b64_json"
        assert call_args[1]["data"]["custom_param"] == "value"

    def test_upscale_invalid_response(self, mock_client, tmp_path):
        """Test upscaling image with invalid response format."""
        test_data = b"fake image data"
        image_path = tmp_path / "test.png"
        image_path.write_bytes(test_data)
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"invalid": "data"}
        mock_client.post.return_value = mock_response
        
        api = ImageUpscaleAPI(mock_client)
        
        with pytest.raises(ImageGenerationError, match="Invalid response format from image upscale API"):
            api.upscale(image_path)

    def test_upscale_empty_data(self, mock_client, tmp_path):
        """Test upscaling image with empty data response."""
        test_data = b"fake image data"
        image_path = tmp_path / "test.png"
        image_path.write_bytes(test_data)
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_client.post.return_value = mock_response
        
        api = ImageUpscaleAPI(mock_client)
        
        with pytest.raises(ImageGenerationError, match="Invalid response format from image upscale API"):
            api.upscale(image_path)


class TestImageStylesAPIComprehensive:
    """Comprehensive test suite for ImageStylesAPI class."""

    def test_image_styles_api_initialization(self, mock_client):
        """Test ImageStylesAPI initialization."""
        api = ImageStylesAPI(mock_client)
        assert api.client == mock_client

    def test_list_styles_success(self, mock_client):
        """Test successful styles listing."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "style-1",
                    "name": "Abstract Art",
                    "description": "Modern abstract art style",
                    "category": "artistic",
                    "preview_url": "https://example.com/preview1.png"
                },
                {
                    "id": "style-2",
                    "name": "Realistic",
                    "description": "Photorealistic style",
                    "category": "realistic",
                    "preview_url": "https://example.com/preview2.png"
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        api = ImageStylesAPI(mock_client)
        styles = api.list_styles()
        
        assert len(styles) == 2
        assert all(isinstance(style, ImageStyle) for style in styles)
        assert styles[0].id == "style-1"
        assert styles[0].name == "Abstract Art"
        assert styles[1].id == "style-2"
        assert styles[1].name == "Realistic"

    def test_list_styles_invalid_response(self, mock_client):
        """Test styles listing with invalid response format."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"invalid": "data"}
        mock_client.get.return_value = mock_response
        
        api = ImageStylesAPI(mock_client)
        
        with pytest.raises(ImageGenerationError, match="Invalid response format from image styles API"):
            api.list_styles()

    def test_get_style_success(self, mock_client):
        """Test getting a specific style by ID."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "style-1",
                    "name": "Abstract Art",
                    "description": "Modern abstract art style",
                    "category": "artistic",
                    "preview_url": "https://example.com/preview1.png"
                },
                {
                    "id": "style-2",
                    "name": "Realistic",
                    "description": "Photorealistic style",
                    "category": "realistic",
                    "preview_url": "https://example.com/preview2.png"
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        api = ImageStylesAPI(mock_client)
        style = api.get_style("style-1")
        
        assert style is not None
        assert isinstance(style, ImageStyle)
        assert style.id == "style-1"
        assert style.name == "Abstract Art"

    def test_get_style_not_found(self, mock_client):
        """Test getting a style that doesn't exist."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "style-1",
                    "name": "Abstract Art",
                    "description": "Modern abstract art style",
                    "category": "artistic",
                    "preview_url": "https://example.com/preview1.png"
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        api = ImageStylesAPI(mock_client)
        style = api.get_style("nonexistent-style")
        
        assert style is None

    def test_search_styles_success(self, mock_client):
        """Test searching styles by query."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "style-1",
                    "name": "Abstract Art",
                    "description": "Modern abstract art style",
                    "category": "artistic",
                    "preview_url": "https://example.com/preview1.png"
                },
                {
                    "id": "style-2",
                    "name": "Realistic",
                    "description": "Photorealistic style",
                    "category": "realistic",
                    "preview_url": "https://example.com/preview2.png"
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        api = ImageStylesAPI(mock_client)
        styles = api.search_styles("abstract")
        
        assert len(styles) == 1
        assert styles[0].id == "style-1"
        assert styles[0].name == "Abstract Art"

    def test_search_styles_case_insensitive(self, mock_client):
        """Test searching styles case insensitive."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "style-1",
                    "name": "Abstract Art",
                    "description": "Modern abstract art style",
                    "category": "artistic",
                    "preview_url": "https://example.com/preview1.png"
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        api = ImageStylesAPI(mock_client)
        styles = api.search_styles("ABSTRACT")
        
        assert len(styles) == 1
        assert styles[0].id == "style-1"

    def test_search_styles_in_description(self, mock_client):
        """Test searching styles in description."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "style-1",
                    "name": "Art Style",
                    "description": "Modern abstract art style",
                    "category": "artistic",
                    "preview_url": "https://example.com/preview1.png"
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        api = ImageStylesAPI(mock_client)
        styles = api.search_styles("abstract")
        
        assert len(styles) == 1
        assert styles[0].id == "style-1"

    def test_search_styles_no_matches(self, mock_client):
        """Test searching styles with no matches."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "style-1",
                    "name": "Abstract Art",
                    "description": "Modern abstract art style",
                    "category": "artistic",
                    "preview_url": "https://example.com/preview1.png"
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        api = ImageStylesAPI(mock_client)
        styles = api.search_styles("nonexistent")
        
        assert len(styles) == 0


class TestConvenienceFunctionsComprehensive:
    """Comprehensive test suite for convenience functions."""

    def test_generate_image_with_client(self, mock_client):
        """Test generate_image with provided client."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"url": "https://example.com/image.png", "b64_json": None, "revised_prompt": "A beautiful sunset", "created": 1234567890}],
            "created": 1234567890
        }
        mock_client.post.return_value = mock_response
        
        result = generate_image("A beautiful sunset", client=mock_client)
        
        assert isinstance(result, ImageGeneration)
        assert result.url == "https://example.com/image.png"

    def test_generate_image_without_client(self):
        """Test generate_image without provided client."""
        with patch('venice_sdk.config.load_config') as mock_load_config:
            with patch('venice_sdk.venice_client.VeniceClient') as mock_venice_client:
                mock_config = MagicMock()
                mock_load_config.return_value = mock_config
                
                mock_client = MagicMock()
                mock_venice_client.return_value = mock_client
                
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "data": [{"url": "https://example.com/image.png", "b64_json": None, "revised_prompt": "A beautiful sunset", "created": 1234567890}],
                    "created": 1234567890
                }
                mock_client.post.return_value = mock_response
                
                result = generate_image("A beautiful sunset")
                
                assert isinstance(result, ImageGeneration)
                assert result.url == "https://example.com/image.png"

    def test_edit_image_with_client(self, mock_client, tmp_path):
        """Test edit_image with provided client."""
        test_data = b"fake image data"
        image_path = tmp_path / "test.png"
        image_path.write_bytes(test_data)
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"url": "https://example.com/edited.png", "b64_json": None, "revised_prompt": "Edited image", "created": 1234567890}],
            "created": 1234567890
        }
        mock_client.post.return_value = mock_response
        
        result = edit_image(image_path, "Make it more colorful", client=mock_client)
        
        assert isinstance(result, ImageEditResult)
        assert result.url == "https://example.com/edited.png"

    def test_upscale_image_with_client(self, mock_client, tmp_path):
        """Test upscale_image with provided client."""
        test_data = b"fake image data"
        image_path = tmp_path / "test.png"
        image_path.write_bytes(test_data)
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"url": "https://example.com/upscaled.png", "b64_json": None, "created": 1234567890}],
            "created": 1234567890
        }
        mock_client.post.return_value = mock_response
        
        result = upscale_image(image_path, client=mock_client)
        
        assert isinstance(result, ImageUpscaleResult)
        assert result.url == "https://example.com/upscaled.png"

    def test_generate_image_with_kwargs(self, mock_client):
        """Test generate_image with additional kwargs."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"url": "https://example.com/image.png", "b64_json": None, "revised_prompt": "A beautiful sunset", "created": 1234567890}],
            "created": 1234567890
        }
        mock_client.post.return_value = mock_response
        
        result = generate_image(
            "A beautiful sunset",
            client=mock_client,
            model="dall-e-3",
            size="1024x1024",
            quality="hd",
            style="abstract"
        )
        
        assert isinstance(result, ImageGeneration)
        call_args = mock_client.post.call_args
        assert call_args[1]["data"]["model"] == "dall-e-3"
        assert call_args[1]["data"]["size"] == "1024x1024"
        assert call_args[1]["data"]["quality"] == "hd"
        assert call_args[1]["data"]["style"] == "abstract"
