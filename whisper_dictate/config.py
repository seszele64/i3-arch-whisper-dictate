"""Configuration management for whisper-dictate."""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class DatabaseConfig(BaseModel):
    """WHY THIS EXISTS: Database configuration needs to follow XDG
    Base Directory spec for proper Linux integration.

    RESPONSIBILITY: Define database storage settings.
    BOUNDARIES:
    - DOES: Provide path configuration for database and recordings
    - DOES NOT: Handle actual database operations
    """

    path: Optional[Path] = Field(
        default=None, description="Database file path (defaults to XDG data directory)"
    )
    recordings_path: Optional[Path] = Field(
        default=None,
        description="Recordings directory path (defaults to XDG data directory)",
    )
    log_retention_days: int = Field(
        default=30,
        description="Number of days to retain database logs",
    )
    min_free_space_mb: int = Field(
        default=100,
        description="Minimum free disk space required in MB before recording",
    )

    def get_database_path(self) -> Path:
        """Get the full database file path.

        Returns:
            Path: Full path to the database file
        """
        if self.path:
            return self.path

        # Use XDG Base Directory spec: ~/.local/share/whisper-dictate/
        data_dir = (
            Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share"))
            / "whisper-dictate"
        )
        return data_dir / "whisper-dictate.db"

    def get_recordings_path(self) -> Path:
        """Get the full recordings directory path.

        Returns:
            Path: Full path to the recordings directory
        """
        if self.recordings_path:
            return self.recordings_path

        # Use XDG Base Directory spec: ~/.local/share/whisper-dictate/recordings/
        return (
            Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share"))
            / "whisper-dictate"
            / "recordings"
        )


class AudioConfig(BaseModel):
    """WHY THIS EXISTS: Audio recording parameters need to be configurable
    for different environments and use cases.

    RESPONSIBILITY: Define audio recording settings with sensible defaults.
    BOUNDARIES:
    - DOES: Provide typed configuration for audio parameters
    - DOES NOT: Handle actual audio recording or validation
    """

    sample_rate: int = Field(default=16000, description="Audio sample rate in Hz")
    channels: int = Field(default=1, description="Number of audio channels")
    duration: float = Field(
        default=5.0, description="Maximum recording duration in seconds"
    )
    device: Optional[int | str] = Field(
        default=None, description="Audio input device index or name"
    )
    mp3_enabled: bool = Field(
        default=True,
        description="Enable MP3 conversion before API upload. "
        "Reduces file size by 80-90% with no impact on transcription quality. "
        "Set to False to keep original WAV format.",
    )
    mp3_bitrate: str = Field(
        default="128k",
        description="MP3 encoding bitrate (e.g., '64k', '128k', '192k'). "
        "Higher values produce larger files with marginal quality improvement for speech. "
        "'128k' is recommended for voice transcription.",
    )
    keep_wav: bool = Field(
        default=False,
        description="Keep original WAV file after MP3 conversion. "
        "When False (default), WAV is deleted after successful MP3 creation to save space. "
        "Set to True if you need to preserve original recordings.",
    )


class OpenAIConfig(BaseModel):
    """WHY THIS EXISTS: OpenAI API configuration needs to be centralized
    and validated to prevent runtime errors.

    RESPONSIBILITY: Manage OpenAI API settings with validation.
    BOUNDARIES:
    - DOES: Store and validate API configuration
    - DOES NOT: Handle API calls or authentication
    """

    api_key: str = Field(description="OpenAI API key")
    model: str = Field(default="whisper-1", description="Whisper model to use")
    timeout: float = Field(default=30.0, description="API request timeout in seconds")


class AppConfig(BaseModel):
    """WHY THIS EXISTS: Application configuration needs to be centralized
    for easy management and testing.

    RESPONSIBILITY: Aggregate all configuration sections.
    BOUNDARIES:
    - DOES: Provide typed access to all configuration
    - DOES NOT: Handle configuration persistence or validation
    """

    database: DatabaseConfig = Field(default_factory=lambda: DatabaseConfig())
    audio: AudioConfig = Field(default_factory=AudioConfig)
    openai: OpenAIConfig = Field(
        default_factory=lambda: OpenAIConfig(api_key=os.getenv("OPENAI_API_KEY", ""))
    )
    log_level: str = Field(default="INFO", description="Logging level")
    copy_to_clipboard: bool = Field(
        default=True, description="Copy transcription to clipboard"
    )


def load_config() -> AppConfig:
    """WHY THIS EXISTS: Configuration loading needs to be centralized
    to ensure consistent initialization across the application.

    RESPONSIBILITY: Load and validate configuration from environment.
    BOUNDARIES:
    - DOES: Load configuration from environment variables
    - DOES NOT: Handle configuration file management

    Returns:
        AppConfig: Validated application configuration

    Raises:
        ValueError: If required configuration is missing
    """
    config = AppConfig()

    if not config.openai.api_key:
        raise ValueError(
            "OpenAI API key not found. Set OPENAI_API_KEY environment variable."
        )

    return config
