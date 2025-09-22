# Images API

The Images API provides comprehensive image generation, editing, and processing capabilities using various AI models.

## Overview

The Images API includes several specialized classes:

- **`ImagesAPI`** - Image generation from text prompts
- **`ImageEditAPI`** - Image editing and modification
- **`ImageUpscaleAPI`** - Image upscaling and enhancement
- **`ImageStylesAPI`** - Artistic style management

## Image Generation

### ImagesAPI

Generate images from text descriptions using various AI models.

```python
from venice_sdk import VeniceClient

client = VeniceClient()
images = client.images  # ImagesAPI instance
```

#### Methods

##### `generate(prompt: str, model: str = "dall-e-3", n: int = 1, size: str = "1024x1024", quality: str = "standard", response_format: str = "url", user: Optional[str] = None, **kwargs) -> ImageGenerationResult`

Generate images from a text prompt.

```python
# Basic image generation
result = images.generate(
    prompt="A serene mountain landscape at sunset",
    model="dall-e-3",
    size="1024x1024",
    quality="hd"
)

# Save the image
result.save("mountain.png")

# Access image data
image_data = result.get_image_data()
print(f"Image size: {len(image_data)} bytes")
```

**Parameters:**
- `prompt` (str) - Text description of the image to generate
- `model` (str) - Model to use for generation (default: "dall-e-3")
- `n` (int) - Number of images to generate (1-10, default: 1)
- `size` (str) - Image size: "256x256", "512x512", "1024x1024", "1792x1024", "1024x1792" (default: "1024x1024")
- `quality` (str) - Image quality: "standard", "hd" (default: "standard")
- `response_format` (str) - Response format: "url", "b64_json" (default: "url")
- `user` (Optional[str]) - User identifier for tracking
- `**kwargs` - Additional model-specific parameters

**Returns:**
- `ImageGenerationResult` - Generated image result object

**Raises:**
- `ValueError` - If parameters are invalid
- `ImageGenerationError` - If generation fails

##### `generate_batch(prompts: List[str], **kwargs) -> List[ImageGenerationResult]`

Generate multiple images from multiple prompts.

```python
prompts = [
    "A cat sitting on a windowsill",
    "A dog playing in the park",
    "A bird flying over the ocean"
]

results = images.generate_batch(
    prompts=prompts,
    model="dall-e-3",
    size="512x512"
)

for i, result in enumerate(results):
    result.save(f"image_{i}.png")
```

**Parameters:**
- `prompts` (List[str]) - List of text descriptions
- `**kwargs` - Additional parameters passed to generate()

**Returns:**
- `List[ImageGenerationResult]` - List of generated image results

## Image Editing

### ImageEditAPI

Edit and modify existing images using AI.

```python
image_edit = client.image_edit  # ImageEditAPI instance
```

#### Methods

##### `edit(image: Union[str, Path, bytes], prompt: str, model: str = "dall-e-2-edit", n: int = 1, size: str = "1024x1024", response_format: str = "url", user: Optional[str] = None, **kwargs) -> ImageEditResult`

Edit an existing image based on a text prompt.

```python
# Edit an image from file path
result = image_edit.edit(
    image="path/to/image.png",
    prompt="Add a rainbow in the sky",
    model="dall-e-2-edit",
    size="1024x1024"
)

# Save the edited image
result.save("edited_image.png")

# Edit from URL
result = image_edit.edit(
    image="https://example.com/image.jpg",
    prompt="Make it look like a painting"
)
```

**Parameters:**
- `image` (Union[str, Path, bytes]) - Image to edit (file path, URL, or bytes)
- `prompt` (str) - Description of the desired changes
- `model` (str) - Model to use for editing (default: "dall-e-2-edit")
- `n` (int) - Number of edited images to generate (default: 1)
- `size` (str) - Output image size (default: "1024x1024")
- `response_format` (str) - Response format: "url", "b64_json" (default: "url")
- `user` (Optional[str]) - User identifier for tracking
- `**kwargs` - Additional model-specific parameters

**Returns:**
- `ImageEditResult` - Edited image result object

## Image Upscaling

### ImageUpscaleAPI

Upscale and enhance image resolution.

```python
image_upscale = client.image_upscale  # ImageUpscaleAPI instance
```

#### Methods

