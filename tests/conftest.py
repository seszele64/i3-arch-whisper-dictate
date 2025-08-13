"""Test configuration and fixtures for whisper-dictate."""

import os
import tempfile
from pathlib import Path
from typing import Generator
import pytest
from unittest.mock import Mock, patch

from whisper_dictate.config import AppConfig, AudioConfig, OpenAIConfig
from whisper_dictate.transcription import TranscriptionResult


@pytest.fixture
def temp_audio_file() -> Generator[Path, None, None]:
    """Create a temporary audio file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        # Create minimal WAV file header for testing
        wav_header = (
            b'RIFF\x26\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00'
            b'\x00}\x00\x00\x02\x00\x10\x00data\x02\x00\x00\x00\x00\x00'
        )
        tmp.write(wav_header)
        tmp.flush()
        yield Path(tmp.name)
    # Cleanup
    try:
        os.unlink(tmp.name)
    except OSError:
        pass


@pytest.fixture
def mock_config() -> AppConfig:
    """Create a mock configuration for testing."""
    return AppConfig(
        audio=AudioConfig(
            sample_rate=16000,
            channels=1,
            duration=1.0,  # Short duration for tests
            device=None
        ),
        openai=OpenAIConfig(
            api_key="test-api-key",
            model="whisper-1",
            timeout=10.0
        ),
        log_level="DEBUG",
        copy_to_clipboard=True
    )


@pytest.fixture
def mock_transcription_result() -> TranscriptionResult:
    """Create a mock transcription result for testing."""
    return TranscriptionResult(
        text="This is a test transcription.",
        language="en"
    )


@pytest.fixture
def mock_openai_client() -> Generator[Mock, None, None]:
    """Mock OpenAI client for testing transcription."""
    with patch('openai.OpenAI') as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock successful transcription response
        mock_response = Mock()
        mock_response.text = "This is a test transcription."
        mock_response.language = "en"
        mock_client.audio.transcriptions.create.return_value = mock_response
        
        yield mock_client


@pytest.fixture
def mock_subprocess() -> Generator[Mock, None, None]:
    """Mock subprocess for testing clipboard and notifications."""
    with patch('subprocess.run') as mock_run:
        # Default successful response
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "mock output"
        mock_run.return_value.stderr = ""
        yield mock_run


@pytest.fixture
def mock_sounddevice() -> Generator[Mock, None, None]:
    """Mock sounddevice for testing audio recording."""
    with patch('sounddevice.rec') as mock_rec, \
         patch('sounddevice.wait') as mock_wait, \
         patch('sounddevice.query_devices') as mock_query:
        
        # Mock successful recording
        mock_rec.return_value = [[0.1], [0.2], [0.3]]  # Mock audio data
        mock_wait.return_value = None
        
        # Mock device query
        mock_query.return_value = [
            {'name': 'default', 'max_input_channels': 2},
            {'name': 'pulse', 'max_input_channels': 2}
        ]
        
        yield {
            'rec': mock_rec,
            'wait': mock_wait,
            'query': mock_query
        }


@pytest.fixture
def mock_soundfile() -> Generator[Mock, None, None]:
    """Mock soundfile for testing audio file operations."""
    with patch('soundfile.write') as mock_write:
        mock_write.return_value = None
        yield mock_write


@pytest.fixture
def temp_env_vars() -> Generator[None, None, None]:
    """Set up temporary environment variables for testing."""
    original_env = dict(os.environ)
    
    # Set test environment variables
    os.environ['OPENAI_API_KEY'] = 'test-api-key'
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)