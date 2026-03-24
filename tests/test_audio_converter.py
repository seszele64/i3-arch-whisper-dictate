"""Tests for audio converter functionality."""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock
import tempfile
import os


# Create mock pydub module for testing
class MockAudioSegment:
    """Mock AudioSegment class for pydub."""

    def __init__(self):
        self._data = b""

    @classmethod
    def from_wav(cls, filepath):
        return cls()

    def export(self, filepath, format=None, bitrate=None, **kwargs):
        # Create empty file to simulate export
        Path(filepath).touch()


class MockPydub:
    """Mock pydub module."""

    AudioSegment = MockAudioSegment


@pytest.fixture(autouse=True)
def mock_pydub_in_sys_modules():
    """Add mock pydub module to sys.modules before tests."""
    # Store original pydub if it exists
    original_pydub = sys.modules.get("pydub")

    # Create and add mock pydub to sys.modules
    mock_module = Mock()
    mock_module.AudioSegment = MockAudioSegment
    sys.modules["pydub"] = mock_module

    yield

    # Restore original
    if original_pydub is not None:
        sys.modules["pydub"] = original_pydub
    else:
        sys.modules.pop("pydub", None)


class TestAudioConverter:
    """Test the AudioConverter class."""

    def test_init_default_values(self):
        """Test AudioConverter initialization with default values."""
        from whisper_dictate.audio_converter import AudioConverter

        converter = AudioConverter()
        assert converter.bitrate == "128k"
        assert converter.keep_wav is False

    def test_init_custom_values(self):
        """Test AudioConverter initialization with custom values."""
        from whisper_dictate.audio_converter import AudioConverter

        converter = AudioConverter(bitrate="64k", keep_wav=True)
        assert converter.bitrate == "64k"
        assert converter.keep_wav is True

    def test_convert_success(self, temp_audio_file):
        """Test successful WAV to MP3 conversion."""
        from whisper_dictate.audio_converter import AudioConverter

        converter = AudioConverter()

        result = converter.convert(temp_audio_file)

        # Verify result
        assert result == temp_audio_file.with_suffix(".mp3")
        assert result.exists()

    def test_convert_with_custom_bitrate(self, temp_audio_file):
        """Test conversion with custom bitrate."""
        from whisper_dictate.audio_converter import AudioConverter

        converter = AudioConverter(bitrate="64k")

        result = converter.convert(temp_audio_file)

        # Should still work with custom bitrate
        assert result == temp_audio_file.with_suffix(".mp3")
        assert result.exists()

    def test_convert_fallback_when_ffmpeg_unavailable(self, temp_audio_file):
        """Test fallback to original WAV when FFmpeg is not available."""
        from whisper_dictate.audio_converter import AudioConverter

        converter = AudioConverter()

        # Simulate FFmpeg not found by making from_wav raise FileNotFoundError
        original_from_wav = MockAudioSegment.from_wav
        MockAudioSegment.from_wav = classmethod(
            lambda cls, path: (_ for _ in ()).throw(
                FileNotFoundError("ffmpeg not found")
            )
        )

        try:
            result = converter.convert(temp_audio_file)

            # Should return original WAV path
            assert result == temp_audio_file
        finally:
            MockAudioSegment.from_wav = original_from_wav

    def test_convert_fallback_on_generic_error(self, temp_audio_file):
        """Test fallback to original WAV on any conversion error."""
        from whisper_dictate.audio_converter import AudioConverter

        converter = AudioConverter()

        # Simulate any conversion error
        original_from_wav = MockAudioSegment.from_wav
        MockAudioSegment.from_wav = classmethod(
            lambda cls, path: (_ for _ in ()).throw(Exception("Corrupt audio file"))
        )

        try:
            result = converter.convert(temp_audio_file)

            # Should return original WAV path
            assert result == temp_audio_file
        finally:
            MockAudioSegment.from_wav = original_from_wav

    def test_convert_deletes_source_by_default(self, temp_audio_file):
        """Test that source WAV is deleted after successful conversion."""
        from whisper_dictate.audio_converter import AudioConverter

        converter = AudioConverter(keep_wav=False)

        result = converter.convert(temp_audio_file)

        # Source WAV should be deleted
        assert not temp_audio_file.exists()
        assert result.exists()
        assert result.suffix == ".mp3"

    def test_convert_keeps_source_when_keep_wav_true(self, temp_audio_file):
        """Test that source WAV is preserved when keep_wav=True."""
        from whisper_dictate.audio_converter import AudioConverter

        converter = AudioConverter(keep_wav=True)

        result = converter.convert(temp_audio_file)

        # Source WAV should still exist
        assert temp_audio_file.exists()
        assert result.exists()
        assert result.suffix == ".mp3"

    def test_convert_delete_source_overrides_keep_wav(self, temp_audio_file):
        """Test that delete_source=True overrides keep_wav setting."""
        from whisper_dictate.audio_converter import AudioConverter

        # keep_wav=True but delete_source=True should still delete
        converter = AudioConverter(keep_wav=True)

        result = converter.convert(temp_audio_file, delete_source=True)

        # Source WAV should be deleted because delete_source=True
        assert not temp_audio_file.exists()
        assert result.exists()

    def test_convert_preserves_when_delete_source_false_and_keep_wav_false(
        self, temp_audio_file
    ):
        """Test WAV is preserved when delete_source=False and keep_wav=False."""
        from whisper_dictate.audio_converter import AudioConverter

        converter = AudioConverter(keep_wav=False)

        result = converter.convert(temp_audio_file, delete_source=False)

        # Source WAV should still exist because delete_source=False
        assert temp_audio_file.exists()
        assert result.exists()

    def test_convert_accepts_string_path(self):
        """Test that convert accepts string path instead of Path object."""
        from whisper_dictate.audio_converter import AudioConverter

        converter = AudioConverter()

        # Create temp file with string path
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(b"RIFF")
            tmp.flush()
            wav_path_str = tmp.name
            mp3_path_str = wav_path_str.replace(".wav", ".mp3")

        try:
            result = converter.convert(wav_path_str)

            # Should work with string path
            assert result == Path(mp3_path_str)
            assert result.exists()
        finally:
            # Cleanup
            try:
                os.unlink(wav_path_str)
            except OSError:
                pass
            try:
                os.unlink(mp3_path_str)
            except OSError:
                pass

    def test_convert_and_keep_wav_method(self, temp_audio_file):
        """Test convert_and_keep_wav convenience method."""
        from whisper_dictate.audio_converter import AudioConverter

        converter = AudioConverter(keep_wav=False)  # Default would delete

        result = converter.convert_and_keep_wav(temp_audio_file)

        # Source should be preserved
        assert temp_audio_file.exists()
        assert result.exists()

    def test_convert_and_delete_wav_method(self, temp_audio_file):
        """Test convert_and_delete_wav convenience method."""
        from whisper_dictate.audio_converter import AudioConverter

        converter = AudioConverter(keep_wav=True)  # Default would keep

        result = converter.convert_and_delete_wav(temp_audio_file)

        # Source should be deleted
        assert not temp_audio_file.exists()
        assert result.exists()

    def test_convert_with_path_object(self, temp_audio_file):
        """Test convert properly handles Path objects."""
        from whisper_dictate.audio_converter import AudioConverter

        converter = AudioConverter()

        # Pass Path object directly
        result = converter.convert(Path(temp_audio_file))

        # Should work with Path input
        assert result.suffix == ".mp3"
        assert result.exists()

    def test_output_path_has_mp3_extension(self, temp_audio_file):
        """Test that output path has .mp3 extension."""
        from whisper_dictate.audio_converter import AudioConverter

        converter = AudioConverter()

        result = converter.convert(temp_audio_file)

        assert result.suffix == ".mp3"
        assert result.name.endswith(".mp3")

    def test_convert_logs_start(self, temp_audio_file, caplog):
        """Test that conversion start is logged."""
        from whisper_dictate.audio_converter import AudioConverter

        converter = AudioConverter()

        with caplog.at_level("INFO"):
            converter.convert(temp_audio_file)

        # Check that start of conversion was logged
        assert any(
            "Starting WAV to MP3 conversion" in record.message
            for record in caplog.records
        )

    def test_convert_logs_success_with_size_reduction(self, temp_audio_file, caplog):
        """Test that successful conversion with size reduction is logged."""
        from whisper_dictate.audio_converter import AudioConverter

        converter = AudioConverter()

        with caplog.at_level("INFO"):
            converter.convert(temp_audio_file)

        # Check success message with size info
        assert any(
            "Conversion successful" in record.message for record in caplog.records
        )

    def test_convert_logs_warning_on_ffmpeg_missing(self, temp_audio_file, caplog):
        """Test that warning is logged when FFmpeg is missing."""
        from whisper_dictate.audio_converter import AudioConverter

        converter = AudioConverter()

        # Simulate FFmpeg not found
        original_from_wav = MockAudioSegment.from_wav
        MockAudioSegment.from_wav = classmethod(
            lambda cls, path: (_ for _ in ()).throw(
                FileNotFoundError("ffmpeg not found")
            )
        )

        try:
            with caplog.at_level("WARNING"):
                result = converter.convert(temp_audio_file)

            # Check warning message
            assert any(
                "FFmpeg not found" in record.message for record in caplog.records
            )
            # Should still return WAV path
            assert result == temp_audio_file
        finally:
            MockAudioSegment.from_wav = original_from_wav
