# Audio API

The Audio API provides text-to-speech synthesis capabilities with multiple voices and formats.

## Overview

The Audio API allows you to convert text into natural-sounding speech using various AI models and voice options.

## Basic Usage

```python
from venice_sdk import VeniceClient

client = VeniceClient()
audio = client.audio  # AudioAPI instance
```

## Methods

### `speech(input_text: str, voice: str = "alloy", model: str = "tts-kokoro", response_format: str = "mp3", speed: float = 1.0, user: Optional[str] = None, **kwargs) -> AudioResult`

Convert text to speech.

```python
# Basic text-to-speech
audio_result = audio.speech(
    input_text="Hello from Venice AI!",
    voice="alloy",
    model="tts-kokoro"
)

# Save to file
audio_result.save("hello.mp3")

# Get audio data
audio_data = audio_result.get_audio_data()
print(f"Audio size: {len(audio_data)} bytes")
```

**Parameters:**
- `input_text` (str) - Text to convert to speech
- `voice` (str) - Voice to use (default: "alloy")
- `model` (str) - TTS model to use (default: "tts-kokoro")
- `response_format` (str) - Audio format: "mp3", "wav", "aac", "flac" (default: "mp3")
- `speed` (float) - Speech speed multiplier (0.25 to 4.0, default: 1.0)
- `user` (Optional[str]) - User identifier for tracking
- `**kwargs` - Additional model-specific parameters

**Returns:**
- `AudioResult` - Audio result object

**Raises:**
- `ValueError` - If parameters are invalid
- `AudioError` - If synthesis fails

### `get_voices() -> List[Voice]`

Get available voices.

```python
voices = audio.get_voices()
for voice in voices:
    print(f"Voice: {voice.name}")
    print(f"Description: {voice.description}")
    print(f"Gender: {voice.gender}")
    print(f"Language: {voice.language}")
```

**Returns:**
- `List[Voice]` - List of available voices

### `speech_batch(texts: List[str], voice: str = "alloy", **kwargs) -> List[AudioResult]`

Convert multiple texts to speech.

```python
texts = [
    "Welcome to Venice AI",
    "This is a test of batch processing",
    "Thank you for using our service"
]

results = audio.speech_batch(
    texts=texts,
    voice="alloy",
    model="tts-kokoro"
)

for i, result in enumerate(results):
    result.save(f"batch_{i}.mp3")
```

**Parameters:**
- `texts` (List[str]) - List of texts to convert
- `voice` (str) - Voice to use for all texts
- `**kwargs` - Additional parameters passed to speech()

**Returns:**
- `List[AudioResult]` - List of audio results

## Data Classes

### AudioResult

Represents the result of audio synthesis.

```python
@dataclass
class AudioResult:
    audio_data: bytes
    format: str
    duration: Optional[float]
    model: Optional[str]
    voice: Optional[str]
    
    def save(self, path: Union[str, Path]) -> Path:
        """Save the audio to a file."""
        
    def get_audio_data(self) -> bytes:
        """Get the raw audio data as bytes."""
        
    def get_duration(self) -> Optional[float]:
        """Get the audio duration in seconds."""
```

### Voice

Represents an available voice.

```python
@dataclass
class Voice:
    name: str
    description: str
    gender: str
    language: str
    accent: Optional[str]
    age_range: Optional[str]
    sample_url: Optional[str]
```

## Advanced Usage

### Custom Voice Selection

```python
# Get all available voices
voices = audio.get_voices()

# Filter by gender
female_voices = [v for v in voices if v.gender.lower() == "female"]

# Filter by language
english_voices = [v for v in voices if v.language.lower() == "english"]

# Use a specific voice
selected_voice = next(v for v in voices if v.name == "alloy")
audio_result = audio.speech(
    input_text="Hello world",
    voice=selected_voice.name
)
```

### Different Audio Formats

```python
# MP3 (default)
mp3_result = audio.speech(
    input_text="MP3 format",
    response_format="mp3"
)

# WAV (uncompressed)
wav_result = audio.speech(
    input_text="WAV format",
    response_format="wav"
)

# AAC (compressed)
aac_result = audio.speech(
    input_text="AAC format",
    response_format="aac"
)

# FLAC (lossless)
flac_result = audio.speech(
    input_text="FLAC format",
    response_format="flac"
)
```

### Speed Control

```python
# Slow speech
slow_result = audio.speech(
    input_text="This is slow speech",
    speed=0.5
)

# Fast speech
fast_result = audio.speech(
    input_text="This is fast speech",
    speed=2.0
)

# Normal speed (default)
normal_result = audio.speech(
    input_text="This is normal speed",
    speed=1.0
)
```

### Batch Processing

```python
from venice_sdk import AudioBatchProcessor

# Create a batch processor
processor = AudioBatchProcessor(audio)

# Process multiple texts
texts = [
    "First message",
    "Second message",
    "Third message"
]

results = processor.process_batch(
    texts=texts,
    voice="alloy",
    output_dir="audio_output"
)

print(f"Generated {len(results)} audio files")
```

