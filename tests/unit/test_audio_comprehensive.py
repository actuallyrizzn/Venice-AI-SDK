"""
Comprehensive unit tests for the audio module.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from venice_sdk.audio import (
    Voice, AudioResult, AudioAPI, AudioBatchProcessor,
    text_to_speech, text_to_speech_file
)
from venice_sdk.errors import VeniceAPIError, AudioGenerationError


class TestVoiceComprehensive:
    """Comprehensive test suite for Voice class."""

    def test_voice_initialization(self):
        """Test Voice initialization with all parameters."""
        voice = Voice(
            id="test-voice",
            name="Test Voice",
            description="A test voice",
            language="en-US",
            gender="female",
            age="adult"
        )
        
        assert voice.id == "test-voice"
        assert voice.name == "Test Voice"
        assert voice.description == "A test voice"
        assert voice.language == "en-US"
        assert voice.gender == "female"
        assert voice.age == "adult"

    def test_voice_initialization_with_defaults(self):
        """Test Voice initialization with default values."""
        voice = Voice(id="test-voice", name="Test Voice")
        
        assert voice.id == "test-voice"
        assert voice.name == "Test Voice"
        assert voice.description is None
        assert voice.language is None
        assert voice.gender is None
        assert voice.age is None

    def test_voice_equality(self):
        """Test Voice equality comparison."""
        voice1 = Voice("test-voice", "Test Voice", "desc", "en-US", "female", "adult")
        voice2 = Voice("test-voice", "Test Voice", "desc", "en-US", "female", "adult")
        voice3 = Voice("different-voice", "Test Voice", "desc", "en-US", "female", "adult")
        
        assert voice1 == voice2
        assert voice1 != voice3

    def test_voice_string_representation(self):
        """Test Voice string representation."""
        voice = Voice("test-voice", "Test Voice")
        voice_str = str(voice)
        
        assert "Voice" in voice_str
        assert "test-voice" in voice_str


class TestAudioResultComprehensive:
    """Comprehensive test suite for AudioResult class."""

    def test_audio_result_initialization(self):
        """Test AudioResult initialization with all parameters."""
        audio_data = b"fake audio data"
        audio_result = AudioResult(
            audio_data=audio_data,
            format="mp3",
            duration=5.5,
            sample_rate=44100
        )
        
        assert audio_result.audio_data == audio_data
        assert audio_result.format == "mp3"
        assert audio_result.duration == 5.5
        assert audio_result.sample_rate == 44100

    def test_audio_result_initialization_with_defaults(self):
        """Test AudioResult initialization with default values."""
        audio_data = b"fake audio data"
        audio_result = AudioResult(audio_data=audio_data, format="wav")
        
        assert audio_result.audio_data == audio_data
        assert audio_result.format == "wav"
        assert audio_result.duration is None
        assert audio_result.sample_rate is None

    def test_audio_result_save_to_file(self, tmp_path):
        """Test AudioResult save method."""
        audio_data = b"fake audio data"
        audio_result = AudioResult(audio_data=audio_data, format="mp3")
        
        output_path = tmp_path / "test_audio.mp3"
        saved_path = audio_result.save(output_path)
        
        assert saved_path == output_path
        assert output_path.exists()
        assert output_path.read_bytes() == audio_data

    def test_audio_result_save_with_string_path(self, tmp_path):
        """Test AudioResult save method with string path."""
        audio_data = b"fake audio data"
        audio_result = AudioResult(audio_data=audio_data, format="wav")
        
        output_path = str(tmp_path / "test_audio.wav")
        saved_path = audio_result.save(output_path)
        
        assert isinstance(saved_path, Path)
        assert saved_path.exists()
        assert saved_path.read_bytes() == audio_data

    def test_audio_result_play_with_pygame(self):
        """Test AudioResult play method with pygame available."""
        audio_data = b"fake audio data"
        audio_result = AudioResult(audio_data=audio_data, format="mp3")
        
        with patch('venice_sdk.audio.pygame') as mock_pygame:
            mock_mixer = MagicMock()
            mock_pygame.mixer = mock_mixer
            mock_music = MagicMock()
            mock_mixer.music = mock_music
            
            audio_result.play()
            
            mock_mixer.init.assert_called_once()
            mock_music.load.assert_called_once()
            mock_music.play.assert_called_once()

    def test_audio_result_play_without_pygame(self):
        """Test AudioResult play method without pygame."""
        audio_data = b"fake audio data"
        audio_result = AudioResult(audio_data=audio_data, format="mp3")
        
        with patch('venice_sdk.audio.pygame', side_effect=ImportError):
            with pytest.raises(AudioGenerationError, match="pygame is required for audio playback"):
                audio_result.play()

    def test_audio_result_equality(self):
        """Test AudioResult equality comparison."""
        audio_data = b"fake audio data"
        result1 = AudioResult(audio_data, "mp3", 5.0, 44100)
        result2 = AudioResult(audio_data, "mp3", 5.0, 44100)
        result3 = AudioResult(b"different data", "mp3", 5.0, 44100)
        
        assert result1 == result2
        assert result1 != result3

    def test_audio_result_string_representation(self):
        """Test AudioResult string representation."""
        audio_data = b"fake audio data"
        audio_result = AudioResult(audio_data=audio_data, format="mp3")
        result_str = str(audio_result)
        
        assert "AudioResult" in result_str
        assert "mp3" in result_str


class TestAudioAPIComprehensive:
    """Comprehensive test suite for AudioAPI class."""

    def test_audio_api_initialization(self, mock_client):
        """Test AudioAPI initialization."""
        api = AudioAPI(mock_client)
        assert api.client == mock_client

    def test_audio_api_voices_constant(self, mock_client):
        """Test that VOICES constant is properly defined."""
        api = AudioAPI(mock_client)
        
        assert "alloy" in api.VOICES
        assert "echo" in api.VOICES
        assert "fable" in api.VOICES
        assert "onyx" in api.VOICES
        assert "nova" in api.VOICES
        assert "shimmer" in api.VOICES
        
        # Test voice properties
        alloy_voice = api.VOICES["alloy"]
        assert alloy_voice.id == "alloy"
        assert alloy_voice.name == "Alloy"
        assert alloy_voice.gender == "neutral"

    def test_speech_success(self, mock_client):
        """Test successful speech synthesis."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake audio data"
        mock_client.post.return_value = mock_response
        
        api = AudioAPI(mock_client)
        result = api.speech("Hello world", voice="alloy", response_format="mp3")
        
        assert isinstance(result, AudioResult)
        assert result.audio_data == b"fake audio data"
        assert result.format == "mp3"
        assert result.sample_rate == 44100  # From _get_sample_rate

    def test_speech_with_all_parameters(self, mock_client):
        """Test speech synthesis with all parameters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake audio data"
        mock_client.post.return_value = mock_response
        
        api = AudioAPI(mock_client)
        result = api.speech(
            input_text="Hello world",
            model="tts-1",
            voice="echo",
            response_format="wav",
            speed=1.5,
            user="test-user",
            custom_param="value"
        )
        
        assert isinstance(result, AudioResult)
        mock_client.post.assert_called_once_with("/audio/speech", data={
            "model": "tts-1",
            "input": "Hello world",
            "voice": "echo",
            "response_format": "wav",
            "speed": 1.5,
            "user": "test-user",
            "custom_param": "value"
        })

    def test_speech_invalid_voice(self, mock_client):
        """Test speech synthesis with invalid voice."""
        api = AudioAPI(mock_client)
        
        with pytest.raises(AudioGenerationError, match="Invalid voice: invalid-voice"):
            api.speech("Hello world", voice="invalid-voice")

    def test_speech_invalid_speed_too_low(self, mock_client):
        """Test speech synthesis with speed too low."""
        api = AudioAPI(mock_client)
        
        with pytest.raises(AudioGenerationError, match="Speed must be between 0.25 and 4.0"):
            api.speech("Hello world", speed=0.1)

    def test_speech_invalid_speed_too_high(self, mock_client):
        """Test speech synthesis with speed too high."""
        api = AudioAPI(mock_client)
        
        with pytest.raises(AudioGenerationError, match="Speed must be between 0.25 and 4.0"):
            api.speech("Hello world", speed=5.0)

    def test_speech_boundary_speeds(self, mock_client):
        """Test speech synthesis with boundary speed values."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake audio data"
        mock_client.post.return_value = mock_response
        
        api = AudioAPI(mock_client)
        
        # Test minimum speed
        result = api.speech("Hello world", speed=0.25)
        assert isinstance(result, AudioResult)
        
        # Test maximum speed
        result = api.speech("Hello world", speed=4.0)
        assert isinstance(result, AudioResult)

    def test_speech_api_error_with_json(self, mock_client):
        """Test speech synthesis with API error (JSON response)."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": {"message": "Invalid request"}}
        mock_client.post.return_value = mock_response
        
        api = AudioAPI(mock_client)
        
        with pytest.raises(AudioGenerationError, match="Audio generation failed: Invalid request"):
            api.speech("Hello world")

    def test_speech_api_error_without_json(self, mock_client):
        """Test speech synthesis with API error (non-JSON response)."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.side_effect = Exception("Not JSON")
        mock_client.post.return_value = mock_response
        
        api = AudioAPI(mock_client)
        
        with pytest.raises(AudioGenerationError, match="Audio generation failed with status 500"):
            api.speech("Hello world")

    def test_speech_to_file_success(self, mock_client, tmp_path):
        """Test speech to file functionality."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake audio data"
        mock_client.post.return_value = mock_response
        
        api = AudioAPI(mock_client)
        output_path = tmp_path / "test_audio.mp3"
        
        result_path = api.speech_to_file(
            input_text="Hello world",
            output_path=output_path,
            voice="alloy",
            response_format="mp3"
        )
        
        assert result_path == output_path
        assert output_path.exists()
        assert output_path.read_bytes() == b"fake audio data"

    def test_speech_to_file_with_string_path(self, mock_client, tmp_path):
        """Test speech to file with string path."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake audio data"
        mock_client.post.return_value = mock_response
        
        api = AudioAPI(mock_client)
        output_path = str(tmp_path / "test_audio.wav")
        
        result_path = api.speech_to_file(
            input_text="Hello world",
            output_path=output_path,
            response_format="wav"
        )
        
        assert isinstance(result_path, Path)
        assert result_path.exists()

    def test_speech_stream_success(self, mock_client):
        """Test speech streaming functionality."""
        mock_response = MagicMock()
        mock_response.__iter__ = MagicMock(return_value=iter([b"chunk1", b"chunk2", b"chunk3"]))
        mock_client.stream.return_value = mock_response
        
        api = AudioAPI(mock_client)
        chunks = list(api.speech_stream("Hello world", voice="alloy"))
        
        assert chunks == [b"chunk1", b"chunk2", b"chunk3"]
        mock_client.stream.assert_called_once()

    def test_speech_stream_with_parameters(self, mock_client):
        """Test speech streaming with all parameters."""
        mock_response = MagicMock()
        mock_response.__iter__ = MagicMock(return_value=iter([b"chunk1"]))
        mock_client.stream.return_value = mock_response
        
        api = AudioAPI(mock_client)
        chunks = list(api.speech_stream(
            input_text="Hello world",
            model="tts-1",
            voice="echo",
            response_format="wav",
            speed=1.5,
            chunk_size=512,
            custom_param="value"
        ))
        
        assert chunks == [b"chunk1"]
        mock_client.stream.assert_called_once_with("/audio/speech", data={
            "model": "tts-1",
            "input": "Hello world",
            "voice": "echo",
            "response_format": "wav",
            "speed": 1.5,
            "custom_param": "value"
        })

    def test_speech_stream_invalid_voice(self, mock_client):
        """Test speech streaming with invalid voice."""
        api = AudioAPI(mock_client)
        
        with pytest.raises(AudioGenerationError, match="Invalid voice: invalid-voice"):
            list(api.speech_stream("Hello world", voice="invalid-voice"))

    def test_speech_stream_invalid_speed(self, mock_client):
        """Test speech streaming with invalid speed."""
        api = AudioAPI(mock_client)
        
        with pytest.raises(AudioGenerationError, match="Speed must be between 0.25 and 4.0"):
            list(api.speech_stream("Hello world", speed=5.0))

    def test_speech_stream_empty_chunks(self, mock_client):
        """Test speech streaming with empty chunks."""
        mock_response = MagicMock()
        mock_response.__iter__ = MagicMock(return_value=iter([b"chunk1", b"", b"chunk2", None]))
        mock_client.stream.return_value = mock_response
        
        api = AudioAPI(mock_client)
        chunks = list(api.speech_stream("Hello world"))
        
        # Empty chunks and None should be filtered out
        assert chunks == [b"chunk1", b"chunk2"]

    def test_get_voices(self, mock_client):
        """Test getting all voices."""
        api = AudioAPI(mock_client)
        voices = api.get_voices()
        
        assert len(voices) == 6
        assert all(isinstance(voice, Voice) for voice in voices)
        voice_ids = [voice.id for voice in voices]
        assert "alloy" in voice_ids
        assert "echo" in voice_ids

    def test_get_voice_success(self, mock_client):
        """Test getting a specific voice by ID."""
        api = AudioAPI(mock_client)
        voice = api.get_voice("alloy")
        
        assert voice is not None
        assert isinstance(voice, Voice)
        assert voice.id == "alloy"
        assert voice.name == "Alloy"

    def test_get_voice_not_found(self, mock_client):
        """Test getting a voice that doesn't exist."""
        api = AudioAPI(mock_client)
        voice = api.get_voice("nonexistent-voice")
        
        assert voice is None

    def test_search_voices_by_name(self, mock_client):
        """Test searching voices by name."""
        api = AudioAPI(mock_client)
        voices = api.search_voices("alloy")
        
        assert len(voices) == 1
        assert voices[0].id == "alloy"

    def test_search_voices_by_description(self, mock_client):
        """Test searching voices by description."""
        api = AudioAPI(mock_client)
        voices = api.search_voices("neutral")
        
        assert len(voices) == 1
        assert voices[0].id == "alloy"

    def test_search_voices_case_insensitive(self, mock_client):
        """Test searching voices case insensitive."""
        api = AudioAPI(mock_client)
        voices = api.search_voices("ALLOY")
        
        assert len(voices) == 1
        assert voices[0].id == "alloy"

    def test_search_voices_multiple_matches(self, mock_client):
        """Test searching voices with multiple matches."""
        api = AudioAPI(mock_client)
        voices = api.search_voices("voice")
        
        # Should match voices with "voice" in name or description
        assert len(voices) >= 1

    def test_search_voices_no_matches(self, mock_client):
        """Test searching voices with no matches."""
        api = AudioAPI(mock_client)
        voices = api.search_voices("nonexistent")
        
        assert len(voices) == 0

    def test_get_sample_rate(self, mock_client):
        """Test getting sample rate for different formats."""
        api = AudioAPI(mock_client)
        
        assert api._get_sample_rate("mp3") == 44100
        assert api._get_sample_rate("wav") == 44100
        assert api._get_sample_rate("aac") == 44100
        assert api._get_sample_rate("flac") == 44100
        assert api._get_sample_rate("ogg") == 44100
        assert api._get_sample_rate("unknown") is None
        assert api._get_sample_rate("MP3") == 44100  # Case insensitive