##### `upscale(image: Union[str, Path, bytes], scale: int = 2, model: str = "real-esrgan", response_format: str = "url", user: Optional[str] = None, **kwargs) -> ImageUpscaleResult`

Upscale an image to higher resolution.

```python
# Upscale an image
result = image_upscale.upscale(
    image="small_image.png",
    scale=4,  # 4x upscaling
    model="real-esrgan"
)

# Save the upscaled image
result.save("upscaled_image.png")

# Upscale from URL
result = image_upscale.upscale(
    image="https://example.com/small.jpg",
    scale=2
)
```

**Parameters:**
- `image` (Union[str, Path, bytes]) - Image to upscale
- `scale` (int) - Upscaling factor (default: 2)
- `model` (str) - Model to use for upscaling (default: "real-esrgan")
- `response_format` (str) - Response format: "url", "b64_json" (default: "url")
- `user` (Optional[str]) - User identifier for tracking
- `**kwargs` - Additional model-specific parameters

**Returns:**
- `ImageUpscaleResult` - Upscaled image result object

## Image Styles

### ImageStylesAPI

Manage and access artistic style presets.

```python
image_styles = client.image_styles  # ImageStylesAPI instance
```

#### Methods

##### `list_styles() -> List[ImageStyle]`

Get available artistic styles.

```python
styles = image_styles.list_styles()
for style in styles:
    print(f"Style: {style.name}")
    print(f"Description: {style.description}")
    print(f"Category: {style.category}")
```

**Returns:**
- `List[ImageStyle]` - List of available styles

##### `get_style(style_id: str) -> Optional[ImageStyle]`

Get a specific style by ID.

```python
style = image_styles.get_style("anime")
if style:
    print(f"Found style: {style.name}")
    print(f"Description: {style.description}")
```

**Parameters:**
- `style_id` (str) - Style identifier

**Returns:**
- `Optional[ImageStyle]` - Style object if found, None otherwise

## Data Classes

### ImageGenerationResult

Represents the result of image generation.

```python
@dataclass
class ImageGenerationResult:
    url: Optional[str]
    b64_json: Optional[str]
    revised_prompt: Optional[str]
    created: Optional[int]
    model: Optional[str]
    
    def save(self, path: Union[str, Path]) -> Path:
        """Save the image to a file."""
        
    def get_image_data(self) -> bytes:
        """Get the raw image data as bytes."""
```

### ImageEditResult

Represents the result of image editing.

```python
@dataclass
class ImageEditResult:
    url: Optional[str]
    b64_json: Optional[str]
    revised_prompt: Optional[str]
    created: Optional[int]
    model: Optional[str]
    
    def save(self, path: Union[str, Path]) -> Path:
        """Save the edited image to a file."""
        
    def get_image_data(self) -> bytes:
        """Get the raw image data as bytes."""
```

### ImageUpscaleResult

Represents the result of image upscaling.

```python
@dataclass
class ImageUpscaleResult:
    url: Optional[str]
    b64_json: Optional[str]
    created: Optional[int]
    model: Optional[str]
    scale: Optional[int]
    
    def save(self, path: Union[str, Path]) -> Path:
        """Save the upscaled image to a file."""
        
    def get_image_data(self) -> bytes:
        """Get the raw image data as bytes."""
```

### ImageStyle

Represents an artistic style.

```python
@dataclass
class ImageStyle:
    id: str
    name: str
    description: str
    category: str
    preview_url: Optional[str]
    parameters: Dict[str, Any]
```

## Advanced Usage

### Batch Processing

Process multiple images efficiently:

```python
from venice_sdk import ImageBatchProcessor

# Create a batch processor
processor = ImageBatchProcessor(client.images)

# Process multiple prompts
prompts = [
    "A futuristic cityscape",
    "A peaceful forest scene",
    "An abstract art piece"
]

results = processor.process_batch(
    prompts=prompts,
    model="dall-e-3",
    size="1024x1024"
)

# Save all results
for i, result in enumerate(results):
    result.save(f"batch_image_{i}.png")
```

### Data URL Support

Handle base64-encoded images:

```python
# Generate image with base64 response
result = images.generate(
    prompt="A beautiful sunset",
    response_format="b64_json"
)

# The result automatically handles data URLs
if result.b64_json:
    # Save from base64 data
    result.save("sunset.png")
    
    # Get raw bytes
    image_data = result.get_image_data()
    print(f"Image size: {len(image_data)} bytes")
```

