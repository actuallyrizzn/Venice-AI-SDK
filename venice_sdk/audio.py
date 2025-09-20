"""
Venice AI SDK - Audio and Speech Module

This module provides text-to-speech capabilities using the Venice AI API.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Generator
import io

from .client import HTTPClient
from .errors import VeniceAPIError, AudioGenerationError
from .config import load_config

try:
    import pygame
except ImportError:
    pygame = None


@dataclass
class Voice:
    """Represents an available voice for text-to-speech."""
    id: str
    name: str
    description: Optional[str] = None
    language: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[str] = None


@dataclass
class AudioResult:
    """Represents an audio generation result."""
    audio_data: bytes
    format: str
    duration: Optional[float] = None
    sample_rate: Optional[int] = None
    
    def save(self, path: Union[str, Path]) -> Path:
        """Save the audio data to a file."""
        path = Path(path)
        path.write_bytes(self.audio_data)
        return path
    
    def play(self) -> None:
        """Play the audio (requires pygame or similar)."""
        if pygame is None:
            raise AudioGenerationError("pygame is required for audio playback. Install with: pip install pygame")
        
        pygame.mixer.init()
        audio_file = io.BytesIO(self.audio_data)
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()


class AudioAPI:
    """Audio and speech synthesis API client."""
    
    # Available voices
    VOICES = {
        "af_alloy": Voice(
            id="af_alloy",
            name="Alloy",
            description="Neutral, balanced voice",
            gender="neutral"
        ),
        "af_aoede": Voice(
            id="af_aoede",
            name="Aoede",
            description="Warm, friendly voice",
            gender="male"
        ),
        "af_bella": Voice(
            id="af_bella",
            name="Bella",
            description="Professional, clear voice",
            gender="male"
        ),
        "af_heart": Voice(
            id="af_heart",
            name="Heart",
            description="Deep, authoritative voice",
            gender="male"
        ),
        "af_jadzia": Voice(
            id="af_jadzia",
            name="Jadzia",
            description="Bright, energetic voice",
            gender="female"
        ),
        "af_jessica": Voice(
            id="af_jessica",
            name="Jessica",
            description="Soft, gentle voice",
            gender="female"
        )
    }
    
    def __init__(self, client: HTTPClient):
        self.client = client
    
    def speech(
        self,
        input_text: str,
        model: str = "tts-1",
        voice: str = "af_alloy",
        response_format: str = "mp3",
        speed: float = 1.0,
        user: Optional[str] = None,
        **kwargs
    ) -> AudioResult:
        """
        Convert text to speech.
        
        Args:
            input_text: Text to convert to speech
            model: TTS model to use
            voice: Voice to use for synthesis
            response_format: Audio format ("mp3", "wav", "aac", "flac")
            speed: Speech speed multiplier (0.25 to 4.0)
            user: User identifier for tracking
            **kwargs: Additional parameters
            
        Returns:
            AudioResult with audio data
        """
        if voice not in self.VOICES:
            raise AudioGenerationError(f"Invalid voice: {voice}. Available voices: {list(self.VOICES.keys())}")
        
        if not (0.25 <= speed <= 4.0):
            raise AudioGenerationError("Speed must be between 0.25 and 4.0")
        
        data = {
            "model": model,
            "input": input_text,
            "voice": voice,
            "response_format": response_format,
            "speed": speed,
            **kwargs
        }
        
        if user:
            data["user"] = user
        
        response = self.client.post("/audio/speech", data=data)
        
        # Audio responses are binary data, not JSON
        if response.status_code != 200:
            try:
                error_data = response.json()
                raise AudioGenerationError(f"Audio generation failed: {error_data.get('error', {}).get('message', 'Unknown error')}")
            except:
                raise AudioGenerationError(f"Audio generation failed with status {response.status_code}")
        
        return AudioResult(
            audio_data=response.content,
            format=response_format,
            sample_rate=self._get_sample_rate(response_format)
        )
    
    def speech_to_file(
        self,
        input_text: str,
        output_path: Union[str, Path],
        model: str = "tts-1",
        voice: str = "af_alloy",
        response_format: str = "mp3",
        speed: float = 1.0,
        **kwargs
    ) -> Path:
        """
        Convert text to speech and save to file.
        
        Args:
            input_text: Text to convert to speech
            output_path: Path to save the audio file
            model: TTS model to use
            voice: Voice to use for synthesis
            response_format: Audio format
            speed: Speech speed multiplier
            **kwargs: Additional parameters
            
        Returns:
            Path to the saved audio file
        """
        audio_result = self.speech(
            input_text=input_text,
            model=model,
            voice=voice,
            response_format=response_format,
            speed=speed,
            **kwargs
        )
        
        output_path = Path(output_path)
        return audio_result.save(output_path)
    
    def speech_stream(
        self,
        input_text: str,
        model: str = "tts-1",
        voice: str = "af_alloy",
        response_format: str = "mp3",
        speed: float = 1.0,
        chunk_size: int = 1024,
        **kwargs
    ) -> Generator[bytes, None, None]:
        """
        Convert text to speech with streaming response.
        
        Args:
            input_text: Text to convert to speech
            model: TTS model to use
            voice: Voice to use for synthesis
            response_format: Audio format
            speed: Speech speed multiplier
            chunk_size: Size of audio chunks to yield
            **kwargs: Additional parameters
            
        Yields:
            Audio data chunks as bytes
        """
        if voice not in self.VOICES:
            raise AudioGenerationError(f"Invalid voice: {voice}. Available voices: {list(self.VOICES.keys())}")
        
        if not (0.25 <= speed <= 4.0):
            raise AudioGenerationError("Speed must be between 0.25 and 4.0")
        
        data = {
            "model": model,
            "input": input_text,
            "voice": voice,
            "response_format": response_format,
            "speed": speed,
            **kwargs
        }
        
        response = self.client.stream("/audio/speech", data=data)
        
        for chunk in response:
            if chunk:
                yield chunk
    
    def get_voices(self) -> List[Voice]:
        """
        Get list of available voices.
        
        Returns:
            List of Voice objects
        """
        return list(self.VOICES.values())
    
    def get_voice(self, voice_id: str) -> Optional[Voice]:
        """
        Get a specific voice by ID.
        
        Args:
            voice_id: Voice identifier
            
        Returns:
            Voice object or None if not found
        """
        return self.VOICES.get(voice_id)
    
    def search_voices(self, query: str) -> List[Voice]:
        """
        Search for voices by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching Voice objects
        """
        query_lower = query.lower()
        return [
            voice for voice in self.VOICES.values()
            if (query_lower in voice.name.lower() or 
                (voice.description and query_lower in voice.description.lower()))
        ]
    
    def _get_sample_rate(self, format: str) -> Optional[int]:
        """Get typical sample rate for audio format."""
        sample_rates = {
            "mp3": 44100,
            "wav": 44100,
            "aac": 44100,
            "flac": 44100,
            "ogg": 44100
        }
        return sample_rates.get(format.lower())


class AudioBatchProcessor:
    """Batch processor for multiple text-to-speech conversions."""
    
    def __init__(self, audio_api: AudioAPI):
        self.audio_api = audio_api
    
    def process_batch(
        self,
        texts: List[str],
        output_dir: Union[str, Path],
        voice: str = "af_alloy",
        response_format: str = "mp3",
        **kwargs
    ) -> List[Path]:
        """
        Process multiple texts to speech and save to files.
        
        Args:
            texts: List of texts to convert
            output_dir: Directory to save audio files
            voice: Voice to use for synthesis
            response_format: Audio format
            **kwargs: Additional parameters
            
        Returns:
            List of paths to saved audio files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        
        for i, text in enumerate(texts):
            # Create filename based on text content or index
            safe_text = "".join(c for c in text[:50] if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = f"{i:03d}_{safe_text}.{response_format}"
            output_path = output_dir / filename
            
            try:
                saved_path = self.audio_api.speech_to_file(
                    input_text=text,
                    output_path=output_path,
                    voice=voice,
                    response_format=response_format,
                    **kwargs
                )
                saved_files.append(saved_path)
            except Exception as e:
                print(f"Failed to process text {i}: {e}")
                continue
        
        return saved_files


# Convenience functions
def text_to_speech(
    text: str,
    client: Optional[HTTPClient] = None,
    **kwargs
) -> AudioResult:
    """Convenience function to convert text to speech."""
    if client is None:
        from .config import load_config
        from .venice_client import VeniceClient
        config = load_config()
        client = VeniceClient(config)
    
    api = AudioAPI(client)
    return api.speech(text, **kwargs)


def text_to_speech_file(
    text: str,
    output_path: Union[str, Path],
    client: Optional[HTTPClient] = None,
    **kwargs
) -> Path:
    """Convenience function to convert text to speech and save to file."""
    if client is None:
        from .config import load_config
        from .venice_client import VeniceClient
        config = load_config()
        client = VeniceClient(config)
    
    api = AudioAPI(client)
    return api.speech_to_file(text, output_path, **kwargs)