class TestAudioBatchProcessorComprehensive:
    """Comprehensive test suite for AudioBatchProcessor class."""

    def test_audio_batch_processor_initialization(self, mock_client):
        """Test AudioBatchProcessor initialization."""
        audio_api = AudioAPI(mock_client)
        processor = AudioBatchProcessor(audio_api)
        
        assert processor.audio_api == audio_api

    def test_process_batch_success(self, mock_client, tmp_path):
        """Test successful batch processing."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake audio data"
        mock_client.post.return_value = mock_response
        
        audio_api = AudioAPI(mock_client)
        processor = AudioBatchProcessor(audio_api)
        
        texts = ["Hello world", "Goodbye world", "Test message"]
        output_dir = tmp_path / "audio_output"
        
        saved_files = processor.process_batch(
            texts=texts,
            output_dir=output_dir,
            voice="alloy",
            response_format="mp3"
        )
        
        assert len(saved_files) == 3
        assert all(isinstance(path, Path) for path in saved_files)
        assert all(path.exists() for path in saved_files)
        assert output_dir.exists()

    def test_process_batch_with_custom_parameters(self, mock_client, tmp_path):
        """Test batch processing with custom parameters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake audio data"
        mock_client.post.return_value = mock_response
        
        audio_api = AudioAPI(mock_client)
        processor = AudioBatchProcessor(audio_api)
        
        texts = ["Test message"]
        output_dir = tmp_path / "audio_output"
        
        saved_files = processor.process_batch(
            texts=texts,
            output_dir=output_dir,
            voice="echo",
            response_format="wav",
            speed=1.5,
            model="tts-1"
        )
        
        assert len(saved_files) == 1
        assert saved_files[0].suffix == ".wav"

    def test_process_batch_with_special_characters(self, mock_client, tmp_path):
        """Test batch processing with special characters in text."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake audio data"
        mock_client.post.return_value = mock_response
        
        audio_api = AudioAPI(mock_client)
        processor = AudioBatchProcessor(audio_api)
        
        texts = ["Hello! @#$%^&*() world", "Test with spaces and-dashes"]
        output_dir = tmp_path / "audio_output"
        
        saved_files = processor.process_batch(texts=texts, output_dir=output_dir)
        
        assert len(saved_files) == 2
        # Check that filenames are sanitized
        for path in saved_files:
            assert path.name.startswith(("000_", "001_"))
            assert path.suffix == ".mp3"

    def test_process_batch_with_long_text(self, mock_client, tmp_path):
        """Test batch processing with long text (should be truncated in filename)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake audio data"
        mock_client.post.return_value = mock_response
        
        audio_api = AudioAPI(mock_client)
        processor = AudioBatchProcessor(audio_api)
        
        long_text = "This is a very long text that should be truncated in the filename because it exceeds the 50 character limit for safe filename generation"
        texts = [long_text]
        output_dir = tmp_path / "audio_output"
        
        saved_files = processor.process_batch(texts=texts, output_dir=output_dir)
        
        assert len(saved_files) == 1
        # Filename should be truncated
        assert len(saved_files[0].stem) <= 53  # 3 digits + underscore + 50 chars

    def test_process_batch_with_errors(self, mock_client, tmp_path, capsys):
        """Test batch processing with some errors."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake audio data"
        
        # First call succeeds, second fails
        mock_client.post.side_effect = [
            mock_response,
            VeniceAPIError("API Error", status_code=500),
            mock_response
        ]
        
        audio_api = AudioAPI(mock_client)
        processor = AudioBatchProcessor(audio_api)
        
        texts = ["Success text", "Error text", "Another success"]
        output_dir = tmp_path / "audio_output"
        
        saved_files = processor.process_batch(texts=texts, output_dir=output_dir)
        
        # Should have 2 successful files, 1 failed
        assert len(saved_files) == 2
        assert all(path.exists() for path in saved_files)
        
        # Check that error was printed
        captured = capsys.readouterr()
        assert "Failed to process text 1" in captured.out

    def test_process_batch_empty_texts(self, mock_client, tmp_path):
        """Test batch processing with empty texts list."""
        audio_api = AudioAPI(mock_client)
        processor = AudioBatchProcessor(audio_api)
        
        texts = []
        output_dir = tmp_path / "audio_output"
        
        saved_files = processor.process_batch(texts=texts, output_dir=output_dir)
        
        assert len(saved_files) == 0
        assert output_dir.exists()  # Directory should still be created

    def test_process_batch_creates_directory(self, mock_client, tmp_path):
        """Test that batch processing creates output directory."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake audio data"
        mock_client.post.return_value = mock_response
        
        audio_api = AudioAPI(mock_client)
        processor = AudioBatchProcessor(audio_api)
        
        texts = ["Test message"]
        output_dir = tmp_path / "nested" / "audio_output"
        
        # Directory doesn't exist yet
        assert not output_dir.exists()
        
        saved_files = processor.process_batch(texts=texts, output_dir=output_dir)
        
        assert output_dir.exists()
        assert len(saved_files) == 1