### Custom Models

Use different models for different purposes:

```python
# High-quality generation
hd_result = images.generate(
    prompt="A detailed portrait",
    model="dall-e-3",
    quality="hd",
    size="1792x1024"
)

# Fast generation
fast_result = images.generate(
    prompt="A simple sketch",
    model="stable-diffusion-3.5",
    size="512x512"
)

# Artistic style
artistic_result = images.generate(
    prompt="A landscape in Van Gogh style",
    model="midjourney-v6",
    size="1024x1024"
)
```

## Error Handling

Handle various error conditions:

```python
from venice_sdk.errors import ImageGenerationError, InvalidRequestError

try:
    result = images.generate(
        prompt="A beautiful image",
        model="dall-e-3"
    )
except ValueError as e:
    print(f"Invalid parameter: {e}")
except InvalidRequestError as e:
    print(f"Invalid request: {e}")
except ImageGenerationError as e:
    print(f"Generation failed: {e}")
```

## Examples

### Complete Image Workflow

```python
from venice_sdk import VeniceClient
from pathlib import Path

client = VeniceClient()

# 1. Generate an image
print("Generating image...")
result = client.images.generate(
    prompt="A serene mountain landscape at sunset",
    model="dall-e-3",
    size="1024x1024",
    quality="hd"
)

# Save the original
result.save("original.png")
print("Original image saved")

# 2. Edit the image
print("Editing image...")
edited = client.image_edit.edit(
    image="original.png",
    prompt="Add a rainbow in the sky",
    model="dall-e-2-edit"
)

edited.save("edited.png")
print("Edited image saved")

# 3. Upscale the edited image
print("Upscaling image...")
upscaled = client.image_upscale.upscale(
    image="edited.png",
    scale=2,
    model="real-esrgan"
)

upscaled.save("final.png")
print("Final upscaled image saved")

# 4. List available styles
print("Available styles:")
styles = client.image_styles.list_styles()
for style in styles[:5]:  # Show first 5
    print(f"- {style.name}: {style.description}")
```

### Image Processing Pipeline

```python
from venice_sdk import VeniceClient
import asyncio

async def process_image_pipeline(prompt: str, output_dir: str = "output"):
    """Complete image processing pipeline."""
    client = VeniceClient()
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Step 1: Generate base image
    print(f"Generating: {prompt}")
    generated = client.images.generate(
        prompt=prompt,
        model="dall-e-3",
        size="1024x1024"
    )
    generated.save(output_path / "01_generated.png")
    
    # Step 2: Apply artistic style
    print("Applying artistic style...")
    styled = client.image_edit.edit(
        image=output_path / "01_generated.png",
        prompt="Apply impressionist painting style",
        model="dall-e-2-edit"
    )
    styled.save(output_path / "02_styled.png")
    
    # Step 3: Upscale for high resolution
    print("Upscaling...")
    upscaled = client.image_upscale.upscale(
        image=output_path / "02_styled.png",
        scale=2
    )
    upscaled.save(output_path / "03_final.png")
    
    print(f"Pipeline complete! Check {output_dir}/")
    return output_path / "03_final.png"

# Run the pipeline
final_image = asyncio.run(process_image_pipeline(
    "A cyberpunk cityscape at night",
    "cyberpunk_output"
))
```

## Best Practices

1. **Choose Appropriate Models**: Different models excel at different types of images
2. **Optimize Prompts**: Clear, descriptive prompts yield better results
3. **Batch Processing**: Use batch methods for multiple images
4. **Error Handling**: Always handle potential errors gracefully
5. **File Management**: Use descriptive filenames and organize outputs
6. **Quality vs Speed**: Balance quality settings with processing time
7. **Cost Management**: Monitor usage to control costs

## Troubleshooting

### Common Issues

**"Invalid prompt"**
- Ensure the prompt is descriptive and clear
- Avoid overly long or complex prompts
- Check for inappropriate content

**"Model not available"**
- Verify the model name is correct
- Check if the model is available in your region
- Try alternative models

**"Image generation failed"**
- Check your API key and permissions
- Verify you have sufficient credits
- Try with a simpler prompt

**"File not found"**
- Ensure the image file path is correct
- Check file permissions
- Verify the file format is supported

**"Rate limit exceeded"**
- Wait for the rate limit to reset
- Implement exponential backoff
- Consider upgrading your plan
