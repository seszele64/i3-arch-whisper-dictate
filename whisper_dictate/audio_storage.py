"""Audio storage management for whisper-dictate.

Provides audio file storage with:
- XDG Base Directory spec compliance
- Date-based directory structure (YYYY/MM/DD)
- Unique filename generation (timestamp + random suffix)
- File save, retrieve, and cleanup operations
"""

import logging
import os
import random
import string
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from whisper_dictate.config import DatabaseConfig

logger = logging.getLogger(__name__)

# Length of random suffix for unique filenames
RANDOM_SUFFIX_LENGTH = 8


def _generate_random_suffix(length: int = RANDOM_SUFFIX_LENGTH) -> str:
    """Generate a random alphanumeric suffix for unique filenames.

    Args:
        length: Length of the random suffix

    Returns:
        str: Random alphanumeric string
    """
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def _generate_unique_filename(
    timestamp: Optional[datetime] = None, suffix: str = "wav"
) -> str:
    """Generate a unique filename with timestamp and random suffix.

    Args:
        timestamp: Datetime for the filename (defaults to now)
        suffix: File extension (without dot)

    Returns:
        str: Unique filename in format YYYYMMDD_HHMMSS_random.wav
    """
    if timestamp is None:
        timestamp = datetime.now()

    date_part = timestamp.strftime("%Y%m%d_%H%M%S")
    random_part = _generate_random_suffix()

    return f"{date_part}_{random_part}.{suffix}"


def _get_date_based_path(base_path: Path, timestamp: Optional[datetime] = None) -> Path:
    """Get the date-based directory path for a recording.

    Creates directory structure: base_path/YYYY/MM/DD/

    Args:
        base_path: Base recordings directory
        timestamp: Datetime for the path (defaults to now)

    Returns:
        Path: Full path to the date-based directory
    """
    if timestamp is None:
        timestamp = datetime.now()

    return (
        base_path
        / f"{timestamp.year:04d}"
        / f"{timestamp.month:02d}"
        / f"{timestamp.day:02d}"
    )


