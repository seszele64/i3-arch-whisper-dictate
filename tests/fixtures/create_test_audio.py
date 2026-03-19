"""Generate a test audio file for integration tests."""

import struct
import wave
from pathlib import Path


def create_test_wav(filepath: Path, duration_seconds: float = 2.0) -> None:
    """Create a minimal WAV file with silence for testing.

    Args:
        filepath: Path to write the WAV file
        duration_seconds: Duration of audio in seconds
    """
    # Audio parameters
    sample_rate = 16000  # 16 kHz (optimal for Whisper)
    num_channels = 1  # Mono
    sample_width = 2  # 16-bit

    # Calculate number of samples
    num_samples = int(sample_rate * duration_seconds)

    # Generate silence (zeros)
    # For a real test, you might want to use actual audio content
    audio_data = b"\x00\x00" * num_samples

    # Create WAV file
    with wave.open(str(filepath), "wb") as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data)

    print(f"Created test audio file: {filepath}")
    print(f"  Duration: {duration_seconds}s")
    print(f"  Sample rate: {sample_rate} Hz")
    print(f"  Channels: {num_channels}")
    print(f"  Size: {filepath.stat().st_size} bytes")


if __name__ == "__main__":
    # Create the test file in the fixtures directory
    fixtures_dir = Path(__file__).parent
    test_wav = fixtures_dir / "test_audio.wav"
    create_test_wav(test_wav, duration_seconds=2.0)
