# Video API

The Video API provides comprehensive video generation capabilities, supporting both text-to-video and image-to-video generation using state-of-the-art AI models.

## Overview

The Video API includes:

- **`VideoAPI`** - Video generation from text prompts or images
- **`VideoJob`** - Represents a video generation job with status tracking
- **`VideoQuote`** - Price estimates for video generation
- **`VideoMetadata`** - Video file metadata and properties

## Video Generation

### VideoAPI

Generate videos from text descriptions or animate static images into video clips.

```python
from venice_sdk import VeniceClient

client = VeniceClient()
video = client.video  # VideoAPI instance
```

#### Methods

##### `queue(model: str, prompt: Optional[str] = None, image: Optional[Union[str, bytes, Path]] = None, duration: Optional[Union[int, str]] = None, resolution: Optional[str] = None, audio: bool = False, seed: Optional[int] = None, negative_prompt: Optional[str] = None, aspect_ratio: Optional[str] = None, fps: Optional[int] = None, motion_bucket_id: Optional[int] = None, guidance_scale: Optional[float] = None, **kwargs) -> VideoJob`

Queue a video generation job for asynchronous processing.

```python
# Text-to-video generation
job = video.queue(
    model="kling-2.6-pro-text-to-video",
    prompt="A serene sunset over a calm ocean with gentle waves",
    duration=5,  # or "5s"
    aspect_ratio="16:9",
    resolution="1080p"
)

print(f"Job ID: {job.job_id}")
print(f"Status: {job.status}")

# Image-to-video generation
job = video.queue(
    model="kling-2.6-pro-image-to-video",
    image="path/to/image.png",  # or URL or bytes
    prompt="Animate this image with gentle movement",
    duration=5
)
```

**Parameters:**

- `model` (str, required): Video model ID (e.g., "kling-2.6-pro-text-to-video", "sora-2-text-to-video")
- `prompt` (str, optional): Text description of the video (required for text-to-video)
- `image` (str/bytes/Path, optional): Image file path, URL, or bytes (required for image-to-video)
- `duration` (int/str, optional): Video duration in seconds (e.g., 5 or "5s")
- `resolution` (str, optional): Video resolution (e.g., "720p", "1080p", "4k")
- `audio` (bool, optional): Whether to include audio (default: False)
- `seed` (int, optional): Random seed for reproducible results
- `negative_prompt` (str, optional): Text describing what should not appear
- `aspect_ratio` (str, optional): Desired aspect ratio (e.g., "16:9", "9:16", "1:1")
- `fps` (int, optional): Frames per second (e.g., 24, 30, 60)
- `motion_bucket_id` (int, optional): Motion intensity for image-to-video (1-127)
- `guidance_scale` (float, optional): How closely to follow the prompt

**Returns:**

- `VideoJob`: Job object with `job_id` and initial status

**Raises:**

- `VideoGenerationError`: If request fails or parameters are invalid

##### `retrieve(job_id: str) -> VideoJob`

Retrieve the status of a video generation job.

```python
# Check job status
job = video.retrieve("job_123")

print(f"Status: {job.status}")
print(f"Progress: {job.progress}%")

if job.is_completed():
    print(f"Video URL: {job.video_url}")
elif job.is_failed():
    print(f"Error: {job.error}")
```

**Parameters:**

- `job_id` (str, required): The job ID returned from `queue()`

**Returns:**

- `VideoJob`: Updated job object with current status

**Raises:**

- `VideoGenerationError`: If job not found or request fails

##### `wait_for_completion(job_id: str, poll_interval: int = 5, max_wait_time: Optional[int] = None, callback: Optional[Callable[[VideoJob], None]] = None) -> VideoJob`

Wait for a video generation job to complete by polling.

```python
# Wait for completion with progress callback
def progress_callback(job):
    print(f"Status: {job.status}, Progress: {job.progress}%")

completed_job = video.wait_for_completion(
    job.job_id,
    poll_interval=5,
    max_wait_time=300,  # 5 minutes
    callback=progress_callback
)

if completed_job.is_completed():
    print(f"Video ready: {completed_job.video_url}")
```

**Parameters:**

- `job_id` (str, required): The job ID to wait for
- `poll_interval` (int, optional): Seconds between status checks (default: 5)
- `max_wait_time` (int, optional): Maximum seconds to wait (default: None, wait indefinitely)
- `callback` (Callable, optional): Function called on each status update

**Returns:**

- `VideoJob`: Completed job object

**Raises:**

- `VideoGenerationError`: If job fails or timeout is reached

##### `quote(model: str, prompt: Optional[str] = None, image: Optional[Union[str, bytes, Path]] = None, duration: Optional[Union[int, str]] = None, resolution: Optional[str] = None, audio: bool = False, **kwargs) -> VideoQuote`

Get a price estimate for video generation before submitting the job.