class AudioStorage:
    """Audio storage manager for whisper-dictate.

    Manages audio file storage with XDG Base Directory spec compliance,
    date-based directory structure, and unique filename generation.

    RESPONSIBILITY: Handle all audio file storage operations.
    BOUNDARIES:
    - DOES: Create directories, save/move/retrieve/delete audio files
    - DOES NOT: Handle transcription, database operations, or audio recording
    """

    def __init__(self, config: Optional[DatabaseConfig] = None):
        """Initialize audio storage with configuration.

        Args:
            config: Database configuration containing recordings path
        """
        if config is None:
            config = DatabaseConfig()

        self._config = config
        self._recordings_path = config.get_recordings_path()
        logger.debug(f"AudioStorage initialized with path: {self._recordings_path}")

    @property
    def recordings_path(self) -> Path:
        """Get the base recordings directory path.

        Returns:
            Path: Full path to recordings directory
        """
        return self._recordings_path

    def get_recording_path(self, recording_id: int) -> Optional[Path]:
        """Get the absolute path for a recording by ID.

        Args:
            recording_id: Recording ID

        Returns:
            Optional[Path]: Absolute path to the recording file, or None if not found
        """
        # This is a placeholder - actual implementation will query database
        # The database stores relative paths, this method resolves to absolute
        return self._recordings_path / str(recording_id)

    def ensure_directory_exists(self, directory: Path) -> None:
        """Ensure a directory exists, creating it if necessary.

        Args:
            directory: Directory path to create
        """
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")

    def get_date_directory(
        self, timestamp: Optional[datetime] = None, create: bool = True
    ) -> Path:
        """Get the date-based directory for a recording.

        Args:
            timestamp: Datetime for the directory (defaults to now)
            create: Whether to create the directory if it doesn't exist

        Returns:
            Path: Full path to the date-based directory
        """
        directory = _get_date_based_path(self._recordings_path, timestamp)

        if create:
            self.ensure_directory_exists(directory)

        return directory

    def generate_storage_path(
        self, timestamp: Optional[datetime] = None, suffix: str = "wav"
    ) -> tuple[Path, str]:
        """Generate a unique storage path for a new recording.

        Args:
            timestamp: Datetime for the filename (defaults to now)
            suffix: File extension (without dot)

        Returns:
            tuple[Path, str]: Full file path and the filename
        """
        # Get date-based directory
        directory = self.get_date_directory(timestamp, create=True)

        # Generate unique filename
        filename = _generate_unique_filename(timestamp, suffix)

        # Return full path
        return directory / filename, filename

    def save_audio(
        self,
        source_path: Path,
        timestamp: Optional[datetime] = None,
        suffix: str = "wav",
    ) -> tuple[Path, str]:
        """Save an audio file from temporary storage to persistent storage.

        Uses shutil.move() to atomically move the file from temp to
        persistent storage.

        Args:
            source_path: Path to the source audio file (e.g., temp file)
            timestamp: Datetime for the filename (defaults to now)
            suffix: File extension (without dot)

        Returns:
            tuple[Path, str]: Full path to saved file and relative path from recordings root

        Raises:
            FileNotFoundError: If source file doesn't exist
            IOError: If file move fails
        """
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        # Generate unique storage path
        dest_path, filename = self.generate_storage_path(timestamp, suffix)

        # Ensure destination directory exists
        self.ensure_directory_exists(dest_path.parent)

        # Move file to persistent storage
        try:
            shutil.move(str(source_path), str(dest_path))
            logger.info(f"Audio saved to: {dest_path}")
        except Exception as e:
            logger.error(f"Failed to save audio file: {e}")
            raise IOError(f"Failed to move audio file: {e}") from e

        # Return full path and relative path from recordings root
        relative_path = dest_path.relative_to(self._recordings_path)
        return dest_path, str(relative_path)

    def copy_audio(
        self,
        source_path: Path,
        timestamp: Optional[datetime] = None,
        suffix: str = "wav",
    ) -> tuple[Path, str]:
        """Copy an audio file to persistent storage (keeps original).

        Args:
            source_path: Path to the source audio file
            timestamp: Datetime for the filename (defaults to now)
            suffix: File extension (without dot)

        Returns:
            tuple[Path, str]: Full path to copied file and relative path from recordings root

        Raises:
            FileNotFoundError: If source file doesn't exist
            IOError: If file copy fails
        """
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        # Generate unique storage path
        dest_path, filename = self.generate_storage_path(timestamp, suffix)

        # Ensure destination directory exists
        self.ensure_directory_exists(dest_path.parent)

        # Copy file to persistent storage
        try:
            shutil.copy2(str(source_path), str(dest_path))
            logger.info(f"Audio copied to: {dest_path}")
        except Exception as e:
            logger.error(f"Failed to copy audio file: {e}")
            raise IOError(f"Failed to copy audio file: {e}") from e

        # Return full path and relative path from recordings root
        relative_path = dest_path.relative_to(self._recordings_path)
        return dest_path, str(relative_path)

    def get_audio_path(self, relative_path: str) -> Path:
        """Resolve a relative path to absolute path in recordings directory.

        Args:
            relative_path: Relative path from recordings root

        Returns:
            Path: Absolute path to the audio file
        """
        return self._recordings_path / relative_path

    def get_audio(self, relative_path: str) -> Optional[bytes]:
        """Read audio file contents.

        Args:
            relative_path: Relative path from recordings root

        Returns:
            Optional[bytes]: Audio file contents, or None if not found
        """
        full_path = self.get_audio_path(relative_path)

        if not full_path.exists():
            logger.warning(f"Audio file not found: {full_path}")
            return None

        try:
            return full_path.read_bytes()
        except Exception as e:
            logger.error(f"Failed to read audio file: {e}")
            return None

    def delete_audio(self, relative_path: str) -> bool:
        """Delete an audio file.

        Args:
            relative_path: Relative path from recordings root

        Returns:
            bool: True if deleted, False if not found
        """
        full_path = self.get_audio_path(relative_path)

        if not full_path.exists():
            logger.warning(f"Audio file not found for deletion: {full_path}")
            return False

        try:
            full_path.unlink()
            logger.info(f"Audio file deleted: {full_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete audio file: {e}")
            return False

    def cleanup_empty_directories(self, base_path: Optional[Path] = None) -> int:
        """Remove empty date-based directories.

        Args:
            base_path: Base directory to clean (defaults to recordings path)

        Returns:
            int: Number of directories removed
        """
        if base_path is None:
            base_path = self._recordings_path

        removed_count = 0

        # Walk through year/month/day directories and remove empty ones
        for year_dir in base_path.iterdir():
            if not year_dir.is_dir():
                continue

            for month_dir in year_dir.iterdir():
                if not month_dir.is_dir():
                    continue

                for day_dir in month_dir.iterdir():
                    if not day_dir.is_dir():
                        continue

                    # Check if directory is empty
                    if not any(day_dir.iterdir()):
                        try:
                            day_dir.rmdir()
                            removed_count += 1
                            logger.debug(f"Removed empty directory: {day_dir}")
                        except OSError:
                            pass

                # Check if month directory is empty
                if month_dir.is_dir() and not any(month_dir.iterdir()):
                    try:
                        month_dir.rmdir()
                        removed_count += 1
                        logger.debug(f"Removed empty directory: {month_dir}")
                    except OSError:
                        pass

            # Check if year directory is empty
            if year_dir.is_dir() and not any(year_dir.iterdir()):
                try:
                    year_dir.rmdir()
                    removed_count += 1
                    logger.debug(f"Removed empty directory: {year_dir}")
                except OSError:
                    pass

        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} empty directories")

        return removed_count

    def get_storage_stats(self) -> dict:
        """Get storage statistics.

        Returns:
            dict: Statistics including total files, total size, etc.
        """
        total_files = 0
        total_size = 0

        if self._recordings_path.exists():
            for path in self._recordings_path.rglob("*"):
                if path.is_file():
                    total_files += 1
                    total_size += path.stat().st_size

        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "recordings_path": str(self._recordings_path),
        }


# Global audio storage instance
_audio_storage: Optional[AudioStorage] = None


def get_audio_storage(config: Optional[DatabaseConfig] = None) -> AudioStorage:
    """Get or create the global audio storage instance.

    Args:
        config: Optional database configuration

    Returns:
        AudioStorage: Audio storage instance
    """
    global _audio_storage

    if _audio_storage is None:
        _audio_storage = AudioStorage(config)

    return _audio_storage
