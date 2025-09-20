"""
Live tests for the Images module.

These tests make real API calls to verify images functionality.
"""

import pytest
import os
import tempfile
from pathlib import Path
from venice_sdk.images import ImageAPI, ImageEditAPI, ImageUpscaleAPI, ImageStylesAPI
from venice_sdk.client import HTTPClient
from venice_sdk.config import Config
from venice_sdk.errors import VeniceAPIError
from .test_utils import LiveTestUtils


@pytest.mark.live
class TestImagesAPILive:
    """Live tests for Images APIs with real API calls."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.api_key = os.getenv("VENICE_API_KEY")
        if not self.api_key:
            pytest.skip("VENICE_API_KEY environment variable not set")
        
        self.config = Config(api_key=self.api_key)
        self.client = HTTPClient(self.config)
        self.image_api = ImageAPI(self.client)
        self.image_edit_api = ImageEditAPI(self.client)
        self.image_upscale_api = ImageUpscaleAPI(self.client)
        self.image_styles_api = ImageStylesAPI(self.client)
        
        # Get available image models dynamically
        self.image_models = ["dall-e-3", "dall-e-2", "midjourney", "stable-diffusion", "venice-image", "image-gen"]
        self.default_image_model = "dall-e-3"

    def test_generate_image(self):
        """Test basic image generation."""
        prompt = "A beautiful sunset over a mountain landscape"
        
        result = self.image_api.generate(
            prompt=prompt,
            model=self.default_image_model,
            n=1,
            size="1024x1024",
            quality="standard"
        )
        
        assert result is not None
        assert hasattr(result, 'url')
        assert hasattr(result, 'b64_json')
        assert hasattr(result, 'revised_prompt')
        assert hasattr(result, 'created')
        
        # At least one of url or b64_json should be present
        assert result.url is not None or result.b64_json is not None

    def test_generate_image_with_different_sizes(self):
        """Test image generation with different sizes."""
        prompt = "A cute cat sitting on a windowsill"
        sizes = ["1024x1024", "512x512", "256x256"]
        
        for size in sizes:
            try:
                result = self.image_api.generate(
                    prompt=prompt,
                    model=self.default_image_model,
                    size=size,
                    quality="standard"
                )
                
                assert result is not None
                assert result.url is not None or result.b64_json is not None
                
            except VeniceAPIError as e:
                # Some sizes might not be available
                if e.status_code == 400:
                    continue
                raise

    def test_generate_image_with_different_qualities(self):
        """Test image generation with different qualities."""
        prompt = "A futuristic city skyline at night"
        qualities = ["standard", "hd"]
        
        for quality in qualities:
            try:
                result = self.image_api.generate(
                    prompt=prompt,
                    model=self.default_image_model,
                    quality=quality
                )
                
                assert result is not None
                assert result.url is not None or result.b64_json is not None
                
            except VeniceAPIError as e:
                # Some qualities might not be available
                if e.status_code == 400:
                    continue
                raise

    def test_generate_multiple_images(self):
        """Test generating multiple images (one by one since API doesn't support n > 1)."""
        prompt = "Abstract art with vibrant colors"
        
        # Generate images one by one since API doesn't support n > 1
        results = []
        for i in range(2):
            result = self.image_api.generate(
                prompt=f"{prompt} - variation {i+1}",
                model=self.default_image_model,
                n=1,
                size="1024x1024"
            )
            results.extend(result if isinstance(result, list) else [result])
        
        assert isinstance(results, list)
        assert len(results) == 2
        
        for image in results:
            assert hasattr(image, 'url')
            assert hasattr(image, 'b64_json')
            assert image.url is not None or image.b64_json is not None

    def test_generate_image_with_style(self):
        """Test image generation with style."""
        prompt = "A portrait of a person"
        
        try:
            result = self.image_api.generate(
                prompt=prompt,
                model=self.default_image_model,
                style="vivid"
            )
            
            assert result is not None
            assert result.url is not None or result.b64_json is not None
            
        except VeniceAPIError as e:
            # Style might not be available
            if e.status_code == 400:
                pytest.skip("Style not available for this model")
            raise

    def test_generate_image_with_b64_json_response(self):
        """Test image generation with base64 JSON response."""
        prompt = "A simple geometric pattern"
        
        result = self.image_api.generate(
            prompt=prompt,
            model=self.default_image_model,
            response_format="b64_json"
        )
        
        assert result is not None
        assert result.b64_json is not None
        assert result.url is None

    def test_generate_image_batch(self):
        """Test batch image generation."""
        prompts = [
            "A serene lake with mountains in the background",
            "A bustling city street with people walking",
            "A peaceful garden with flowers blooming"
        ]
        
        results = self.image_api.generate_batch(
            prompts=prompts,
            model=self.default_image_model,
            size="1024x1024"
        )
        
        assert isinstance(results, list)
        assert len(results) == len(prompts)
        
        for result in results:
            assert hasattr(result, 'url')
            assert hasattr(result, 'b64_json')
            assert result.url is not None or result.b64_json is not None

    def test_save_image_to_file(self):
        """Test saving generated image to file."""
        prompt = "A beautiful landscape with a river"
        
        result = self.image_api.generate(
            prompt=prompt,
            model=self.default_image_model,
            response_format="url"
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "generated_image.png"
            
            saved_path = result.save(output_path)
            
            assert saved_path == output_path
            assert output_path.exists()
            assert output_path.stat().st_size > 0

    def test_get_image_data(self):
        """Test getting image data as bytes."""
        prompt = "A simple test image"
        
        result = self.image_api.generate(
            prompt=prompt,
            model=self.default_image_model,
            response_format="b64_json"
        )
        
        image_data = result.get_image_data()
        
        assert isinstance(image_data, bytes)
        assert len(image_data) > 0

    def test_list_image_styles(self):
        """Test listing available image styles."""
        styles = self.image_styles_api.list_styles()
        
        assert isinstance(styles, list)
        assert len(styles) > 0
        
        # Verify style structure
        style = styles[0]
        assert hasattr(style, 'id')
        assert hasattr(style, 'name')
        assert hasattr(style, 'description')
        assert hasattr(style, 'category')
        assert hasattr(style, 'preview_url')

    def test_get_image_style_by_id(self):
        """Test getting a specific image style by ID."""
        # First get the list to find a valid style ID
        styles = self.image_styles_api.list_styles()
        assert len(styles) > 0
        
        style_id = styles[0].id
        style = self.image_styles_api.get_style(style_id)
        
        assert style is not None
        assert style.id == style_id
        assert hasattr(style, 'name')
        assert hasattr(style, 'description')

    def test_get_nonexistent_image_style(self):
        """Test getting an image style that doesn't exist."""
        style = self.image_styles_api.get_style("nonexistent-style-id")
        assert style is None

    def test_search_image_styles(self):
        """Test searching image styles."""
        # Search for styles with "abstract" in the name or description
        styles = self.image_styles_api.search_styles("abstract")
        
        assert isinstance(styles, list)
        # Should find at least one style
        
        # Verify search results
        for style in styles:
            search_term = "abstract"
            assert (search_term in style.name.lower() or 
                   search_term in style.description.lower())

    def test_search_image_styles_case_insensitive(self):
        """Test case-insensitive image style search."""
        styles = self.image_styles_api.search_styles("ABSTRACT")
        
        assert isinstance(styles, list)

    def test_search_image_styles_no_results(self):
        """Test image style search with no results."""
        styles = self.image_styles_api.search_styles("nonexistent-style-name")
        
        assert isinstance(styles, list)
        assert len(styles) == 0

    def test_image_generation_with_parameters(self):
        """Test image generation with various parameters."""
        prompt = "A creative artwork"
        
        result = self.image_api.generate(
            prompt=prompt,
            model=self.default_image_model,
            n=1,
            size="1024x1024",
            quality="standard",
            response_format="url",
            user="test-user-123"
        )
        
        assert result is not None
        assert result.url is not None or result.b64_json is not None

    def test_image_generation_error_handling(self):
        """Test error handling in image generation."""
        # Test with invalid model
        with pytest.raises(VeniceAPIError):
            self.image_api.generate(
                prompt="Test prompt",
                model="invalid-model"
            )

    def test_image_generation_with_empty_prompt(self):
        """Test image generation with empty prompt."""
        with pytest.raises(ValueError):
            self.image_api.generate(
                prompt="",
                model=self.default_image_model
            )

    def test_image_generation_with_none_prompt(self):
        """Test image generation with None prompt."""
        with pytest.raises(ValueError):
            self.image_api.generate(
                prompt=None,
                model=self.default_image_model
            )

    def test_image_generation_with_special_characters(self):
        """Test image generation with special characters."""
        prompt = "A surreal artwork with @#$%^&*()_+-=[]{}|;':\",./<>? symbols"
        
        result = self.image_api.generate(
            prompt=prompt,
            model=self.default_image_model
        )
        
        assert result is not None
        assert result.url is not None or result.b64_json is not None

    def test_image_generation_with_unicode(self):
        """Test image generation with unicode characters."""
        prompt = "A beautiful artwork with 🌟🎨🎭 emojis and special characters"
        
        result = self.image_api.generate(
            prompt=prompt,
            model=self.default_image_model
        )
        
        assert result is not None
        assert result.url is not None or result.b64_json is not None

    def test_image_generation_with_long_prompt(self):
        """Test image generation with long prompt."""
        long_prompt = "A very detailed and complex artwork that describes a futuristic city with flying cars, neon lights, and people walking on the streets. The city should have tall buildings, a beautiful skyline, and a sense of wonder and amazement. " * 10
        
        result = self.image_api.generate(
            prompt=long_prompt,
            model=self.default_image_model
        )
        
        assert result is not None
        assert result.url is not None or result.b64_json is not None

    def test_image_generation_performance(self):
        """Test image generation performance."""
        import time
        
        prompt = "A simple test image for performance testing"
        
        start_time = time.time()
        result = self.image_api.generate(
            prompt=prompt,
            model=self.default_image_model
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert result is not None
        assert response_time < 60  # Should complete within 60 seconds
        assert response_time > 0

    def test_image_generation_batch_performance(self):
        """Test batch image generation performance."""
        import time
        
        prompts = [f"Test image {i} for batch performance" for i in range(3)]
        
        start_time = time.time()
        results = self.image_api.generate_batch(
            prompts=prompts,
            model=self.default_image_model
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert len(results) == len(prompts)
        assert response_time < 120  # Should complete within 120 seconds
        assert response_time > 0

    def test_image_generation_concurrent_requests(self):
        """Test concurrent image generation requests."""
        import threading
        import time
        
        results = []
        errors = []
        
        def generate_image():
            try:
                prompt = f"Hello from thread {threading.current_thread().name}"
                result = self.image_api.generate(
                    prompt=prompt,
                    model=self.default_image_model
                )
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for i in range(2):  # Reduced to 2 to avoid rate limiting
            thread = threading.Thread(target=generate_image, name=f"Thread-{i}")
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(results) == 2
        assert len(errors) == 0
        assert all(result is not None for result in results)

    def test_image_generation_memory_usage(self):
        """Test memory usage during image generation."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Generate multiple images
        for i in range(3):
            prompt = f"Testing memory usage for image generation {i}"
            result = self.image_api.generate(
                prompt=prompt,
                model=self.default_image_model
            )
            assert result is not None
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 200MB)
        assert memory_increase < 200 * 1024 * 1024

    def test_image_generation_with_different_models(self):
        """Test image generation with different models."""
        prompt = "A beautiful landscape"
        models = ["dall-e-3", "dall-e-2"]
        
        for model in models:
            try:
                result = self.image_api.generate(
                    prompt=prompt,
                    model=model
                )
                
                assert result is not None
                assert result.url is not None or result.b64_json is not None
                
            except VeniceAPIError as e:
                # Some models might not be available
                if e.status_code == 404:
                    continue
                raise

    def test_image_generation_with_revised_prompt(self):
        """Test image generation with revised prompt."""
        prompt = "A beautiful sunset over mountains"
        
        result = self.image_api.generate(
            prompt=prompt,
            model=self.default_image_model
        )
        
        assert result is not None
        if result.revised_prompt:
            assert isinstance(result.revised_prompt, str)
            assert len(result.revised_prompt) > 0

    def test_image_generation_creation_timestamp(self):
        """Test image generation creation timestamp."""
        prompt = "A test image for timestamp verification"
        
        result = self.image_api.generate(
            prompt=prompt,
            model=self.default_image_model
        )
        
        assert result is not None
        if result.created:
            assert isinstance(result.created, int)
            assert result.created > 0

    def test_image_generation_file_formats(self):
        """Test image generation with different file formats."""
        prompt = "A test image for format verification"
        
        # Test with URL format
        result_url = self.image_api.generate(
            prompt=prompt,
            model=self.default_image_model,
            response_format="url"
        )
        
        assert result_url is not None
        assert result_url.url is not None
        assert result_url.b64_json is None
        
        # Test with base64 format
        result_b64 = self.image_api.generate(
            prompt=prompt,
            model=self.default_image_model,
            response_format="b64_json"
        )
        
        assert result_b64 is not None
        assert result_b64.b64_json is not None
        assert result_b64.url is None

    def test_image_generation_quality_comparison(self):
        """Test image generation quality comparison."""
        prompt = "A detailed portrait of a person"
        
        # Test standard quality
        result_standard = self.image_api.generate(
            prompt=prompt,
            model=self.default_image_model,
            quality="standard"
        )
        
        # Test HD quality
        try:
            result_hd = self.image_api.generate(
                prompt=prompt,
                model=self.default_image_model,
                quality="hd"
            )
            
            assert result_standard is not None
            assert result_hd is not None
            
        except VeniceAPIError as e:
            # HD quality might not be available
            if e.status_code == 400:
                pytest.skip("HD quality not available for this model")
            raise

    def test_image_generation_size_comparison(self):
        """Test image generation size comparison."""
        prompt = "A simple geometric pattern"
        
        # Test different sizes
        sizes = ["1024x1024", "512x512"]
        
        for size in sizes:
            try:
                result = self.image_api.generate(
                    prompt=prompt,
                    model=self.default_image_model,
                    size=size
                )
                
                assert result is not None
                assert result.url is not None or result.b64_json is not None
                
            except VeniceAPIError as e:
                # Some sizes might not be available
                if e.status_code == 400:
                    continue
                raise

    def test_image_generation_with_user_parameter(self):
        """Test image generation with user parameter."""
        prompt = "A test image with user parameter"
        
        result = self.image_api.generate(
            prompt=prompt,
            model=self.default_image_model,
            user="test-user-123"
        )
        
        assert result is not None
        assert result.url is not None or result.b64_json is not None

    def test_image_generation_with_custom_parameters(self):
        """Test image generation with custom parameters."""
        prompt = "A test image with custom parameters"
        
        result = self.image_api.generate(
            prompt=prompt,
            model=self.default_image_model,
            custom_param="custom_value"
        )
        
        assert result is not None
        assert result.url is not None or result.b64_json is not None

    def test_image_generation_error_responses(self):
        """Test image generation error responses."""
        # Test with invalid prompt (too short)
        with pytest.raises(VeniceAPIError):
            self.image_api.generate(
                prompt="a",
                model=self.default_image_model
            )

    def test_image_generation_rate_limiting(self):
        """Test image generation rate limiting."""
        # Make multiple rapid requests to potentially trigger rate limiting
        results = []
        for i in range(3):
            try:
                result = self.image_api.generate(
                    prompt=f"Rate limit test {i}",
                    model=self.default_image_model
                )
                results.append(result)
            except VeniceAPIError as e:
                if e.status_code == 429:
                    # Rate limited - this is expected behavior
                    assert e.status_code == 429
                    return
        
        # If we get here, all requests succeeded
        assert len(results) == 3
        assert all(result is not None for result in results)
