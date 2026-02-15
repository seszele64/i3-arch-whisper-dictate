# Whisper Dictate Constitution

## Core Principles

### I. Latency First
Voice dictation must feel instantaneous. Every user interaction (key press, recording start/stop) must respond within 100ms. Use async patterns, avoid blocking operations, and minimize external API calls during recording state transitions.

### II. Reliability (NON-NEGOTIABLE)
This tool is used in daily workflows - failures disrupt productivity. 
- Always handle exceptions gracefully with user-friendly error messages
- Implement proper resource cleanup (audio streams, threads, temporary files)
- Add retry logic for transient failures (network issues, API timeouts)
- Log errors to `~/.local/share/whisper-dictate/whisper-dictate.log` for debugging

### III. Privacy & Security
Voice data is sensitive and must be handled with care:
- Never persist audio recordings beyond processing
- Support API key via environment variables, not hardcoded values
- Use `.env` files with proper `.gitignore` entries
- Consider local Whisper model option for offline/private transcription

### IV. Configuration Over Hardcoding
Users have diverse setups (different window managers, audio backends, notification systems). Support configuration via:
- Environment variables (for CLI usage)
- Config file (`~/.config/whisper-dictate/config.yaml` or `.env`)
- Sensible defaults with clear override mechanisms

### V. Clean, Testable Code
- Follow PEP 8 Python style guidelines
- Use type hints for all function signatures
- Write unit tests for core modules (audio, transcription, clipboard, notifications)
- Keep modules focused: one responsibility per file
- Document public APIs with docstrings

## Technical Standards

### Audio Processing
- Use 16kHz sample rate (optimal for Whisper)
- Record in mono WAV format
- Implement proper audio device detection and selection
- Handle audio backend failures gracefully (pipewire/pulseaudio/ALSA)

### Platform Support
- Primary: Linux (Arch Linux with i3)
- Support multiple audio backends: sounddevice, portaudio
- Support multiple clipboards: xclip, xsel, wl-clipboard
- Support multiple notification systems: dunst, notify-send

### Dependencies
- Keep dependencies minimal and well-tested
- Pin versions in `requirements.txt` for reproducibility
- Document all system dependencies in README

## Development Workflow

### Code Review
- All changes require code review before merge
- Verify tests pass: `pytest tests/`
- Check linting: `flake8 whisper_dictate/`
- Test on actual hardware with real audio input

### Testing Strategy
- Unit tests for pure functions and utilities
- Integration tests for external API calls (mocked)
- Manual testing checklist for audio/clipboard/notification modules

## Governance

- Constitution supersedes all other practices
- Amendments require PR with rationale and migration plan
- All PRs must verify compliance with these principles
- Complexity must be justified - prefer simple solutions

**Version**: 1.0.0 | **Ratified**: 2026-02-15 | **Last Amended**: 2026-02-15