## Error Handling

```python
from venice_sdk.errors import AudioError, VeniceAPIError

try:
    result = audio.speech(
        input_text="Hello world",
        voice="alloy"
    )
except ValueError as e:
    print(f"Invalid parameter: {e}")
except AudioError as e:
    print(f"Audio synthesis failed: {e}")
except VeniceAPIError as e:
    print(f"API error: {e}")
```

## Examples

### Complete Audio Workflow

```python
from venice_sdk import VeniceClient
from pathlib import Path

client = VeniceClient()

# 1. Get available voices
print("Available voices:")
voices = client.audio.get_voices()
for voice in voices[:5]:  # Show first 5
    print(f"- {voice.name}: {voice.description}")

# 2. Generate speech
print("\nGenerating speech...")
result = client.audio.speech(
    input_text="Hello from Venice AI! This is a test of text-to-speech synthesis.",
    voice="alloy",
    model="tts-kokoro",
    response_format="mp3"
)

# 3. Save the audio
output_path = "welcome.mp3"
result.save(output_path)
print(f"Audio saved to: {output_path}")

# 4. Get audio information
print(f"Format: {result.format}")
print(f"Duration: {result.get_duration()} seconds")
print(f"Size: {len(result.get_audio_data())} bytes")
```

### Multi-Voice Audio Generation

```python
def generate_multi_voice_audio():
    """Generate audio with different voices."""
    client = VeniceClient()
    
    # Text for different speakers
    script = [
        ("alloy", "Welcome to our presentation."),
        ("echo", "Today we'll discuss AI technology."),
        ("fable", "Let's start with the basics."),
        ("onyx", "AI is transforming many industries."),
        ("nova", "Thank you for your attention."),
        ("shimmer", "Any questions?")
    ]
    
    # Generate audio for each speaker
    audio_files = []
    for i, (voice, text) in enumerate(script):
        result = client.audio.speech(
            input_text=text,
            voice=voice,
            model="tts-kokoro"
        )
        
        filename = f"speaker_{i+1}_{voice}.mp3"
        result.save(filename)
        audio_files.append(filename)
        print(f"Generated: {filename}")
    
    return audio_files

# Run the multi-voice generation
files = generate_multi_voice_audio()
print(f"Generated {len(files)} audio files")
```

### Audio Processing Pipeline

```python
def audio_processing_pipeline(text: str, output_dir: str = "audio_output"):
    """Complete audio processing pipeline."""
    client = VeniceClient()
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Step 1: Generate with different voices
    voices = ["alloy", "echo", "fable"]
    results = []
    
    for voice in voices:
        result = client.audio.speech(
            input_text=text,
            voice=voice,
            model="tts-kokoro"
        )
        
        filename = output_path / f"{voice}.mp3"
        result.save(filename)
        results.append((voice, filename))
        print(f"Generated {voice}: {filename}")
    
    # Step 2: Generate with different speeds
    speeds = [0.5, 1.0, 2.0]
    for speed in speeds:
        result = client.audio.speech(
            input_text=text,
            voice="alloy",
            speed=speed
        )
        
        filename = output_path / f"speed_{speed}x.mp3"
        result.save(filename)
        print(f"Generated speed {speed}x: {filename}")
    
    # Step 3: Generate with different formats
    formats = ["mp3", "wav", "aac"]
    for format in formats:
        result = client.audio.speech(
            input_text=text,
            voice="alloy",
            response_format=format
        )
        
        filename = output_path / f"format_{format}.{format}"
        result.save(filename)
        print(f"Generated {format}: {filename}")
    
    print(f"Pipeline complete! Check {output_dir}/")
    return results

# Run the pipeline
pipeline_results = audio_processing_pipeline(
    "This is a comprehensive test of the Venice AI audio system.",
    "audio_pipeline_output"
)
```

## Best Practices

1. **Choose Appropriate Voices**: Different voices work better for different content types
2. **Optimize Text Length**: Very long texts may hit rate limits
3. **Use Batch Processing**: For multiple texts, use batch methods
4. **Format Selection**: Choose the right format for your use case
5. **Speed Control**: Test different speeds to find the best fit
6. **Error Handling**: Always handle potential errors gracefully
7. **File Management**: Use descriptive filenames and organize outputs

## Troubleshooting

### Common Issues

**"Voice not found"**
- Check available voices with `get_voices()`
- Ensure the voice name is spelled correctly
- Try using a different voice

**"Invalid speed"**
- Speed must be between 0.25 and 4.0
- Use 1.0 for normal speed

**"Unsupported format"**
- Check supported formats: mp3, wav, aac, flac
- Ensure the format is lowercase

**"Audio generation failed"**
- Check your API key and permissions
- Verify you have sufficient credits
- Try with a shorter text

**"Rate limit exceeded"**
- Wait for the rate limit to reset
- Implement exponential backoff
- Consider using batch processing
