## Why

Currently, audio recordings are saved and sent to the Whisper API in WAV format, which consumes significant disk space due to uncompressed audio data. WAV files at 44.1kHz stereo can be quite large (10+ MB per minute), leading to unnecessary storage costs and larger API uploads. Converting to MP3 before API upload provides ~80-90% file size reduction with no perceptible loss in transcription quality for speech recognition tasks.

## What Changes

- **NEW**: AudioConverter class for WAV to MP3 conversion using pydub/FFmpeg
- **NEW**: Configuration options for MP3 quality settings (bitrate, keep_wav)
- **MODIFIED**: DictationService to convert WAV to MP3 before API upload
- **NEW**: Fallback to WAV if MP3 conversion fails
- **NEW**: Optional preservation of original WAV files based on config

## Capabilities

### New Capabilities

- `mp3-audio-conversion`: Audio format conversion from WAV to MP3 with configurable quality settings and optional original file preservation

### Modified Capabilities

<!-- No existing capability requirements are being modified - this is purely additive functionality -->

## Impact

- **New Dependency**: `pydub==0.25.1` Python package and `ffmpeg` system package
- **Modified Components**: `whisper_dictate/transcription.py` (WhisperTranscriber), `whisper_dictate/config.py` (AudioConfig), `whisper_dictate/dictation.py` (DictationService)
- **Audio Files**: All audio storage paths may change from .wav to .mp3 extension
- **API Calls**: File uploads to Whisper API will be significantly smaller