```python
# Get quote for text-to-video
quote = video.quote(
    model="kling-2.6-pro-text-to-video",
    prompt="A beautiful sunset",
    duration=5,
    resolution="1080p"
)

print(f"Estimated cost: ${quote.estimated_cost} {quote.currency}")
print(f"Estimated duration: {quote.estimated_duration} seconds")

if quote.pricing_breakdown:
    print(f"Base cost: ${quote.pricing_breakdown.get('base_cost', 0)}")
    print(f"Duration cost: ${quote.pricing_breakdown.get('duration_cost', 0)}")
```

**Parameters:**

- Same as `queue()` method

**Returns:**

- `VideoQuote`: Quote object with cost and duration estimates

**Raises:**

- `VideoGenerationError`: If request fails

##### `complete(model: str, prompt: Optional[str] = None, image: Optional[Union[str, bytes, Path]] = None, duration: Optional[Union[int, str]] = None, resolution: Optional[str] = None, audio: bool = False, timeout: int = 900, **kwargs) -> VideoJob`

Generate a video synchronously (queue and wait for completion in one call).

```python
# Synchronous video generation
job = video.complete(
    model="kling-2.6-pro-text-to-video",
    prompt="A cat playing with yarn",
    duration=5,
    aspect_ratio="16:9",
    timeout=600  # 10 minutes
)

if job.is_completed():
    print(f"Video ready: {job.video_url}")
    # Download the video
    job.download("output.mp4")
```

**Parameters:**

- Same as `queue()` method, plus:
- `timeout` (int, optional): Maximum seconds to wait (default: 900 = 15 minutes)

**Returns:**

- `VideoJob`: Completed job object

**Raises:**

- `VideoGenerationError`: If generation fails or timeout is reached

## VideoJob

Represents a video generation job with status tracking and download capabilities.

### Properties

- `job_id` (str): Unique job identifier
- `status` (str): Current status ("queued", "processing", "completed", "failed")
- `progress` (float): Completion percentage (0-100)
- `video_url` (str, optional): URL to download the completed video
- `video_id` (str, optional): Video identifier
- `created_at` (str, optional): Job creation timestamp
- `started_at` (str, optional): Processing start timestamp
- `completed_at` (str, optional): Completion timestamp
- `error` (str, optional): Error message if failed
- `error_code` (str, optional): Error code if failed
- `model` (str, optional): Model used for generation
- `metadata` (VideoMetadata, optional): Video file metadata

### Methods

##### `is_completed() -> bool`

Check if the job has completed successfully.

```python
if job.is_completed():
    print("Video is ready!")
```

##### `is_failed() -> bool`

Check if the job has failed.

```python
if job.is_failed():
    print(f"Generation failed: {job.error}")
```

##### `is_processing() -> bool`

Check if the job is still processing (queued or processing).

```python
if job.is_processing():
    print("Video is still being generated...")
```

##### `download(output_path: Union[str, Path]) -> Path`

Download the completed video to a file.

```python
# Download video
saved_path = job.download("my_video.mp4")
print(f"Video saved to: {saved_path}")

# Download to Path object
from pathlib import Path
output = Path("videos") / "output.mp4"
saved_path = job.download(output)
```

**Parameters:**

- `output_path` (str/Path): Destination file path

**Returns:**

- `Path`: Path to the saved file

**Raises:**

- `VideoGenerationError`: If job not completed or download fails

##### `get_video_data() -> bytes`

Get the video file data as bytes.

```python
# Get video data
video_data = job.get_video_data()
print(f"Video size: {len(video_data)} bytes")

# Save manually
with open("video.mp4", "wb") as f:
    f.write(video_data)
```

**Returns:**

- `bytes`: Video file data

**Raises:**

- `VideoGenerationError`: If job not completed or download fails

## VideoQuote

Represents a price estimate for video generation.

### Properties

- `estimated_cost` (float): Estimated cost in the specified currency
- `currency` (str): Currency code (e.g., "USD", "EUR", "GBP")
- `estimated_duration` (int, optional): Estimated generation time in seconds
- `pricing_breakdown` (dict, optional): Detailed cost breakdown
- `cost_components` (list, optional): Array of cost component objects
- `pricing_model` (str, optional): Pricing model used
- `minimum_cost` (float, optional): Minimum cost for this generation type
- `maximum_cost` (float, optional): Maximum cost estimate

## VideoMetadata

Represents metadata about a generated video file.

### Properties

- `duration` (float, optional): Video duration in seconds
- `resolution` (str, optional): Video resolution (e.g., "1080p")
- `fps` (int, optional): Frames per second
- `format` (str, optional): Video format (e.g., "mp4")
- `file_size` (int, optional): File size in bytes

## Examples

### Basic Text-to-Video Generation

```python
from venice_sdk import VeniceClient

client = VeniceClient()

# Queue a video generation job
job = client.video.queue(
    model="kling-2.6-pro-text-to-video",
    prompt="A serene sunset over a calm ocean with gentle waves",
    duration=5,
    aspect_ratio="16:9",
    resolution="1080p"
)

# Wait for completion
completed_job = client.video.wait_for_completion(
    job.job_id,
    poll_interval=5,
    max_wait_time=300
)

# Download the video
if completed_job.is_completed():
    completed_job.download("sunset_video.mp4")
```

