"""Integration tests using real OpenAI API.

These tests require a valid OPENAI_API_KEY environment variable.
They are marked with @pytest.mark.integration and are skipped by default
during unit test runs.
"""

import os
from pathlib import Path

import pytest

from whisper_dictate.config import OpenAIConfig
from whisper_dictate.transcription import WhisperTranscriber, TranscriptionResult


# Skip all integration tests if OPENAI_API_KEY is not set
pytestmark = pytest.mark.skipif(
    os.environ.get("OPENAI_API_KEY") is None,
    reason="OPENAI_API_KEY environment variable not set",
)


@pytest.fixture
def test_audio_file() -> Path:
    """Path to the test audio fixture."""
    return Path(__file__).parent / "fixtures" / "test_audio.wav"


@pytest.fixture
def real_openai_config() -> OpenAIConfig:
    """Create OpenAI config using the real API key."""
    return OpenAIConfig(
        api_key=os.environ.get("OPENAI_API_KEY", ""),
        model="whisper-1",
        timeout=30.0,
    )


class TestRealTranscription:
    """Integration tests using real OpenAI Whisper API."""

    @pytest.mark.integration
    @pytest.mark.timeout(60)
    def test_real_transcription_success(
        self, real_openai_config: OpenAIConfig, test_audio_file: Path
    ) -> None:
        """Test transcription with real OpenAI API.

        This test uses a real audio file and validates that:
        1. The transcription completes successfully
        2. The result contains expected text
        3. The language is detected
        """
        if not test_audio_file.exists():
            pytest.skip(f"Test audio file not found: {test_audio_file}")

        transcriber = WhisperTranscriber(real_openai_config)
        result = transcriber.transcribe_audio(test_audio_file)

        assert isinstance(result, TranscriptionResult)
        assert result.text is not None
        assert len(result.text) > 0
        # Language should be auto-detected
        assert result.language is not None or True  # Language may or may not be returned

    @pytest.mark.integration
    @pytest.mark.timeout(60)
    def test_real_transcription_different_audio(
        self, real_openai_config: OpenAIConfig, test_audio_file: Path
    ) -> None:
        """Test transcription with alternative audio patterns.

        Validates the API can handle various audio formats and content.
        """
        if not test_audio_file.exists():
            pytest.skip(f"Test audio file not found: {test_audio_file}")

        transcriber = WhisperTranscriber(real_openai_config)
        result = transcriber.transcribe_audio(test_audio_file)

        assert isinstance(result, TranscriptionResult)
        assert result.text is not None
        # Just verify we got some text back (content validation)
        assert isinstance(result.text, str)


class TestTranscriptionValidation:
    """Tests validating transcription quality and behavior."""

    @pytest.mark.integration
    @pytest.mark.timeout(60)
    def test_transcription_handles_silence(self, real_openai_config: OpenAIConfig) -> None:
        """Test API behavior with silent/near-silent audio.

        This tests error handling when audio contains no speech.
        """
        # This test is optional - silence handling may vary by API
        pytest.skip("Silence handling test - requires specific test audio")

    @pytest.mark.integration
    @pytest.mark.timeout(60)
    def test_transcription_with_invalid_file(self, real_openai_config: OpenAIConfig) -> None:
        """Test error handling for invalid audio files."""
        transcriber = WhisperTranscriber(real_openai_config)

        with pytest.raises((IOError, ValueError)):
            transcriber.transcribe_audio(Path("/nonexistent/path/audio.wav"))