class TestConvenienceFunctionsComprehensive:
    """Comprehensive test suite for convenience functions."""

    def test_text_to_speech_with_client(self, mock_client):
        """Test text_to_speech with provided client."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake audio data"
        mock_client.post.return_value = mock_response
        
        result = text_to_speech("Hello world", client=mock_client, voice="alloy")
        
        assert isinstance(result, AudioResult)
        assert result.audio_data == b"fake audio data"

    def test_text_to_speech_without_client(self):
        """Test text_to_speech without provided client."""
        with patch('venice_sdk.audio.load_config') as mock_load_config:
            with patch('venice_sdk.audio.VeniceClient') as mock_venice_client:
                mock_config = MagicMock()
                mock_load_config.return_value = mock_config
                
                mock_client = MagicMock()
                mock_venice_client.return_value = mock_client
                
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.content = b"fake audio data"
                mock_client.post.return_value = mock_response
                
                result = text_to_speech("Hello world", voice="alloy")
                
                assert isinstance(result, AudioResult)
                assert result.audio_data == b"fake audio data"

    def test_text_to_speech_file_with_client(self, mock_client, tmp_path):
        """Test text_to_speech_file with provided client."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake audio data"
        mock_client.post.return_value = mock_response
        
        output_path = tmp_path / "test_audio.mp3"
        result_path = text_to_speech_file("Hello world", output_path, client=mock_client)
        
        assert isinstance(result_path, Path)
        assert result_path.exists()
        assert result_path.read_bytes() == b"fake audio data"

    def test_text_to_speech_file_without_client(self, tmp_path):
        """Test text_to_speech_file without provided client."""
        with patch('venice_sdk.audio.load_config') as mock_load_config:
            with patch('venice_sdk.audio.VeniceClient') as mock_venice_client:
                mock_config = MagicMock()
                mock_load_config.return_value = mock_config
                
                mock_client = MagicMock()
                mock_venice_client.return_value = mock_client
                
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.content = b"fake audio data"
                mock_client.post.return_value = mock_response
                
                output_path = tmp_path / "test_audio.wav"
                result_path = text_to_speech_file("Hello world", output_path)
                
                assert isinstance(result_path, Path)
                assert result_path.exists()

    def test_text_to_speech_file_with_string_path(self, mock_client, tmp_path):
        """Test text_to_speech_file with string path."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake audio data"
        mock_client.post.return_value = mock_response
        
        output_path = str(tmp_path / "test_audio.mp3")
        result_path = text_to_speech_file("Hello world", output_path, client=mock_client)
        
        assert isinstance(result_path, Path)
        assert result_path.exists()

    def test_text_to_speech_with_kwargs(self, mock_client):
        """Test text_to_speech with additional kwargs."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake audio data"
        mock_client.post.return_value = mock_response
        
        result = text_to_speech(
            "Hello world",
            client=mock_client,
            voice="echo",
            speed=1.5,
            response_format="wav",
            custom_param="value"
        )
        
        assert isinstance(result, AudioResult)
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "/audio/speech"
        assert call_args[1]["data"]["custom_param"] == "value"
