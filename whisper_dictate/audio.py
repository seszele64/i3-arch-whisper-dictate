"""Audio recording functionality with strong typing."""

import tempfile
import logging
from typing import Optional, Tuple
from pathlib import Path

import sounddevice as sd
import soundfile as sf

from whisper_dictate.config import AudioConfig

logger = logging.getLogger(__name__)


class AudioRecorder:
    """WHY THIS EXISTS: Audio recording needs to be encapsulated to provide
    consistent interface and error handling across the application.
    
    RESPONSIBILITY: Record audio from system microphone with configurable parameters.
    BOUNDARIES:
    - DOES: Record audio to temporary files with specified parameters
    - DOES NOT: Handle transcription, clipboard operations, or user interface
    
    RELATIONSHIPS:
    - DEPENDS ON: AudioConfig for recording parameters
    - USED BY: DictationService for audio capture
    """
    
    def __init__(self, config: AudioConfig) -> None:
        """Initialize audio recorder with configuration.
        
        Args:
            config: Audio recording configuration
        """
        self.config = config
        
    def record_to_file(self, duration: Optional[float] = None) -> Path:
        """WHY THIS EXISTS: Recording audio directly to files prevents
        memory issues with large recordings and provides consistent file handling.
        
        RESPONSIBILITY: Record audio and save to temporary WAV file.
        BOUNDARIES:
        - DOES: Record audio for specified duration to temporary file
        - DOES NOT: Handle transcription or file cleanup
        
        Args:
            duration: Recording duration in seconds (uses config default if None)
            
        Returns:
            Path: Path to temporary WAV file containing recorded audio
            
        Raises:
            sd.PortAudioError: If audio device access fails
            IOError: If file operations fail
        """
        duration = duration or self.config.duration
        
        logger.info(
            f"Starting audio recording: duration={duration}s, "
            f"sample_rate={self.config.sample_rate}Hz, "
            f"channels={self.config.channels}"
        )
        
        try:
            # Record audio
            audio_data = sd.rec(
                int(duration * self.config.sample_rate),
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                device=self.config.device,
                dtype='float32'
            )
            
            logger.debug("Recording started, waiting for completion...")
            sd.wait()
            logger.debug("Recording completed")
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(
                suffix='.wav',
                delete=False,
                dir=tempfile.gettempdir()
            ) as tmp_file:
                sf.write(
                    tmp_file.name,
                    audio_data,
                    self.config.sample_rate,
                    format='WAV',
                    subtype='PCM_16'
                )
                
                file_path = Path(tmp_file.name)
                logger.info(f"Audio saved to temporary file: {file_path}")
                
                return file_path
                
        except sd.PortAudioError as e:
            logger.error(f"Audio device error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during recording: {e}")
            raise
    
    def get_audio_devices(self) -> Tuple[str, ...]:
        """WHY THIS EXISTS: Users need to know available audio devices
        for configuration and troubleshooting.
        
        RESPONSIBILITY: List available audio input devices.
        BOUNDARIES:
        - DOES: Query and return device names
        - DOES NOT: Handle device selection or configuration
        
        Returns:
            Tuple[str, ...]: Names of available audio input devices
        """
        devices = sd.query_devices()
        input_devices = tuple(
            device['name'] for device in devices
            if device['max_input_channels'] > 0
        )
        
        logger.debug(f"Found {len(input_devices)} audio input devices")
        return input_devices