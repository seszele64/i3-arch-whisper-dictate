"""Database-backed logging handler for whisper-dictate.

Provides a custom logging handler that writes log entries to the SQLite database
in addition to file-based logging. This enables structured log querying and filtering.
"""

import asyncio
import logging
import sqlite3
from typing import Any, Optional

from whisper_dictate.database import Database, get_database
from whisper_dictate.config import DatabaseConfig


class DatabaseLogHandler(logging.Handler):
    """Custom logging handler that writes to SQLite database.

    This handler stores log entries in the database with level, message,
    source, timestamp, and optional metadata. It provides dual logging
    by writing to both file and database.

    Attributes:
        _database: Database instance for log storage
        _source_prefix: Prefix for log source names
    """

    def __init__(
        self,
        database: Optional[Database] = None,
        config: Optional[DatabaseConfig] = None,
        source_prefix: str = "whisper_dictate",
    ):
        """Initialize the database log handler.

        Args:
            database: Optional database instance (will create if not provided)
            config: Optional database configuration
            source_prefix: Prefix for log source names
        """
        super().__init__()
        self._database = database
        self._config = config
        self._source_prefix = source_prefix
        self._initialized = False
        self._init_task: Optional[asyncio.Task] = None

    def _ensure_initialized(self) -> None:
        """Ensure database is initialized (synchronous wrapper)."""
        if not self._initialized and self._init_task is None:
            # Will be initialized asynchronously when emit is first called
            pass

    async def _initialize_async(self) -> None:
        """Initialize the database connection asynchronously."""
        if self._initialized:
            return

        if self._database is None:
            if self._config is None:
                self._config = DatabaseConfig()
            self._database = get_database(self._config)
            await self._database.initialize()

        self._initialized = True

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to the database.

        This method schedules the actual database write asynchronously
        to avoid blocking the logging thread.

        Args:
            record: Log record to emit
        """
        # Schedule async write if not already done
        if not self._initialized:
            if self._init_task is None:
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        self._init_task = loop.create_task(self._initialize_async())
                    else:
                        # Synchronous context - initialize immediately
                        asyncio.run(self._initialize_async())
                        self._initialized = True
                except RuntimeError:
                    # No event loop - will initialize on next async call
                    return

            if self._init_task and not self._init_task.done():
                # Add callback to write log after initialization
                self._init_task.add_done_callback(lambda _: self._emit_async(record))
                return

        # Already initialized - write directly
        if self._initialized:
            self._emit_async(record)

    def _emit_async(self, record: logging.LogRecord) -> None:
        """Emit log record asynchronously.

        Args:
            record: Log record to emit
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._write_log(record))
            else:
                asyncio.run(self._write_log(record))
        except RuntimeError:
            # Cannot get event loop - skip database logging
            pass

    async def _write_log(self, record: logging.LogRecord) -> None:
        """Write log record to database.

        Args:
            record: Log record to write
        """
        if self._database is None:
            return

        try:
            # Get the source module name
            source = (
                f"{self._source_prefix}.{record.module}"
                if record.module
                else self._source_prefix
            )

            # Extract metadata from record if present
            metadata: Optional[dict[str, Any]] = None
            if hasattr(record, "metadata"):
                metadata = record.metadata

            # Add extra fields to metadata
            if record.exc_info:
                metadata = metadata or {}
                metadata["exception"] = self.format(record)

            await self._database.create_log(
                level=record.levelname,
                message=record.getMessage(),
                source=source,
                metadata=metadata,
            )
        except Exception:
            # Don't let logging failures break the application
            # File logging will still work
            pass

    async def close(self) -> None:
        """Close the handler and cleanup resources."""
        await super().close()
        if self._database:
            await self._database.close()
            self._database = None
            self._initialized = False


class SyncDatabaseLogHandler:
    """Synchronous wrapper for database logging.

    This class provides a synchronous interface for use with logging.config
    or other synchronous logging setup code. It buffers logs and writes
    them to the database in batches.
    """

    def __init__(
        self,
        database_path: str,
        source_prefix: str = "whisper_dictate",
        retention_days: int = 30,
    ):
        """Initialize the synchronous handler.

        Args:
            database_path: Path to the SQLite database
            source_prefix: Prefix for log source names
            retention_days: Number of days to retain logs
        """
        from pathlib import Path

        self._db_path = Path(database_path)
        self._source_prefix = source_prefix
        self._retention_days = retention_days
        self._connection: Optional[sqlite3.Connection] = None

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._connection is None:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            self._connection = sqlite3.connect(str(self._db_path))
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to the database (synchronous).

        Args:
            record: Log record to emit
        """
        try:
            conn = self._get_connection()
            source = (
                f"{self._source_prefix}.{record.module}"
                if record.module
                else self._source_prefix
            )

            # Extract metadata
            metadata = None
            if hasattr(record, "metadata"):
                import json

                metadata = json.dumps(record.metadata)

            conn.execute(
                "INSERT INTO logs (level, message, source, metadata_json) VALUES (?, ?, ?, ?)",
                (record.levelname, record.getMessage(), source, metadata),
            )
            conn.commit()
        except Exception:
            # Silently ignore logging failures
            pass

    def flush(self) -> None:
        """Flush any buffered logs."""
        if self._connection:
            self._connection.commit()

    def close(self) -> None:
        """Close the handler."""
        if self._connection:
            self._connection.close()
            self._connection = None


def setup_dual_logging(
    level: str = "INFO",
    database: Optional[Database] = None,
    config: Optional[DatabaseConfig] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """Setup dual logging (file + database).

    This function configures logging to write to both file and database,
    providing both persistent file logs for debugging and database logs
    for structured querying.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        database: Optional database instance
        config: Optional database configuration
        log_file: Optional custom log file path

    Returns:
        logging.Logger: Configured root logger
    """
    from pathlib import Path

    # Create log directory
    if log_file:
        log_path = Path(log_file)
    else:
        log_dir = Path.home() / ".local" / "share" / "whisper-dictate"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "whisper-dictate.log"

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers
    root_logger.handlers.clear()

    # File handler
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(getattr(logging, level.upper()))
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Database handler (if database is available)
    if database or config:
        db_handler = DatabaseLogHandler(database=database, config=config)
        db_handler.setLevel(getattr(logging, level.upper()))
        db_handler.setFormatter(formatter)
        root_logger.addHandler(db_handler)

    return root_logger
