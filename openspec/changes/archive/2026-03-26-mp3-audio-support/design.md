## Context

The whisper-dictate application currently records audio in WAV format and sends it directly to the OpenAI Whisper API for transcription. WAV files are uncompressed and consume significant disk space (approximately 10MB per minute at 44.1kHz stereo). The Whisper API natively supports MP3 format, which can achieve 80-90% file size reduction with no impact on transcription quality for speech.

The project uses:
- Python 3.11+ with pydantic for configuration
- sounddevice/soundfile for audio recording
- OpenAI Whisper API for transcription
- SQLite database for persistence

## Goals / Non-Goals

**Goals:**
- Implement WAV to MP3 conversion before API upload using pydub/FFmpeg
- Reduce storage requirements and API upload size
- Provide configurable MP3 quality settings (bitrate)
- Make WAV preservation optional via configuration
- Ensure graceful degradation when FFmpeg is unavailable

**Non-Goals:**
- Re-encoding existing stored recordings
- Supporting formats other than WAV to MP3 (this is not a general audio converter)
- Implementing audio quality analysis or adaptive bitrate
- Modifying the Whisper API integration beyond file format support

## Decisions

### Decision 1: Use pydub with FFmpeg backend for conversion

**Choice:** Implement AudioConverter using pydub library with FFmpeg backend

**Rationale:**
- pydub provides a simple, well-documented API for audio format conversion
- FFmpeg is the gold standard for audio transcoding and is universally available
- Whisper API already supports MP3 natively, so no API changes needed
- The conversion is a simple file transformation step before API upload

**Alternatives Considered:**
- Using pure Python audio libraries (e.g., audioread): More complex, limited format support
- Implementing MP3 encoding from scratch: Overkill for this use case, not practical
- Relying on external script calls to ffmpeg CLI: Less clean than library API

### Decision 2: Default MP3 bitrate of 128 kbps

**Choice:** Default to 128 kbps MP3 encoding

**Rationale:**
- 128 kbps provides good balance between file size and quality
- Research indicates 32-64 kbps is sufficient for speech transcription quality
- 128 kbps is a safe default that ensures no quality concerns
- Users who need lower bandwidth can configure down to 64k or 32k

**Alternatives Considered:**
- 64 kbps: Would work for speech but might concern users about quality
- 256 kbps: Better quality but larger files, less savings
- User-configurable with safe default: Best approach for flexibility

### Decision 3: Make WAV preservation configurable (default: delete)

**Choice:** Default to deleting original WAV after MP3 conversion, with option to preserve

**Rationale:**
- Storage savings are the primary motivation for this change
- Users who need WAV files can opt-in to preservation
- Backwards compatible - existing behavior preserved via keep_wav=True

**Alternatives Considered:**
- Always preserve: Defeats the purpose of storage reduction
- Always delete: Breaks backwards compatibility for existing users
- Separate archive mode: Overcomplicated for this feature

### Decision 4: Graceful fallback to WAV when FFmpeg unavailable

**Choice:** If FFmpeg/pydub conversion fails, fall back to original WAV file

**Rationale:**
- Ensures the system always remains functional
- Logs warning so users know conversion didn't occur
- The transcription still works, just with larger file

**Alternatives Considered:**
- Raise error and fail transcription: Too aggressive, would break recording workflow
- Prompt user: Not practical in CLI daemon mode

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| FFmpeg not installed on system | Conversion fails | Graceful fallback to WAV, log warning with installation instructions |
| MP3 encoding quality issues | Transcription accuracy | Allow configurable bitrate, document that 64k is sufficient for speech |
| Breaking existing integrations | Users expecting WAV | Default is keep_wav=False (space-saving); users can opt-in to preserve WAV via configuration |
| pydub dependency conflicts | Installation fails | Test on clean environment, provide clear dependency instructions |

## Migration Plan

1. **Phase 1 - Code Changes**
   - Add pydub dependency to requirements.txt
   - Add MP3 configuration fields to AudioConfig
   - Implement AudioConverter class
   - Modify transcription workflow to convert before API call

2. **Phase 2 - Testing**
   - Test conversion with various WAV files
   - Verify transcription quality with MP3 vs WAV
   - Test fallback behavior when FFmpeg unavailable
   - Verify configuration options work correctly

3. **Phase 3 - Deployment**
   - Update documentation with new configuration options
   - Provide clear upgrade instructions (install ffmpeg)
   - Monitor for any issues in production

## Dependencies

- **pydub==0.25.1** - Audio format conversion library
- **FFmpeg** - Audio encoding backend (system dependency)

## Open Questions

1. Should we version the MP3 files differently in the database (add format column)?
   - Decision: Add `format` column to recordings table, default to 'mp3'

2. Should we convert existing WAV recordings to MP3 on upgrade?
   - Decision: No - existing recordings remain WAV, only new recordings use MP3

3. What about users who have already set up the project?
   - Decision: They will need to `pip install pydub==0.25.1` and install ffmpeg, but existing WAV files work as fallback
