"""Database module for whisper-dictate.

Provides async SQLite database operations using aiosqlite with:
- Connection management via context manager
- Schema versioning and migrations
- Automatic table creation on initialization
- Integrity checking on startup
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterator, Optional

import aiosqlite

from whisper_dictate.config import DatabaseConfig

logger = logging.getLogger(__name__)

# Current schema version
CURRENT_SCHEMA_VERSION = 1


class Database:
    """Async SQLite database manager for whisper-dictate.

    Provides connection management, schema versioning, migrations,
    and integrity checking.
    """

    def __init__(self, config: DatabaseConfig):
        """Initialize database with configuration.

        Args:
            config: Database configuration containing path settings
        """
        self._config = config
        self._db_path = config.get_database_path()
        self._connection: Optional[aiosqlite.Connection] = None
        self._lock = asyncio.Lock()

    @property
    def path(self) -> Path:
        """Get the database file path.

        Returns:
            Path: Full path to the database file
        """
        return self._db_path

    async def initialize(self) -> None:
        """Initialize the database.

        Creates the database directory if it doesn't exist, establishes
        connection, and runs migrations if needed.
        """
        # Create database directory if it doesn't exist
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initializing database at {self._db_path}")

        # Connect and configure database
        await self._connect()
        await self._configure()

        # Run migrations
        await self._migrate()

        # Verify integrity
        await self._check_integrity()

        logger.info("Database initialized successfully")

    async def close(self) -> None:
        """Close the database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.debug("Database connection closed")

    @asynccontextmanager
    async def connection(self) -> AsyncIterator[aiosqlite.Connection]:
        """Get a database connection as a context manager.

        Yields:
            aiosqlite.Connection: Database connection

        Raises:
            RuntimeError: If database is not initialized
        """
        if not self._connection:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        async with self._lock:
            yield self._connection

    async def execute(self, query: str, parameters: tuple = ()) -> aiosqlite.Cursor:
        """Execute a query and return the cursor.

        Args:
            query: SQL query to execute
            parameters: Query parameters

        Returns:
            aiosqlite.Cursor: Result cursor
        """
        async with self.connection() as conn:
            return await conn.execute(query, parameters)

    async def executemany(self, query: str, parameters: list) -> None:
        """Execute a query with multiple parameter sets.

        Args:
            query: SQL query to execute
            parameters: List of parameter tuples
        """
        async with self.connection() as conn:
            await conn.executemany(query, parameters)

    async def fetchone(self, query: str, parameters: tuple = ()) -> Optional[tuple]:
        """Execute a query and fetch one result.

        Args:
            query: SQL query to execute
            parameters: Query parameters

        Returns:
            Optional[tuple]: Result row or None
        """
        async with self.connection() as conn:
            cursor = await conn.execute(query, parameters)
            return await cursor.fetchone()

    async def fetchall(self, query: str, parameters: tuple = ()) -> list[tuple]:
        """Execute a query and fetch all results.

        Args:
            query: SQL query to execute
            parameters: Query parameters

        Returns:
            list[tuple]: Result rows
        """
        async with self.connection() as conn:
            cursor = await conn.execute(query, parameters)
            return await cursor.fetchall()

    async def _connect(self) -> None:
        """Establish database connection."""
        self._connection = await aiosqlite.connect(
            self._db_path,
            isolation_level=None,  # Autocommit mode
        )
        # Enable WAL mode for better crash recovery
        await self._connection.execute("PRAGMA journal_mode=WAL")
        # Enable foreign keys
        await self._connection.execute("PRAGMA foreign_keys=ON")

        logger.debug("Database connection established")

    async def _configure(self) -> None:
        """Configure database settings."""
        async with self.connection() as conn:
            # Set busy timeout to 5 seconds
            await conn.execute("PRAGMA busy_timeout=5000")
            # Enable synchronous NORMAL for better performance
            await conn.execute("PRAGMA synchronous=NORMAL")

    async def _check_integrity(self) -> None:
        """Verify database integrity by checking all tables exist.

        Raises:
            RuntimeError: If integrity check fails
        """
        logger.info("Running database integrity check...")

        expected_tables = [
            "schema_versions",
            "recordings",
            "transcripts",
            "logs",
            "state",
        ]

        async with self.connection() as conn:
            cursor = await conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            rows = await cursor.fetchall()
            existing_tables = {row[0] for row in rows}

        missing_tables = set(expected_tables) - existing_tables
        if missing_tables:
            raise RuntimeError(
                f"Database integrity check failed. Missing tables: {missing_tables}"
            )

        logger.info(f"Integrity check passed. Found tables: {sorted(existing_tables)}")

    async def _migrate(self) -> None:
        """Run database migrations."""
        current_version = await self._get_schema_version()

        if current_version == 0:
            logger.info("No schema version found. Creating initial schema...")
            await self._create_schema()
            await self._set_schema_version(CURRENT_SCHEMA_VERSION)
        elif current_version < CURRENT_SCHEMA_VERSION:
            logger.info(
                f"Migrating schema from version {current_version} "
                f"to {CURRENT_SCHEMA_VERSION}..."
            )
            await self._run_migrations(current_version, CURRENT_SCHEMA_VERSION)
        else:
            logger.debug(f"Schema version is current: {current_version}")

    async def _get_schema_version(self) -> int:
        """Get the current schema version.

        Returns:
            int: Schema version, or 0 if not set
        """
        try:
            async with self.connection() as conn:
                cursor = await conn.execute(
                    "SELECT version FROM schema_versions ORDER BY applied_at DESC LIMIT 1"
                )
                row = await cursor.fetchone()
                return row[0] if row else 0
        except aiosqlite.OperationalError:
            return 0

    async def _set_schema_version(self, version: int) -> None:
        """Set the schema version in the database.

        Args:
            version: Schema version number
        """
        async with self.connection() as conn:
            await conn.execute(
                "INSERT INTO schema_versions (version) VALUES (?) "
                "ON CONFLICT(version) DO NOTHING",
                (version,),
            )
        logger.info(f"Schema version set to {version}")

    async def _create_schema(self) -> None:
        """Create all database tables."""
        async with self.connection() as conn:
            # Schema versions table - tracks applied migrations
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version INTEGER NOT NULL UNIQUE,
                    applied_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
            """)

            # Recordings table - stores audio recording metadata
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS recordings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                    duration REAL,
                    format TEXT NOT NULL DEFAULT 'wav',
                    sample_rate INTEGER,
                    channels INTEGER,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
            """)

            # Transcripts table - stores transcription results
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS transcripts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recording_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    language TEXT,
                    model_used TEXT NOT NULL DEFAULT 'whisper-1',
                    confidence REAL,
                    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY (recording_id) REFERENCES recordings(id) ON DELETE CASCADE
                )
            """)

            # Logs table - stores application logs
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    source TEXT,
                    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                    metadata_json TEXT
                )
            """)

            # State table - stores key-value application state
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS state (
                    key TEXT PRIMARY KEY,
                    value_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
            """)

            # Create indexes for better query performance
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_recordings_timestamp "
                "ON recordings(timestamp)"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_transcripts_recording_id "
                "ON transcripts(recording_id)"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_transcripts_timestamp "
                "ON transcripts(timestamp)"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level)"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp)"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_logs_source ON logs(source)"
            )

        logger.info("Database schema created")

    async def _run_migrations(self, from_version: int, to_version: int) -> None:
        """Run migrations from one version to another.

        Args:
            from_version: Current schema version
            to_version: Target schema version
        """
        # For now, we only have version 1, so this is a placeholder
        # for future migrations
        for version in range(from_version + 1, to_version + 1):
            await self._run_migration(version)
            await self._set_schema_version(version)

    async def _run_migration(self, version: int) -> None:
        """Run a specific migration version.

        Args:
            version: Migration version to run
        """
        logger.info(f"Running migration version {version}")

        # Placeholder for future migrations
        # Example:
        # if version == 2:
        #     await self._migration_002()

        logger.info(f"Migration version {version} completed")

    # ============ Recording Operations ============

    async def create_recording(
        self,
        file_path: str,
        duration: Optional[float] = None,
        format: str = "wav",
        sample_rate: Optional[int] = None,
        channels: Optional[int] = None,
    ) -> int:
        """Create a new recording entry.

        Args:
            file_path: Path to the audio file
            duration: Recording duration in seconds
            format: Audio format (default: wav)
            sample_rate: Audio sample rate
            channels: Number of audio channels

        Returns:
            int: ID of the created recording
        """
        async with self.connection() as conn:
            cursor = await conn.execute(
                """
                INSERT INTO recordings (file_path, duration, format, sample_rate, channels)
                VALUES (?, ?, ?, ?, ?)
                """,
                (file_path, duration, format, sample_rate, channels),
            )
            return cursor.lastrowid

    async def get_recording(self, recording_id: int) -> Optional[dict[str, Any]]:
        """Get a recording by ID.

        Args:
            recording_id: Recording ID

        Returns:
            Optional[dict]: Recording data or None
        """
        row = await self.fetchone(
            "SELECT * FROM recordings WHERE id = ?", (recording_id,)
        )
        if row:
            return self._row_to_dict(
                row,
                [
                    "id",
                    "file_path",
                    "timestamp",
                    "duration",
                    "format",
                    "sample_rate",
                    "channels",
                    "created_at",
                ],
            )
        return None

    async def get_recording_with_audio_path(
        self, recording_id: int
    ) -> Optional[dict[str, Any]]:
        """Get a recording by ID with resolved absolute audio path.

        Args:
            recording_id: Recording ID

        Returns:
            Optional[dict]: Recording data with absolute_path field, or None
        """
        from whisper_dictate.audio_storage import get_audio_storage

        recording = await self.get_recording(recording_id)
        if recording:
            audio_storage = get_audio_storage(self._config)
            recording["absolute_path"] = str(
                audio_storage.get_audio_path(recording["file_path"])
            )
        return recording

    async def list_recordings(
        self, limit: int = 50, offset: int = 0
    ) -> list[dict[str, Any]]:
        """List recordings with pagination.

        Args:
            limit: Maximum number of recordings to return
            offset: Number of recordings to skip

        Returns:
            list[dict]: List of recording data
        """
        rows = await self.fetchall(
            """
            SELECT * FROM recordings 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
        return [
            self._row_to_dict(
                row,
                [
                    "id",
                    "file_path",
                    "timestamp",
                    "duration",
                    "format",
                    "sample_rate",
                    "channels",
                    "created_at",
                ],
            )
            for row in rows
        ]

    async def delete_recording(self, recording_id: int) -> bool:
        """Delete a recording and its transcript.

        Args:
            recording_id: Recording ID

        Returns:
            bool: True if deleted, False if not found
        """
        result = await self.execute(
            "DELETE FROM recordings WHERE id = ?", (recording_id,)
        )
        return result.rowcount > 0

    # ============ Transcript Operations ============

    async def create_transcript(
        self,
        recording_id: int,
        text: str,
        language: Optional[str] = None,
        model_used: str = "whisper-1",
        confidence: Optional[float] = None,
    ) -> int:
        """Create a new transcript entry.

        Args:
            recording_id: ID of the recording
            text: Transcribed text
            language: Detected language
            model_used: Whisper model used
            confidence: Transcription confidence score

        Returns:
            int: ID of the created transcript
        """
        async with self.connection() as conn:
            cursor = await conn.execute(
                """
                INSERT INTO transcripts 
                (recording_id, text, language, model_used, confidence)
                VALUES (?, ?, ?, ?, ?)
                """,
                (recording_id, text, language, model_used, confidence),
            )
            return cursor.lastrowid

    async def get_transcript(self, transcript_id: int) -> Optional[dict[str, Any]]:
        """Get a transcript by ID.

        Args:
            transcript_id: Transcript ID

        Returns:
            Optional[dict]: Transcript data or None
        """
        row = await self.fetchone(
            "SELECT * FROM transcripts WHERE id = ?", (transcript_id,)
        )
        if row:
            return self._row_to_dict(
                row,
                [
                    "id",
                    "recording_id",
                    "text",
                    "language",
                    "model_used",
                    "confidence",
                    "timestamp",
                    "created_at",
                ],
            )
        return None

    async def get_transcript_by_recording(
        self, recording_id: int
    ) -> Optional[dict[str, Any]]:
        """Get transcript for a recording.

        Args:
            recording_id: Recording ID

        Returns:
            Optional[dict]: Transcript data or None
        """
        row = await self.fetchone(
            "SELECT * FROM transcripts WHERE recording_id = ?", (recording_id,)
        )
        if row:
            return self._row_to_dict(
                row,
                [
                    "id",
                    "recording_id",
                    "text",
                    "language",
                    "model_used",
                    "confidence",
                    "timestamp",
                    "created_at",
                ],
            )
        return None

    async def search_transcripts(
        self, query: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Search transcripts by text (case-insensitive substring match).

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            list[dict]: List of matching transcript entries with recording info
        """
        search_pattern = f"%{query}%"
        rows = await self.fetchall(
            """
            SELECT t.*, r.file_path, r.timestamp as recording_timestamp, r.duration
            FROM transcripts t
            JOIN recordings r ON t.recording_id = r.id
            WHERE t.text LIKE ?
            ORDER BY t.timestamp DESC
            LIMIT ?
            """,
            (search_pattern, limit),
        )
        return [
            self._row_to_dict(
                row,
                [
                    "id",
                    "recording_id",
                    "text",
                    "language",
                    "model_used",
                    "confidence",
                    "timestamp",
                    "created_at",
                    "file_path",
                    "recording_timestamp",
                    "duration",
                ],
            )
            for row in rows
        ]

    async def list_transcriptions(
        self, limit: int = 50, date: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """List transcriptions with optional date filtering and pagination.

        Args:
            limit: Maximum number of results to return
            date: Optional date filter (YYYY-MM-DD format)

        Returns:
            list[dict]: List of transcription entries with recording info
        """
        if date:
            rows = await self.fetchall(
                """
                SELECT t.*, r.file_path, r.timestamp as recording_timestamp, r.duration
                FROM transcripts t
                JOIN recordings r ON t.recording_id = r.id
                WHERE date(t.timestamp) = date(?)
                ORDER BY t.timestamp DESC
                LIMIT ?
                """,
                (date, limit),
            )
        else:
            rows = await self.fetchall(
                """
                SELECT t.*, r.file_path, r.timestamp as recording_timestamp, r.duration
                FROM transcripts t
                JOIN recordings r ON t.recording_id = r.id
                ORDER BY t.timestamp DESC
                LIMIT ?
                """,
                (limit,),
            )

        return [
            self._row_to_dict(
                row,
                [
                    "id",
                    "recording_id",
                    "text",
                    "language",
                    "model_used",
                    "confidence",
                    "timestamp",
                    "created_at",
                    "file_path",
                    "recording_timestamp",
                    "duration",
                ],
            )
            for row in rows
        ]

    async def get_transcription_with_recording(
        self, transcript_id: int
    ) -> Optional[dict[str, Any]]:
        """Get a transcript with full recording details by transcript ID.

        Args:
            transcript_id: Transcript ID

        Returns:
            Optional[dict]: Transcript data with recording info, or None
        """
        row = await self.fetchone(
            """
            SELECT t.*, r.file_path, r.timestamp as recording_timestamp, r.duration
            FROM transcripts t
            JOIN recordings r ON t.recording_id = r.id
            WHERE t.id = ?
            """,
            (transcript_id,),
        )
        if row:
            return self._row_to_dict(
                row,
                [
                    "id",
                    "recording_id",
                    "text",
                    "language",
                    "model_used",
                    "confidence",
                    "timestamp",
                    "created_at",
                    "file_path",
                    "recording_timestamp",
                    "duration",
                ],
            )
        return None

    # ============ Log Operations ============

    async def create_log(
        self,
        level: str,
        message: str,
        source: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> int:
        """Create a new log entry.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            message: Log message
            source: Source of the log (module name)
            metadata: Additional metadata as JSON

        Returns:
            int: ID of the created log
        """
        metadata_json = json.dumps(metadata) if metadata else None

        async with self.connection() as conn:
            cursor = await conn.execute(
                """
                INSERT INTO logs (level, message, source, metadata_json)
                VALUES (?, ?, ?, ?)
                """,
                (level, message, source, metadata_json),
            )
            return cursor.lastrowid

    async def query_logs(
        self,
        level: Optional[str] = None,
        source: Optional[str] = None,
        from_time: Optional[str] = None,
        to_time: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query logs with filters.

        Args:
            level: Filter by log level
            source: Filter by source
            from_time: Filter by start timestamp (ISO format)
            to_time: Filter by end timestamp (ISO format)
            limit: Maximum number of logs to return

        Returns:
            list[dict]: List of log entries
        """
        query = "SELECT * FROM logs WHERE 1=1"
        params = []

        if level:
            query += " AND level = ?"
            params.append(level.upper())
        if source:
            query += " AND source = ?"
            params.append(source)
        if from_time:
            query += " AND timestamp >= ?"
            params.append(from_time)
        if to_time:
            query += " AND timestamp <= ?"
            params.append(to_time)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        rows = await self.fetchall(query, tuple(params))
        return [
            self._row_to_dict(
                row, ["id", "level", "message", "source", "timestamp", "metadata_json"]
            )
            for row in rows
        ]

    # ============ State Operations ============

    async def set_state(self, key: str, value: Any) -> None:
        """Set a state value.

        Args:
            key: State key
            value: State value (will be JSON serialized)
        """
        value_json = json.dumps(value)

        async with self.connection() as conn:
            await conn.execute(
                """
                INSERT INTO state (key, value_json, updated_at)
                VALUES (?, ?, datetime('now'))
                ON CONFLICT(key) DO UPDATE SET 
                    value_json = excluded.value_json,
                    updated_at = datetime('now')
                """,
                (key, value_json),
            )

    async def get_state(self, key: str) -> Optional[Any]:
        """Get a state value.

        Args:
            key: State key

        Returns:
            Optional[Any]: State value or None
        """
        row = await self.fetchone("SELECT value_json FROM state WHERE key = ?", (key,))
        if row:
            return json.loads(row[0])
        return None

    async def delete_state(self, key: str) -> bool:
        """Delete a state value.

        Args:
            key: State key

        Returns:
            bool: True if deleted, False if not found
        """
        result = await self.execute("DELETE FROM state WHERE key = ?", (key,))
        return result.rowcount > 0

    # ============ Log Retention ============

    async def cleanup_old_logs(self, retention_days: int = 30) -> int:
        """Delete log entries older than the retention period.

        Args:
            retention_days: Number of days to retain logs

        Returns:
            int: Number of deleted log entries
        """
        async with self.connection() as conn:
            cursor = await conn.execute(
                """
                DELETE FROM logs 
                WHERE timestamp < datetime('now', ?)
                """,
                (f"-{retention_days} days",),
            )
            await conn.commit()
            deleted = cursor.rowcount

        if deleted > 0:
            logger.info(
                f"Cleaned up {deleted} old log entries (retention: {retention_days} days)"
            )

        return deleted

    # ============ Utility Methods ============

    @staticmethod
    def _row_to_dict(row: tuple, columns: list[str]) -> dict[str, Any]:
        """Convert a database row to a dictionary.

        Args:
            row: Database row
            columns: Column names

        Returns:
            dict: Row as dictionary
        """
        return dict(zip(columns, row))


# Global database instance
_database: Optional[Database] = None


def get_database(config: Optional[DatabaseConfig] = None) -> Database:
    """Get or create the global database instance.

    Args:
        config: Optional database configuration

    Returns:
        Database: Database instance
    """
    global _database

    if _database is None:
        if config is None:
            config = DatabaseConfig()
        _database = Database(config)

    return _database


async def initialize_database(config: Optional[DatabaseConfig] = None) -> Database:
    """Initialize the database.

    Args:
        config: Optional database configuration

    Returns:
        Database: Initialized database instance
    """
    db = get_database(config)
    await db.initialize()
    return db
