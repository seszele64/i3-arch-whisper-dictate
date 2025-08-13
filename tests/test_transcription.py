"""Tests for transcription functionality."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from openai import APIError

from whisper_dictate.transcription import WhisperTranscriber, TranscriptionResult
from whisper_dictate.config import OpenAIConfig


class TestTranscriptionResult:
    """Test the TranscriptionResult class."""
    
    def test_init(self):
        """Test TranscriptionResult initialization."""
        result = TranscriptionResult("Hello world", "en")
        assert result.text == "Hello world"
        assert result.language == "en"
    
    def test_init_without_language(self):
        """Test TranscriptionResult initialization without language."""
        result = TranscriptionResult("Hello world")
        assert result.text == "Hello world"
        assert result.language is None
    
    def test_str_representation(self):
        """Test string representation."""
        result = TranscriptionResult("Hello world")
        assert str(result) == "Hello world"
    
    def test_repr_representation(self):
        """Test repr representation."""
        result = TranscriptionResult("Hello world this is a long text")
        expected = "TranscriptionResult(text='Hello world this is a long text...', language=None)"
        assert repr(result) == expected


class TestWhisperTranscriber:
    """Test the WhisperTranscriber class."""
    
    def test_init(self, mock_config, mock_openai_client):
        """Test WhisperTranscriber initialization."""
        transcriber = WhisperTranscriber(mock_config.openai, client=mock_openai_client)
        assert transcriber.config == mock_config.openai
        assert transcriber.client is not None
    
    def test_transcribe_audio_success(self, temp_audio_file, mock_openai_client):
        """Test successful audio transcription."""
        config = OpenAIConfig(api_key="test-key")
        transcriber = WhisperTranscriber(config, client=mock_openai_client)
        
        result = transcriber.transcribe_audio(temp_audio_file)
        
        assert isinstance(result, TranscriptionResult)
        assert result.text == "This is a test transcription."
        assert result.language == "en"
        
        # Verify API call
        mock_openai_client.audio.transcriptions.create.assert_called_once()
        call_args = mock_openai_client.audio.transcriptions.create.call_args
        assert call_args[1]['model'] == 'whisper-1'
        assert call_args[1]['response_format'] == 'json'
    
    def test_transcribe_audio_file_not_found(self, mock_openai_client):
        """Test transcription with non-existent file."""
        config = OpenAIConfig(api_key="test-key")
        transcriber = WhisperTranscriber(config, client=mock_openai_client)
        
        non_existent = Path("/non/existent/file.wav")
        
        with pytest.raises(IOError, match="Audio file not found"):
            transcriber.transcribe_audio(non_existent)
    
    def test_transcribe_audio_api_error(self, temp_audio_file, mock_openai_client):
        """Test handling of API errors."""
        config = OpenAIConfig(api_key="test-key")
        transcriber = WhisperTranscriber(config, client=mock_openai_client)
        
        # Mock API error
        mock_openai_client.audio.transcriptions.create.side_effect = APIError(
            message="API Error",
            request=None,
            body=None
        )
        
        with pytest.raises(APIError):
            transcriber.transcribe_audio(temp_audio_file)
    
    def test_transcribe_audio_unexpected_error(self, temp_audio_file, mock_openai_client):
        """Test handling of unexpected errors."""
        config = OpenAIConfig(api_key="test-key")
        transcriber = WhisperTranscriber(config, client=mock_openai_client)
        
        # Mock unexpected error
        mock_openai_client.audio.transcriptions.create.side_effect = Exception("Unexpected error")
        
        with pytest.raises(Exception, match="Unexpected error"):
            transcriber.transcribe_audio(temp_audio_file)
    
    @patch('builtins.open', side_effect=IOError("Cannot read file"))
    def test_transcribe_audio_file_read_error(self, mock_file, mock_openai_client):
        """Test handling of file read errors."""
        config = OpenAIConfig(api_key="test-key")
        transcriber = WhisperTranscriber(config, client=mock_openai_client)
        
        # Create a mock file that exists but can't be read
        with patch('pathlib.Path.exists', return_value=True):
            audio_file = Path("test.wav")
            
            with pytest.raises(IOError, match="Cannot read file"):
                transcriber.transcribe_audio(audio_file)