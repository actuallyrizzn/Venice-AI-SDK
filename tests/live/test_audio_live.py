"""
Live tests for the AudioAPI module.

These tests make real API calls to verify audio functionality.
"""

import pytest
import os
import tempfile
from pathlib import Path
from venice_sdk.audio import AudioAPI
from venice_sdk.client import HTTPClient
from venice_sdk.config import Config
from venice_sdk.errors import VeniceAPIError


@pytest.mark.live
class TestAudioAPILive:
    """Live tests for AudioAPI with real API calls."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.api_key = os.getenv("VENICE_API_KEY")
        if not self.api_key:
            pytest.skip("VENICE_API_KEY environment variable not set")
        
        self.config = Config(api_key=self.api_key)
        self.client = HTTPClient(self.config)
        self.audio_api = AudioAPI(self.client)

    def test_speech_generation(self):
        """Test basic speech generation."""
        text = "Hello, this is a test of the Venice AI text-to-speech system."
        
        result = self.audio_api.speech(
            input_text=text,
            voice="af_alloy",
            model="tts-kokoro"
        )
        
        assert result is not None
        assert hasattr(result, 'url')
        assert hasattr(result, 'b64_json')
        assert hasattr(result, 'created')
        
        # At least one of url or b64_json should be present
        assert result.url is not None or result.b64_json is not None

    def test_speech_with_different_voices(self):
        """Test speech generation with different voices."""
        text = "Testing different voices for text-to-speech."
        voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        
        for voice in voices:
            try:
                result = self.audio_api.speech(
                    input_text=text,
                    voice=voice,
                    model="tts-kokoro"
                )
                
                assert result is not None
                assert result.url is not None or result.b64_json is not None
                
            except VeniceAPIError as e:
                # Some voices might not be available
                if e.status_code == 404:
                    continue
                raise

    def test_speech_with_different_models(self):
        """Test speech generation with different models."""
        text = "Testing different TTS models."
        models = ["tts-1", "tts-1-hd"]
        
        for model in models:
            try:
                result = self.audio_api.speech(
                    input_text=text,
                    voice="af_alloy",
                    model=model
                )
                
                assert result is not None
                assert result.url is not None or result.b64_json is not None
                
            except VeniceAPIError as e:
                # Some models might not be available
                if e.status_code == 404:
                    continue
                raise

    def test_speech_with_parameters(self):
        """Test speech generation with various parameters."""
        text = "Testing speech generation with different parameters."
        
        result = self.audio_api.speech(
            input_text=text,
            voice="af_alloy",
            model="tts-kokoro",
            response_format="mp3",
            speed=1.0
        )
        
        assert result is not None
        assert result.url is not None or result.b64_json is not None

    def test_speech_to_file(self):
        """Test saving speech to file."""
        text = "This is a test of saving speech to a file."
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_speech.mp3"
            
            result = self.audio_api.speech_to_file(
                input_text=text,
                output_path=output_path,
                voice="af_alloy",
                model="tts-kokoro"
            )
            
            assert result == output_path
            assert output_path.exists()
            assert output_path.stat().st_size > 0

    def test_speech_stream(self):
        """Test streaming speech generation."""
        text = "This is a test of streaming speech generation."
        
        chunks = list(self.audio_api.speech_stream(
            input_text=text,
            voice="af_alloy",
            model="tts-kokoro"
        ))
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, bytes) for chunk in chunks)
        
        # Verify we received some audio data
        total_size = sum(len(chunk) for chunk in chunks)
        assert total_size > 0

    def test_get_voices(self):
        """Test getting available voices."""
        voices = self.audio_api.get_voices()
        
        assert isinstance(voices, list)
        assert len(voices) > 0
        
        # Verify voice structure
        voice = voices[0]
        assert hasattr(voice, 'id')
        assert hasattr(voice, 'name')
        assert hasattr(voice, 'category')
        assert hasattr(voice, 'description')
        assert hasattr(voice, 'preview_url')

    def test_get_voice_by_id(self):
        """Test getting a specific voice by ID."""
        # First get all voices
        voices = self.audio_api.get_voices()
        assert len(voices) > 0
        
        voice_id = voices[0].id
        voice = self.audio_api.get_voice(voice_id)
        
        assert voice is not None
        assert voice.id == voice_id

    def test_get_nonexistent_voice(self):
        """Test getting a voice that doesn't exist."""
        voice = self.audio_api.get_voice("nonexistent-voice-id")
        assert voice is None

    def test_search_voices(self):
        """Test searching voices."""
        # Search for voices with "alloy" in the name
        voices = self.audio_api.search_voices("alloy")
        
        assert isinstance(voices, list)
        # Should find at least the alloy voice
        assert len(voices) > 0
        
        # Verify search results
        for voice in voices:
            assert "alloy" in voice.name.lower() or "alloy" in voice.description.lower()

    def test_search_voices_case_insensitive(self):
        """Test case-insensitive voice search."""
        voices = self.audio_api.search_voices("ALLOY")
        
        assert isinstance(voices, list)
        assert len(voices) > 0

    def test_search_voices_no_results(self):
        """Test voice search with no results."""
        voices = self.audio_api.search_voices("nonexistent-voice-name")
        
        assert isinstance(voices, list)
        assert len(voices) == 0

    def test_audio_batch_processing(self):
        """Test batch audio processing."""
        texts = [
            "First text for batch processing.",
            "Second text for batch processing.",
            "Third text for batch processing."
        ]
        
        results = self.audio_api.process_batch(
            texts=texts,
            voice="af_alloy",
            model="tts-kokoro"
        )
        
        assert isinstance(results, list)
        assert len(results) == len(texts)
        
        for result in results:
            assert result is not None
            assert hasattr(result, 'url')
            assert hasattr(result, 'b64_json')
            assert result.url is not None or result.b64_json is not None

    def test_audio_batch_processing_with_errors(self):
        """Test batch processing with some errors."""
        texts = [
            "Valid text for processing.",
            "",  # Empty text might cause error
            "Another valid text."
        ]
        
        try:
            results = self.audio_api.process_batch(
                texts=texts,
                voice="af_alloy",
                model="tts-kokoro"
            )
            
            assert isinstance(results, list)
            # Some results might be None due to errors
            valid_results = [r for r in results if r is not None]
            assert len(valid_results) > 0
            
        except Exception as e:
            # Batch processing might fail with empty text
            assert isinstance(e, (VeniceAPIError, ValueError))

    def test_audio_with_long_text(self):
        """Test audio generation with long text."""
        long_text = "This is a very long text that will test the audio generation system's ability to handle substantial amounts of text. " * 10
        
        result = self.audio_api.speech(
            input_text=long_text,
            voice="af_alloy",
            model="tts-kokoro"
        )
        
        assert result is not None
        assert result.url is not None or result.b64_json is not None

    def test_audio_with_special_characters(self):
        """Test audio generation with special characters."""
        text = "Testing special characters: @#$%^&*()_+-=[]{}|;':\",./<>? and unicode: 🌟🎵🎤"
        
        result = self.audio_api.speech(
            input_text=text,
            voice="af_alloy",
            model="tts-kokoro"
        )
        
        assert result is not None
        assert result.url is not None or result.b64_json is not None

    def test_audio_with_multiple_languages(self):
        """Test audio generation with multiple languages."""
        multilingual_text = "Hello! 你好! Hola! Bonjour! Guten Tag! こんにちは! Привет!"
        
        result = self.audio_api.speech(
            input_text=multilingual_text,
            voice="af_alloy",
            model="tts-kokoro"
        )
        
        assert result is not None
        assert result.url is not None or result.b64_json is not None

    def test_audio_error_handling(self):
        """Test error handling in audio API."""
        # Test with invalid voice
        with pytest.raises(VeniceAPIError):
            self.audio_api.speech(
                input_text="Test text",
                voice="invalid-voice",
                model="tts-kokoro"
            )

    def test_audio_with_empty_text(self):
        """Test audio generation with empty text."""
        with pytest.raises(ValueError):
            self.audio_api.speech(
                input_text="",
                voice="af_alloy",
                model="tts-kokoro"
            )

    def test_audio_with_none_text(self):
        """Test audio generation with None text."""
        with pytest.raises(ValueError):
            self.audio_api.speech(
                input_text=None,
                voice="af_alloy",
                model="tts-kokoro"
            )

    def test_audio_performance(self):
        """Test audio generation performance."""
        import time
        
        text = "Testing audio generation performance."
        
        start_time = time.time()
        result = self.audio_api.speech(
            input_text=text,
            voice="af_alloy",
            model="tts-kokoro"
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert result is not None
        assert response_time < 30  # Should complete within 30 seconds
        assert response_time > 0

    def test_audio_streaming_performance(self):
        """Test audio streaming performance."""
        import time
        
        text = "Testing audio streaming performance with a longer text."
        
        start_time = time.time()
        chunks = list(self.audio_api.speech_stream(
            input_text=text,
            voice="af_alloy",
            model="tts-kokoro"
        ))
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert len(chunks) > 0
        assert response_time < 30  # Should complete within 30 seconds
        assert response_time > 0

    def test_audio_concurrent_requests(self):
        """Test concurrent audio generation requests."""
        import threading
        import time
        
        results = []
        errors = []
        
        def generate_audio():
            try:
                text = f"Hello from thread {threading.current_thread().name}"
                result = self.audio_api.speech(
                    input_text=text,
                    voice="af_alloy",
                    model="tts-kokoro"
                )
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=generate_audio, name=f"Thread-{i}")
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(results) == 3
        assert len(errors) == 0
        assert all(result is not None for result in results)

    def test_audio_file_operations(self):
        """Test audio file operations."""
        text = "Testing audio file operations."
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test different file formats
            formats = ["mp3", "wav", "ogg"]
            
            for fmt in formats:
                output_path = Path(temp_dir) / f"test_speech.{fmt}"
                
                try:
                    result = self.audio_api.speech_to_file(
                        input_text=text,
                        output_path=output_path,
                        voice="af_alloy",
                        model="tts-kokoro",
                        response_format=fmt
                    )
                    
                    assert result == output_path
                    assert output_path.exists()
                    assert output_path.stat().st_size > 0
                    
                except VeniceAPIError as e:
                    # Some formats might not be supported
                    if e.status_code == 400:
                        continue
                    raise

    def test_audio_quality_comparison(self):
        """Test audio quality comparison between models."""
        text = "Testing audio quality comparison."
        
        # Test standard model
        result_standard = self.audio_api.speech(
            input_text=text,
            voice="af_alloy",
            model="tts-kokoro"
        )
        
        # Test HD model
        try:
            result_hd = self.audio_api.speech(
                input_text=text,
                voice="af_alloy",
                model="tts-1-hd"
            )
            
            assert result_standard is not None
            assert result_hd is not None
            
        except VeniceAPIError as e:
            # HD model might not be available
            if e.status_code == 404:
                pytest.skip("HD model not available")
            raise

    def test_audio_voice_categories(self):
        """Test voice categories."""
        voices = self.audio_api.get_voices()
        
        # Group voices by category
        categories = {}
        for voice in voices:
            category = voice.category
            if category not in categories:
                categories[category] = []
            categories[category].append(voice)
        
        # Should have at least one category
        assert len(categories) > 0
        
        # Test voices from different categories
        for category, category_voices in categories.items():
            if category_voices:
                voice = category_voices[0]
                result = self.audio_api.speech(
                    input_text=f"Testing voice from {category} category.",
                    voice=voice.id,
                    model="tts-kokoro"
                )
                
                assert result is not None
                assert result.url is not None or result.b64_json is not None

    def test_audio_preview_urls(self):
        """Test voice preview URLs."""
        voices = self.audio_api.get_voices()
        
        for voice in voices:
            if voice.preview_url:
                # Preview URL should be a valid URL
                assert voice.preview_url.startswith("http")
                assert len(voice.preview_url) > 10

    def test_audio_voice_descriptions(self):
        """Test voice descriptions."""
        voices = self.audio_api.get_voices()
        
        for voice in voices:
            assert voice.description is not None
            assert isinstance(voice.description, str)
            assert len(voice.description) > 0

    def test_audio_voice_names(self):
        """Test voice names."""
        voices = self.audio_api.get_voices()
        
        for voice in voices:
            assert voice.name is not None
            assert isinstance(voice.name, str)
            assert len(voice.name) > 0
            assert voice.name == voice.id  # Name should match ID

    def test_audio_memory_usage(self):
        """Test memory usage during audio generation."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Generate multiple audio files
        for i in range(5):
            text = f"Testing memory usage for audio generation {i}."
            result = self.audio_api.speech(
                input_text=text,
                voice="af_alloy",
                model="tts-kokoro"
            )
            assert result is not None
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024