### Image-to-Video Animation

```python
# Generate an image first
image = client.images.generate(
    prompt="A serene mountain landscape at sunset",
    model="dall-e-3"
)

# Animate the image
job = client.video.queue(
    model="kling-2.6-pro-image-to-video",
    image=image.url,  # Use the generated image URL
    prompt="Animate with gentle movement and flowing clouds",
    duration=5,
    resolution="720p"
)

# Wait and download
completed_job = client.video.wait_for_completion(job.job_id)
if completed_job.is_completed():
    completed_job.download("animated_landscape.mp4")
```

### Getting Price Quotes

```python
# Get quote before generating
quote = client.video.quote(
    model="kling-2.6-pro-text-to-video",
    prompt="A cat playing with yarn",
    duration=10,
    resolution="1080p",
    audio=True
)

print(f"Estimated cost: ${quote.estimated_cost} {quote.currency}")
print(f"Estimated generation time: {quote.estimated_duration} seconds")

# Compare quotes for different durations
for duration in [5, 10]:
    quote = client.video.quote(
        model="kling-2.6-pro-text-to-video",
        prompt="Test video",
        duration=duration,
        aspect_ratio="16:9"
    )
    print(f"{duration}s video: ${quote.estimated_cost}")
```

### Synchronous Generation

```python
# Generate video synchronously (waits for completion)
job = client.video.complete(
    model="kling-2.6-pro-text-to-video",
    prompt="A quick test video",
    duration=5,
    aspect_ratio="16:9",
    timeout=600  # 10 minutes max
)

if job.is_completed():
    print(f"Video URL: {job.video_url}")
    job.download("test_video.mp4")
```

### Progress Tracking with Callback

```python
def track_progress(job):
    status_emoji = {
        "queued": "⏳",
        "processing": "⚙️",
        "completed": "✅",
        "failed": "❌"
    }
    emoji = status_emoji.get(job.status, "❓")
    print(f"{emoji} {job.status} - {job.progress}%")

job = client.video.queue(
    model="kling-2.6-pro-text-to-video",
    prompt="A beautiful animation",
    duration=5
)

completed_job = client.video.wait_for_completion(
    job.job_id,
    poll_interval=3,
    callback=track_progress
)
```

### Error Handling

```python
from venice_sdk.errors import VideoGenerationError, VeniceAPIError

try:
    job = client.video.queue(
        model="kling-2.6-pro-text-to-video",
        prompt="Test video",
        duration=5
    )
    
    completed_job = client.video.wait_for_completion(job.job_id)
    
    if completed_job.is_completed():
        completed_job.download("video.mp4")
    elif completed_job.is_failed():
        print(f"Generation failed: {completed_job.error}")
        
except VideoGenerationError as e:
    print(f"Video generation error: {e}")
except VeniceAPIError as e:
    print(f"API error: {e.status_code} - {e}")
```

## Available Video Models

Common video models include:

### Text-to-Video Models
- `kling-2.6-pro-text-to-video` - High-quality text-to-video generation
- `kling-2.5-turbo-pro-text-to-video` - Faster variant
- `sora-2-text-to-video` - Advanced text-to-video model
- `sora-2-pro-text-to-video` - Professional-grade variant
- `veo3-full-text-to-video` - Full-featured Google Veo 3 model
- `veo3-fast-text-to-video` - Faster Veo 3 variant
- `wan-2.5-preview-text-to-video` - Preview model
- `ltx-2-full-text-to-video` - Full-featured LTX-2 model
- `longcat-text-to-video` - LongCat model

### Image-to-Video Models
- `kling-2.6-pro-image-to-video` - High-quality image animation
- `sora-2-image-to-video` - Advanced image-to-video model
- `veo3-full-image-to-video` - Full-featured Veo 3 model
- `wan-2.5-preview-image-to-video` - Preview model
- `ltx-2-full-image-to-video` - Full-featured LTX-2 model

To see all available video models, use the Models API:

```python
models = client.models.list()
video_models = [m for m in models if m.get("type") == "video"]
for model in video_models:
    print(f"{model['id']}: {model.get('name', 'N/A')}")
```

## Best Practices

1. **Use Quotes First**: Always get a quote before generating to estimate costs
2. **Async Pattern**: Use `queue()` + `wait_for_completion()` for production applications
3. **Timeout Handling**: Set appropriate timeouts based on video duration and model
4. **Error Handling**: Always check job status and handle failures gracefully
5. **Progress Tracking**: Use callbacks to track generation progress
6. **Model Selection**: Choose models based on quality vs speed requirements
7. **Duration Limits**: Check model documentation for supported duration ranges
8. **Resolution**: Higher resolutions cost more and take longer to generate

## Cost Considerations

- Video generation costs vary by model, duration, and resolution
- Use the `quote()` method to estimate costs before generation
- Longer durations and higher resolutions typically cost more
- Audio generation adds additional cost
- "Fast" model variants are cheaper but may have lower quality

