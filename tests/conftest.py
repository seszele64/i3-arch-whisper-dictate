"""Test configuration and fixtures for whisper-dictate."""

import atexit
import os
import sys
import tempfile
from pathlib import Path
from typing import Generator
import pytest
from unittest.mock import Mock, patch

from whisper_dictate.config import AppConfig, AudioConfig, OpenAIConfig
from whisper_dictate.transcription import TranscriptionResult


# Session-scoped fixture to patch sounddevice/soundfile before any imports
# This must run BEFORE any other fixtures to prevent the real modules from loading
@pytest.fixture(scope="session", autouse=True)
def patch_audio_modules():
    """Patch sounddevice and soundfile modules in sys.modules before any imports.

    This prevents the real audio libraries from being loaded at module import time,
    which can cause hangs when no audio device is available.
    """
    # Create mock modules
    mock_sd = Mock()
    mock_sf = Mock()

    # Configure mock sounddevice
    mock_sd.rec = Mock()
    mock_sd.wait = Mock(return_value=None)
    mock_sd.query_devices = Mock(
        return_value=[
            {"name": "default", "max_input_channels": 2},
            {"name": "pulse", "max_input_channels": 2},
        ]
    )
    mock_sd.PortAudioError = Exception
    mock_sd.stop = Mock()

    # Configure mock soundfile
    mock_sf.write = Mock()

    # Store original modules if they exist
    original_sd = sys.modules.get("sounddevice")
    original_sf = sys.modules.get("soundfile")

    # Patch sys.modules
    sys.modules["sounddevice"] = mock_sd
    sys.modules["soundfile"] = mock_sf

    yield

    # Restore original modules
    if original_sd is not None:
        sys.modules["sounddevice"] = original_sd
    else:
        sys.modules.pop("sounddevice", None)

    if original_sf is not None:
        sys.modules["soundfile"] = original_sf
    else:
        sys.modules.pop("soundfile", None)


# Ensure sounddevice cleanup on exit
def _cleanup_sounddevice():
    try:
        import sounddevice as sd

        sd.stop()
    except Exception:
        pass


atexit.register(_cleanup_sounddevice)


@pytest.fixture(autouse=True)
def reset_persistent_notification_state():
    """Reset PersistentNotification class variables before each test."""
    import whisper_dictate.notifications as notifications_module
    from unittest.mock import patch

    # Store original values
    original_time = notifications_module.PersistentNotification._last_operation_time
    original_recording = notifications_module._recording_notification

    # Apply patch with explicit control
    patcher = patch.object(notifications_module, "is_dunst_running", return_value=True)
    patcher.start()

    notifications_module.PersistentNotification._last_operation_time = 0.0
    notifications_module._recording_notification = None

    yield

    # Explicit cleanup
    patcher.stop()
    notifications_module.PersistentNotification._last_operation_time = original_time
    notifications_module._recording_notification = original_recording


@pytest.fixture
def temp_audio_file() -> Generator[Path, None, None]:
    """Create a temporary audio file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        # Create minimal WAV file header for testing
        wav_header = (
            b"RIFF\x26\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00"
            b"\x00}\x00\x00\x02\x00\x10\x00data\x02\x00\x00\x00\x00\x00"
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
            device=None,
            mp3_enabled=False,  # Default to disabled for backward compatibility
            mp3_bitrate="128k",
            keep_wav=False,
        ),
        openai=OpenAIConfig(api_key="test-api-key", model="whisper-1", timeout=10.0),
        log_level="DEBUG",
        copy_to_clipboard=True,
    )


@pytest.fixture
def mock_config_mp3_enabled() -> AppConfig:
    """Create a mock configuration with MP3 enabled for testing."""
    return AppConfig(
        audio=AudioConfig(
            sample_rate=16000,
            channels=1,
            duration=1.0,
            device=None,
            mp3_enabled=True,
            mp3_bitrate="128k",
            keep_wav=False,
        ),
        openai=OpenAIConfig(api_key="test-api-key", model="whisper-1", timeout=10.0),
        log_level="DEBUG",
        copy_to_clipboard=True,
    )


@pytest.fixture
def mock_config_mp3_keep_wav() -> AppConfig:
    """Create a mock configuration with MP3 enabled and keep_wav=True."""
    return AppConfig(
        audio=AudioConfig(
            sample_rate=16000,
            channels=1,
            duration=1.0,
            device=None,
            mp3_enabled=True,
            mp3_bitrate="128k",
            keep_wav=True,
        ),
        openai=OpenAIConfig(api_key="test-api-key", model="whisper-1", timeout=10.0),
        log_level="DEBUG",
        copy_to_clipboard=True,
    )


@pytest.fixture
def mock_transcription_result() -> TranscriptionResult:
    """Create a mock transcription result for testing."""
    return TranscriptionResult(text="This is a test transcription.", language="en")


@pytest.fixture
def mock_openai_client() -> Generator[Mock, None, None]:
    """Mock OpenAI client for testing transcription."""
    with patch("openai.OpenAI") as mock_client_class:
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
    with patch("subprocess.run") as mock_run:
        # Default successful response
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "mock output"
        mock_run.return_value.stderr = ""
        yield mock_run


@pytest.fixture
def mock_sounddevice() -> Generator[dict[str, Mock], None, None]:
    """Mock sounddevice for testing audio recording."""
    with (
        patch("sounddevice.rec") as mock_rec,
        patch("sounddevice.wait") as mock_wait,
        patch("sounddevice.query_devices") as mock_query,
    ):
        # Mock successful recording
        mock_rec.return_value = [[0.1], [0.2], [0.3]]  # Mock audio data
        mock_wait.return_value = None

        # Mock device query
        mock_query.return_value = [
            {"name": "default", "max_input_channels": 2},
            {"name": "pulse", "max_input_channels": 2},
        ]

        yield {"rec": mock_rec, "wait": mock_wait, "query": mock_query}


@pytest.fixture
def mock_soundfile() -> Generator[Mock, None, None]:
    """Mock soundfile for testing audio file operations."""
    with patch("soundfile.write") as mock_write:
        mock_write.return_value = None
        yield mock_write


@pytest.fixture
def temp_env_vars() -> Generator[None, None, None]:
    """Set up temporary environment variables for testing."""
    original_env = dict(os.environ)

    # Set test environment variables
    os.environ["OPENAI_API_KEY"] = "test-api-key"

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def async_cleanup(request):
    """Function-scoped fixture for async resource cleanup.

    Uses pytest's request.addfinalizer() pattern to allow any pending
    async tasks to complete after each test. This is function-scoped
    rather than session-scoped to avoid event loop conflicts with
    pytest-asyncio.
    """
    import asyncio
    import time

    def cleanup():
        """Allow pending async tasks to complete."""
        try:
            loop = asyncio.get_running_loop()
            # Schedule a small task to let pending async operations complete
            try:
                loop.run_until_complete(asyncio.sleep(0.01))
            except RuntimeError:
                # Loop already running or closed, ignore
                pass
        except RuntimeError:
            # No running loop available, skip async cleanup
            pass

        # Small delay to allow task cleanup
        time.sleep(0.01)

    request.addfinalizer(cleanup)
    return cleanup
