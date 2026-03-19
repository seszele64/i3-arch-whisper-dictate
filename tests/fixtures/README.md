# Test Fixtures

This directory contains test fixtures for the whisper-dictate test suite.

## Files

- `test_audio.wav` - A 2-second silent WAV file for testing purposes
  - Sample rate: 16 kHz (optimal for Whisper API)
  - Channels: Mono
  - Format: 16-bit PCM
  - Size: ~64 KB

## Note on Integration Tests

The test audio file in this directory contains silence and is primarily used for:
1. Testing file handling and validation
2. Testing API connectivity without incurring significant costs
3. CI/CD pipeline validation

For actual transcription validation, consider using:
- A short recording of spoken text
- Known phrases for content validation
- Various audio formats (WAV, MP3, etc.)

To create a proper test audio file:
```bash
# Record 5 seconds of test audio
ffmpeg -f pulse -i default -t 5 -ar 16000 -ac 1 tests/fixtures/test_audio.wav
```

## Storage

Audio files should be kept under 25MB to comply with OpenAI's API limits.
