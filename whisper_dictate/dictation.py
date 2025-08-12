"""Main dictation service orchestrating audio recording and transcription."""

import logging
from pathlib import Path
from typing import Optional

from whisper_dictate.config import AppConfig
from whisper_dictate.audio import AudioRecorder
from whisper_dictate.transcription import WhisperTranscriber, TranscriptionResult
from whisper_dictate.clipboard import ClipboardManager

logger = logging.getLogger(__name__)


class DictationService:
    """WHY THIS EXISTS: Dictation workflow needs to be orchestrated to provide
    a seamless user experience from recording to clipboard.
    
    RESPONSIBILITY: Coordinate audio recording, transcription, and clipboard operations.
    BOUNDARIES:
    - DOES: Manage the complete dictation workflow
    - DOES NOT: Handle user interface or command-line parsing
    
    RELATIONSHIPS:
    - DEPENDS ON: AudioRecorder, WhisperTranscriber, ClipboardManager
    - USED BY: CLI interface for dictation operations
    """
    
    def __init__(self, config: AppConfig) -> None:
        """Initialize dictation service with configuration.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.audio_recorder = AudioRecorder(config.audio)
        self.transcriber = WhisperTranscriber(config.openai)
        self.clipboard = ClipboardManager()
    
    def dictate(self, duration: Optional[float] = None) -> Optional[TranscriptionResult]:
        """WHY THIS EXISTS: Users need a single method to perform complete
        dictation workflow without managing individual components.
        
        RESPONSIBILITY: Execute complete dictation workflow.
        BOUNDARIES:
        - DOES: Record, transcribe, and optionally copy to clipboard
        - DOES NOT: Handle user interaction or error display
        
        Args:
            duration: Recording duration in seconds (uses config default if None)
            
        Returns:
            Optional[TranscriptionResult]: Transcription result if successful, None if failed
            
        Raises:
            Exception: Re-raises any exceptions from underlying services
        """
        audio_file: Optional[Path] = None
        
        try:
            # Record audio
            logger.info("Starting dictation workflow")
            audio_file = self.audio_recorder.record_to_file(duration)
            
            # Transcribe audio
            result = self.transcriber.transcribe_audio(audio_file)
            
            # Copy to clipboard if enabled
            if self.config.copy_to_clipboard:
                success = self.clipboard.copy_to_clipboard(result.text)
                if success:
                    logger.info("Transcription copied to clipboard")
                else:
                    logger.warning("Failed to copy to clipboard")
            
            logger.info("Dictation workflow completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Dictation workflow failed: {e}")
            raise
        finally:
            # Clean up temporary audio file
            if audio_file and audio_file.exists():
                try:
                    audio_file.unlink()
                    logger.debug(f"Cleaned up temporary file: {audio_file}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file: {e}")
    
    def get_system_info(self) -> dict:
        """WHY THIS EXISTS: Users need diagnostic information to troubleshoot
        configuration issues.
        
        RESPONSIBILITY: Provide system diagnostic information.
        BOUNDARIES:
        - DOES: Gather system information for diagnostics
        - DOES NOT: Perform system modifications
        
        Returns:
            dict: System diagnostic information
        """
        return {
            "audio_devices": self.audio_recorder.get_audio_devices(),
            "clipboard_tools": self.clipboard.available_tools,
            "config": {
                "audio_sample_rate": self.config.audio.sample_rate,
                "audio_channels": self.config.audio.channels,
                "audio_duration": self.config.audio.duration,
                "copy_to_clipboard": self.config.copy_to_clipboard,
                "openai_model": self.config.openai.model
            }
        }