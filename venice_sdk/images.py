"""
Venice AI SDK - Image Generation and Processing Module

This module provides comprehensive image generation, editing, upscaling, and style management
capabilities using the Venice AI API.
"""

from __future__ import annotations

import base64
import json
import logging
import requests
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Generator
from urllib.parse import urlparse

from .client import HTTPClient
from .errors import VeniceAPIError, ImageGenerationError
from .endpoints import ImageEndpoints
from ._http import ensure_http_client

logger = logging.getLogger(__name__)


@dataclass
class ImageGeneration:
    """Represents a generated image response."""
    url: Optional[str] = None
    b64_json: Optional[str] = None
    revised_prompt: Optional[str] = None
    created: Optional[int] = None
    
    def save(self, path: Union[str, Path]) -> Path:
        """Save the image to a file."""
        path = Path(path)
        
        if self.url:
            # Check if it's a data URL
            if self.url.startswith('data:'):
                # Extract base64 data from data URL
                header, data = self.url.split(',', 1)
                image_data = base64.b64decode(data)
                path.write_bytes(image_data)
            else:
                # Download from HTTP URL
                response = requests.get(self.url)
                response.raise_for_status()
                path.write_bytes(response.content)
        elif self.b64_json:
            # Save from base64 data
            image_data = base64.b64decode(self.b64_json)
            path.write_bytes(image_data)
        else:
            raise ImageGenerationError("No image data available to save")
        
        return path
    
    def get_image_data(self) -> bytes:
        """Get the raw image data as bytes."""
        
        if self.url:
            # Check if it's a data URL
            if self.url.startswith('data:'):
                # Extract base64 data from data URL
                header, data = self.url.split(',', 1)
                return base64.b64decode(data)
            else:
                # Download from HTTP URL
                response = requests.get(self.url)
                response.raise_for_status()
                return response.content
        elif self.b64_json:
            return base64.b64decode(self.b64_json)
        else:
            raise ImageGenerationError("No image data available")


@dataclass
class ImageEditResult:
    """Represents an image editing response."""
    url: Optional[str] = None
    b64_json: Optional[str] = None
    revised_prompt: Optional[str] = None
    created: Optional[int] = None
    
    def save(self, path: Union[str, Path]) -> Path:
        """Save the edited image to a file."""
        path = Path(path)
        
        if self.url:
            # Check if it's a data URL
            if self.url.startswith('data:'):
                # Extract base64 data from data URL
                header, data = self.url.split(',', 1)
                image_data = base64.b64decode(data)
                path.write_bytes(image_data)
            else:
                # Download from HTTP URL
                response = requests.get(self.url)
                response.raise_for_status()
                path.write_bytes(response.content)
        elif self.b64_json:
            image_data = base64.b64decode(self.b64_json)
            path.write_bytes(image_data)
        else:
            raise ImageGenerationError("No image data available to save")
        
        return path


@dataclass
class ImageUpscaleResult:
    """Represents an image upscaling response."""
    url: Optional[str] = None
    b64_json: Optional[str] = None
    created: Optional[int] = None
    
    def save(self, path: Union[str, Path]) -> Path:
        """Save the upscaled image to a file."""
        path = Path(path)
        
        if self.url:
            # Check if it's a data URL
            if self.url.startswith('data:'):
                # Extract base64 data from data URL
                header, data = self.url.split(',', 1)
                image_data = base64.b64decode(data)
                path.write_bytes(image_data)
            else:
                # Download from HTTP URL
                response = requests.get(self.url)
                response.raise_for_status()
                path.write_bytes(response.content)
        elif self.b64_json:
            image_data = base64.b64decode(self.b64_json)
            path.write_bytes(image_data)
        else:
            raise ImageGenerationError("No image data available to save")
        
        return path


@dataclass
class ImageStyle:
    """Represents an available image style."""
    id: str
    name: str
    description: str
    category: Optional[str] = None
    preview_url: Optional[str] = None


