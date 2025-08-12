"""OpenAI Whisper API integration with strong typing."""

import logging
from pathlib import Path
from typing import Optional

import openai
from openai import OpenAI

from .config import OpenAIConfig

logger = logging.getLogger(__name__)


class TranscriptionResult:
    """WHY THIS EXISTS: Transcription results need structured representation
    to provide consistent handling and error information.
    
    RESPONSIBILITY: Encapsulate transcription results with metadata.
    BOUNDARIES:
    - DOES: Store transcription text and metadata
    - DOES NOT: Handle API calls or file operations
    """
    
    def __init__(self, text: str, language: Optional[str] = None) -> None:
        """Initialize transcription result.
        
        Args:
            text: Transcribed text
            language: Detected language code (optional)
        """
        self.text = text
        self.language = language
    
    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return f"TranscriptionResult(text='{self.text[:50]}...', language={self.language})"


class WhisperTranscriber:
    """WHY THIS EXISTS: OpenAI Whisper API integration needs to be encapsulated
    to provide consistent error handling and configuration management.
    
    RESPONSIBILITY: Transcribe audio files using OpenAI Whisper API.
    BOUNDARIES:
    - DOES: Handle API calls to OpenAI Whisper
    - DOES NOT: Handle audio recording, file management, or clipboard operations
    
    RELATIONSHIPS:
    - DEPENDS ON: OpenAIConfig for API settings
    - USED BY: DictationService for transcription
    """
    
    def __init__(self, config: OpenAIConfig) -> None:
        """Initialize Whisper transcriber with configuration.
        
        Args:
            config: OpenAI API configuration
        """
        self.config = config
        self.client = OpenAI(api_key=config.api_key)
    
    def transcribe_audio(self, audio_file: Path) -> TranscriptionResult:
        """WHY THIS EXISTS: Audio transcription needs to be handled consistently
        with proper error handling and result formatting.
        
        RESPONSIBILITY: Transcribe audio file using OpenAI Whisper API.
        BOUNDARIES:
        - DOES: Make API call and return structured result
        - DOES NOT: Handle file validation or cleanup
        
        Args:
            audio_file: Path to audio file to transcribe
            
        Returns:
            TranscriptionResult: Structured transcription result
            
        Raises:
            openai.APIError: If API call fails
            IOError: If audio file cannot be read
        """
        if not audio_file.exists():
            raise IOError(f"Audio file not found: {audio_file}")
        
        logger.info(f"Transcribing audio file: {audio_file}")
        
        try:
            with open(audio_file, "rb") as file:
                response = self.client.audio.transcriptions.create(
                    model=self.config.model,
                    file=file,
                    response_format="json"
                )
            
            result = TranscriptionResult(
                text=response.text,
                language=getattr(response, 'language', None)
            )
            
            logger.info(
                f"Transcription completed: {len(result.text)} characters, "
                f"language={result.language}"
            )
            
            return result
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during transcription: {e}")
            raise