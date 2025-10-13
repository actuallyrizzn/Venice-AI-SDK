"""
Venice AI SDK - Image Generation and Processing Module

This module provides comprehensive image generation, editing, upscaling, and style management
capabilities using the Venice AI API.
"""

from __future__ import annotations

import base64
import json
import requests
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Generator
from urllib.parse import urlparse

from .client import HTTPClient
from .errors import VeniceAPIError, ImageGenerationError
from .config import load_config
from .endpoints import ImageEndpoints


@dataclass
class ImageGeneration:
    """Represents a generated image response."""
    url: Optional[str] = None
    b64_json: Optional[str] = None
    revised_prompt: Optional[str] = None
    created: Optional[int] = None
    
    def save(self, path: Union[str, Path]) -> Path:
        """Save the image to a file."""
        import base64
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
                import requests
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
        import base64
        
        if self.url:
            # Check if it's a data URL
            if self.url.startswith('data:'):
                # Extract base64 data from data URL
                header, data = self.url.split(',', 1)
                return base64.b64decode(data)
            else:
                # Download from HTTP URL
                import requests
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
        import base64
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
                import requests
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
        import base64
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
                import requests
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
        **kwargs
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
        
        return images[0] if len(images) == 1 else images
    
    def generate_batch(
        self,
        prompts: List[str],
        model: str = "dall-e-3",
        size: str = "1024x1024",
        quality: str = "standard",
        style: Optional[str] = None,
        response_format: str = "url",
        **kwargs
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
                import requests
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
        model: str = "dall-e-2-edit",
        mask: Optional[Union[str, bytes, Path]] = None,
        n: int = 1,
        size: Optional[str] = None,
        response_format: str = "url",
        user: Optional[str] = None,
        **kwargs
    ) -> Union[ImageEditResult, List[ImageEditResult]]:
        """
        Edit an existing image using text prompts.
        
        Args:
            image: Image to edit (URL, file path, or bytes)
            prompt: Text description of desired edits
            model: Model to use for editing
            mask: Optional mask image for selective editing
            n: Number of edited images to generate
            size: Output image dimensions
            response_format: Response format ("url" or "b64_json")
            user: User identifier for tracking
            **kwargs: Additional parameters
            
        Returns:
            Single ImageEditResult or list of ImageEditResults
        """
        data = {
            "model": model,
            "image": self._encode_image(image),
            "prompt": prompt,
            "n": n,
            "response_format": response_format,
            **kwargs
        }
        
        if mask:
            data["mask"] = self._encode_image(mask)
        if size:
            data["size"] = size
        if user:
            data["user"] = user
        
        response = self.client.post(ImageEndpoints.EDIT, data=data)
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
        
        return images[0] if len(images) == 1 else images


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
        **kwargs
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
        
        response = self.client.post(ImageEndpoints.UPSCALE, data=data)
        result = response.json()
        
        if "data" not in result or not result["data"]:
            raise ImageGenerationError("Invalid response format from image upscale API")
        
        item = result["data"][0]  # Upscale typically returns single image
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
    **kwargs
) -> ImageGeneration:
    """Convenience function to generate a single image."""
    if client is None:
        from .config import load_config
        from .venice_client import VeniceClient
        config = load_config()
        client = VeniceClient(config)
    
    api = ImageAPI(client)
    return api.generate(prompt, **kwargs)


def edit_image(
    image: Union[str, bytes, Path],
    prompt: str,
    client: Optional[HTTPClient] = None,
    **kwargs
) -> ImageEditResult:
    """Convenience function to edit an image."""
    if client is None:
        from .config import load_config
        from .venice_client import VeniceClient
        config = load_config()
        client = VeniceClient(config)
    
    api = ImageEditAPI(client)
    return api.edit(image, prompt, **kwargs)


def upscale_image(
    image: Union[str, bytes, Path],
    client: Optional[HTTPClient] = None,
    **kwargs
) -> ImageUpscaleResult:
    """Convenience function to upscale an image."""
    if client is None:
        from .config import load_config
        from .venice_client import VeniceClient
        config = load_config()
        client = VeniceClient(config)
    
    api = ImageUpscaleAPI(client)
    return api.upscale(image, **kwargs)