class ImageAPI:
    """Image generation and processing API client."""
    
    def __init__(self, client: HTTPClient):
        self.client = client
    
    def generate(
        self,
        prompt: str,
        model: str = "dall-e-3",
        n: int = 1,
        size: str = "1024x1024",
        quality: str = "standard",
        style: Optional[str] = None,
        response_format: str = "url",
        user: Optional[str] = None,
        **kwargs: Any
    ) -> Union[ImageGeneration, List[ImageGeneration]]:
        """
        Generate images from text prompts.
        
        Args:
            prompt: Text description of the desired image
            model: Model to use for generation
            n: Number of images to generate (1-10)
            size: Image dimensions (e.g., "1024x1024", "512x512")
            quality: Image quality ("standard" or "hd")
            style: Artistic style to apply
            response_format: Response format ("url" or "b64_json")
            user: User identifier for tracking
            **kwargs: Additional parameters
            
        Returns:
            Single ImageGeneration or list of ImageGenerations
        """
        # Validate input parameters
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        if n < 1 or n > 10:
            raise ValueError("n must be between 1 and 10")
        if size not in ["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]:
            raise ValueError(f"Invalid size: {size}")
        if quality not in ["standard", "hd"]:
            raise ValueError(f"Invalid quality: {quality}")
        if response_format not in ["url", "b64_json"]:
            raise ValueError(f"Invalid response_format: {response_format}")
            
        data = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "size": size,
            "quality": quality,
            "response_format": response_format,
            **kwargs
        }
        
        if style:
            data["style"] = style
        if user:
            data["user"] = user
        
        logger.debug(
            "Image generation request (model=%s, n=%s, size=%s, format=%s)",
            model,
            n,
            size,
            response_format,
        )
        response = self.client.post(ImageEndpoints.GENERATIONS, data=data)
        result = response.json()
        
        if "data" not in result:
            raise ImageGenerationError("Invalid response format from image generation API")
        
        images = []
        for item in result["data"]:
            images.append(ImageGeneration(
                url=item.get("url"),
                b64_json=item.get("b64_json"),
                revised_prompt=item.get("revised_prompt"),
                created=result.get("created")
            ))
        
        logger.debug("Image generation produced %s image(s)", len(images))
        return images[0] if len(images) == 1 else images

    def generate_native(
        self,
        prompt: str,
        model: str,
        *,
        negative_prompt: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None,
        cfg_scale: Optional[float] = None,
        steps: Optional[int] = None,
        seed: Optional[int] = None,
        style_preset: Optional[str] = None,
        format: Optional[str] = None,
        variants: Optional[int] = None,
        safe_mode: Optional[bool] = None,
        return_binary: Optional[bool] = None,
        enhance_prompt: Optional[Any] = None,
        enable_web_search: Optional[Any] = None,
        hide_watermark: Optional[bool] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Venice-native image generation (``POST /image/generate``).

        Richer parameter surface than OpenAI-compat ``generate()`` /
        ``/images/generations``.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        if not model:
            raise ValueError("model is required")
        data: Dict[str, Any] = {"prompt": prompt, "model": model, **kwargs}
        optional = {
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "cfg_scale": cfg_scale,
            "steps": steps,
            "seed": seed,
            "style_preset": style_preset,
            "format": format,
            "variants": variants,
            "safe_mode": safe_mode,
            "return_binary": return_binary,
            "enhance_prompt": enhance_prompt,
            "enable_web_search": enable_web_search,
            "hide_watermark": hide_watermark,
        }
        for key, value in optional.items():
            if value is not None:
                data[key] = value
        response = self.client.post(ImageEndpoints.GENERATE, data=data)
        # Native endpoint may return binary or JSON depending on return_binary / Accept.
        ctype = (response.headers.get("Content-Type") or "").lower()
        if "application/json" in ctype:
            return response.json()
        return response.content
    
    def generate_batch(
        self,
        prompts: List[str],
        model: str = "dall-e-3",
        size: str = "1024x1024",
        quality: str = "standard",
        style: Optional[str] = None,
        response_format: str = "url",
        **kwargs: Any
    ) -> List[ImageGeneration]:
        """
        Generate images for multiple prompts.
        
        Args:
            prompts: List of text descriptions
            model: Model to use for generation
            size: Image dimensions
            quality: Image quality
            style: Artistic style to apply
            response_format: Response format
            **kwargs: Additional parameters
            
        Returns:
            List of ImageGenerations
        """
        all_images = []
        
        for prompt in prompts:
            images = self.generate(
                prompt=prompt,
                model=model,
                n=1,
                size=size,
                quality=quality,
                style=style,
                response_format=response_format,
                **kwargs
            )
            
            if isinstance(images, list):
                all_images.extend(images)
            else:
                all_images.append(images)
        
        return all_images


class ImageEditAPI:
    """Image editing API client."""
    
    def __init__(self, client: HTTPClient):
        self.client = client
    
    def _encode_image(self, image: Union[str, bytes, Path]) -> str:
        """Encode image to base64."""
        if isinstance(image, str):
            if image.startswith(('http://', 'https://')):
                # Download from URL
                response = requests.get(image)
                response.raise_for_status()
                image_data = response.content
            else:
                # Local file path
                image_data = Path(image).read_bytes()
        elif isinstance(image, bytes):
            image_data = image
        elif isinstance(image, Path):
            image_data = image.read_bytes()
        else:
            raise ValueError("Invalid image type. Expected str, bytes, or Path")
        
        return base64.b64encode(image_data).decode('utf-8')
    
    def edit(
        self,
        image: Union[str, bytes, Path],
        prompt: str,
        **kwargs: Any
    ) -> ImageEditResult:
        """
        Edit an existing image using text prompts.
        
        Args:
            image: Image to edit (URL, file path, or bytes)
            prompt: Text description of desired edits
            **kwargs: Additional parameters
            
        Returns:
            ImageEditResult with the edited image
        """
        data = {
            "image": self._encode_image(image),
            "prompt": prompt,
            **kwargs
        }
        
        logger.debug("Image edit request (prompt=%s)", prompt)
        response = self.client.post(ImageEndpoints.EDIT, data=data)
        
        # Check if response is binary image data (case-insensitive check)
        content_type = response.headers.get('Content-Type', '').lower()
        if 'image/' in content_type:
            # Binary image response - convert to base64
            image_data = response.content
            b64_data = base64.b64encode(image_data).decode('utf-8')
            logger.debug("Image edit completed, received binary image")
            return ImageEditResult(b64_json=b64_data)
        else:
            # JSON response
            result = response.json()
            
            if "data" not in result:
                raise ImageGenerationError("Invalid response format from image edit API")
            
            images = []
            for item in result["data"]:
                images.append(ImageEditResult(
                    url=item.get("url"),
                    b64_json=item.get("b64_json"),
                    revised_prompt=item.get("revised_prompt"),
                    created=result.get("created")
                ))
            
            logger.debug("Image edit produced %s image(s)", len(images))
            return images[0] if len(images) == 1 else images

    def multi_edit(
        self,
        images: List[Union[str, bytes, Path]],
        prompt: str,
        model_id: str = "qwen-edit",
        **kwargs: Any
    ) -> ImageEditResult:
        """
        Edit or modify an image using up to three layered inputs (base image plus masks/overlays).

        The first image is the base image; the remaining images are used as edit layers/masks.
        Each image can be a URL, file path, or bytes. Returns PNG with transparent background
        where applicable.

        Args:
            images: List of 1–3 images (URL, path, or bytes). First = base, rest = layers/masks.
            prompt: Text directions for the edit (e.g. "remove the tree", "change the sky to sunrise").
            model_id: Model to use (e.g. qwen-edit, flux-2-max-edit, gpt-image-1-5-edit).
            **kwargs: Additional parameters.

        Returns:
            ImageEditResult with the edited image (PNG).
        """
        if not 1 <= len(images) <= 3:
            raise ValueError("images must contain 1 to 3 images")
        if not prompt or not prompt.strip():
            raise ValueError("prompt cannot be empty")
        encoded: List[str] = []
        for i, img in enumerate(images):
            if isinstance(img, str) and (img.startswith("http://") or img.startswith("https://")):
                encoded.append(img)
            else:
                encoded.append(self._encode_image(img))
        data: Dict[str, Any] = {
            "prompt": prompt,
            "images": encoded,
            "modelId": model_id,
            **kwargs,
        }
        logger.debug("Image multi-edit request (model_id=%s, num_images=%s)", model_id, len(images))
        response = self.client.post(ImageEndpoints.MULTI_EDIT, data=data)
        content_type = response.headers.get("Content-Type", "").lower()
        if "image/" in content_type:
            b64_data = base64.b64encode(response.content).decode("utf-8")
            return ImageEditResult(b64_json=b64_data)
        try:
            err = response.json()
            raise ImageGenerationError(err.get("error", "Multi-edit failed"))
        except Exception:
            raise ImageGenerationError("Multi-edit failed with non-image response")

    def remove_background(
        self,
        image: Optional[Union[str, bytes, Path]] = None,
        image_url: Optional[str] = None,
        **kwargs: Any
    ) -> ImageEditResult:
        """
        Remove the background from an image. Returns a PNG with transparent background.

        Provide either image (file path, bytes, or base64 string) or image_url, not both.

        Args:
            image: Image as file path, bytes, or data-URL/base64 string.
            image_url: Public URL of the image (http/https).
            **kwargs: Additional parameters.

        Returns:
            ImageEditResult with the PNG (transparent background).
        """
        if image is None and not image_url:
            raise ValueError("Provide either image or image_url")
        if image is not None and image_url:
            raise ValueError("Provide only one of image or image_url")
        data: Dict[str, Any] = {}
        if image_url:
            data["image_url"] = image_url
        else:
            data["image"] = self._encode_image(image)
        data.update(kwargs)
        logger.debug("Image background-remove request")
        response = self.client.post(ImageEndpoints.BACKGROUND_REMOVE, data=data)
        content_type = response.headers.get("Content-Type", "").lower()
        if "image/" in content_type:
            b64_data = base64.b64encode(response.content).decode("utf-8")
            return ImageEditResult(b64_json=b64_data)
        try:
            err = response.json()
            raise ImageGenerationError(err.get("error", "Background remove failed"))
        except Exception:
            raise ImageGenerationError("Background remove failed with non-image response")


class ImageUpscaleAPI:
    """Image upscaling API client."""
    
    def __init__(self, client: HTTPClient):
        self.client = client
    
    def _encode_image(self, image: Union[str, bytes, Path]) -> str:
        """Encode image to base64."""
        if isinstance(image, str):
            if image.startswith(('http://', 'https://')):
                import requests
                response = requests.get(image)
                response.raise_for_status()
                image_data = response.content
            else:
                image_data = Path(image).read_bytes()
        elif isinstance(image, bytes):
            image_data = image
        elif isinstance(image, Path):
            image_data = image.read_bytes()
        else:
            raise ValueError("Invalid image type. Expected str, bytes, or Path")
        
        return base64.b64encode(image_data).decode('utf-8')
    
    def upscale(
        self,
        image: Union[str, bytes, Path],
        model: str = "upscaler-v1",
        scale: int = 2,
        response_format: str = "url",
        **kwargs: Any
    ) -> ImageUpscaleResult:
        """
        Upscale an image to higher resolution.
        
        Args:
            image: Image to upscale (URL, file path, or bytes)
            model: Upscaling model to use
            scale: Upscaling factor (2, 4, etc.)
            response_format: Response format ("url" or "b64_json")
            **kwargs: Additional parameters
            
        Returns:
            ImageUpscaleResult with upscaled image
        """
        data = {
            "model": model,
            "image": self._encode_image(image),
            "scale": scale,
            "response_format": response_format,
            **kwargs
        }
        
        logger.debug(
            "Image upscale request (model=%s, scale=%s, response_format=%s)",
            model,
            scale,
            response_format,
        )
        response = self.client.post(ImageEndpoints.UPSCALE, data=data)
        result = response.json()
        
        if "data" not in result or not result["data"]:
            raise ImageGenerationError("Invalid response format from image upscale API")
        
        item = result["data"][0]  # Upscale typically returns single image
        logger.debug("Image upscale completed (model=%s)", model)
        return ImageUpscaleResult(
            url=item.get("url"),
            b64_json=item.get("b64_json"),
            created=result.get("created")
        )


class ImageStylesAPI:
    """Image styles management API client."""
    
    def __init__(self, client: HTTPClient):
        self.client = client
    
    def list_styles(self) -> List[ImageStyle]:
        """
        List all available image styles.
        
        Returns:
            List of ImageStyle objects
        """
        logger.debug("Fetching available image styles")
        response = self.client.get(ImageEndpoints.STYLES)
        result = response.json()
        
        if "data" not in result:
            raise ImageGenerationError("Invalid response format from image styles API")
        
        styles = []
        for style_data in result["data"]:
            # Handle both dict and string formats
            if isinstance(style_data, dict):
                style_id = style_data.get("id", "")
                name = style_data.get("name", "")
                description = style_data.get("description", f"Image style: {name}")
                category = style_data.get("category")
                preview_url = style_data.get("preview_url")
            else:
                # Fallback for string format
                style_id = style_data.lower().replace(" ", "_").replace("-", "_")
                name = style_data
                description = f"Image style: {style_data}"
                category = None
                preview_url = None
            
            styles.append(ImageStyle(
                id=style_id,
                name=name,
                description=description,
                category=category,
                preview_url=preview_url
            ))
        
        logger.debug("Retrieved %s image styles", len(styles))
        return styles
    
    def get_style(self, style_id: str) -> Optional[ImageStyle]:
        """
        Get a specific image style by ID.
        
        Args:
            style_id: Style identifier
            
        Returns:
            ImageStyle object or None if not found
        """
        styles = self.list_styles()
        for style in styles:
            if style.id == style_id:
                return style
        return None
    
    def search_styles(self, query: str) -> List[ImageStyle]:
        """
        Search for styles by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching ImageStyle objects
        """
        styles = self.list_styles()
        query_lower = query.lower()
        
        return [
            style for style in styles
            if query_lower in style.name.lower() or query_lower in style.description.lower()
        ]


# Convenience functions
def generate_image(
    prompt: str,
    client: Optional[HTTPClient] = None,
    **kwargs: Any
) -> ImageGeneration:
    """Convenience function to generate a single image."""
    http_client = ensure_http_client(client)
    api = ImageAPI(http_client)
    result = api.generate(prompt, **kwargs)
    if isinstance(result, list):
        return result[0]
    return result


def edit_image(
    image: Union[str, bytes, Path],
    prompt: str,
    client: Optional[HTTPClient] = None,
    **kwargs: Any
) -> ImageEditResult:
    """Convenience function to edit an image."""
    http_client = ensure_http_client(client)
    api = ImageEditAPI(http_client)
    result = api.edit(image, prompt, **kwargs)
    if isinstance(result, list):
        return result[0]
    return result


def upscale_image(
    image: Union[str, bytes, Path],
    client: Optional[HTTPClient] = None,
    **kwargs: Any
) -> ImageUpscaleResult:
    """Convenience function to upscale an image."""
    http_client = ensure_http_client(client)
    api = ImageUpscaleAPI(http_client)
    return api.upscale(image, **kwargs)


def multi_edit_image(
    images: List[Union[str, bytes, Path]],
    prompt: str,
    client: Optional[HTTPClient] = None,
    **kwargs: Any
) -> ImageEditResult:
    """Convenience function to multi-edit an image (1–3 layers)."""
    http_client = ensure_http_client(client)
    api = ImageEditAPI(http_client)
    return api.multi_edit(images, prompt, **kwargs)


def remove_background(
    image: Optional[Union[str, bytes, Path]] = None,
    image_url: Optional[str] = None,
    client: Optional[HTTPClient] = None,
    **kwargs: Any
) -> ImageEditResult:
    """Convenience function to remove the background from an image."""
    http_client = ensure_http_client(client)
    api = ImageEditAPI(http_client)
    return api.remove_background(image=image, image_url=image_url, **kwargs)
