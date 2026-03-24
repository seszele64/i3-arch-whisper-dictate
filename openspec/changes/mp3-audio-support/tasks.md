## 1. Dependencies

- [ ] 1.1 Add pydub==0.25.1 to requirements.txt
- [ ] 1.2 Add FFmpeg installation instructions to README.md

## 2. Configuration Changes

- [ ] 2.1 Add mp3_enabled field to AudioConfig (default: True)
- [ ] 2.2 Add mp3_bitrate field to AudioConfig (default: "128k")
- [ ] 2.3 Add keep_wav field to AudioConfig (default: False)

## 3. AudioConverter Implementation

- [ ] 3.1 Create whisper_dictate/audio_converter.py with AudioConverter class
- [ ] 3.2 Implement convert() method with WAV to MP3 conversion using pydub
- [ ] 3.3 Implement graceful fallback when FFmpeg is unavailable
- [ ] 3.4 Add logging for conversion operations
- [ ] 3.5 Ensure all file path handling supports both .wav and .mp3 extensions
- [ ] 3.6 Add unit tests for AudioConverter

## 4. Transcription Integration

- [ ] 4.1 Modify WhisperTranscriber.transcribe_audio() to handle MP3 files
- [ ] 4.2 Update dictation.py to convert WAV to MP3 before transcription
- [ ] 4.3 Implement conditional conversion based on mp3_enabled config
- [ ] 4.4 Handle file cleanup based on keep_wav config
- [ ] 4.5 Add integration tests for MP3 transcription flow

## 5. Database Schema Update

- [ ] 5.1 Add format column to recordings table (default: 'mp3')
- [ ] 5.2 Update toggle_dictate.py to pass format when creating recording

## 6. Documentation

- [ ] 6.1 Document new MP3 configuration options in docstrings
- [ ] 6.2 Update README.md with FFmpeg dependency
- [ ] 6.3 Add troubleshooting section for FFmpeg installation

## 7. Testing

- [ ] 7.1 Test default configuration values (mp3_enabled=True, mp3_bitrate=128k, keep_wav=False)
- [ ] 7.2 Verify file size reduction of 80-90% when converting WAV to MP3 at 128k
- [ ] 7.3 Verify transcription quality equivalence between WAV and MP3 at 32-64k bitrate
