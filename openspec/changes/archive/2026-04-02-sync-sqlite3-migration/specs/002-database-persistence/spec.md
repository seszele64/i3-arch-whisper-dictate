## MODIFIED Requirements

### Requirement: Database schema: recordings table
The system SHALL use `sqlite3` library (Python standard library) for synchronous SQLite operations.

#### Scenario: Create recordings table with proper schema
- **WHEN** the database is initialized
- **THEN** the system creates a `recordings` table with the following schema:
  - `id` INTEGER PRIMARY KEY AUTOINCREMENT
  - `file_path` TEXT NOT NULL (path to audio file)
  - `timestamp` TEXT NOT NULL DEFAULT (SQLite datetime format)
  - `duration` REAL (recording duration in seconds)
  - `format` TEXT NOT NULL DEFAULT 'wav' (audio format)
  - `sample_rate` INTEGER (audio sample rate, e.g., 16000, 44100)
  - `channels` INTEGER (number of audio channels)
  - `created_at` TEXT NOT NULL DEFAULT (SQLite datetime format)

---

### Requirement: Database initialization on first run
The system SHALL use Python's standard library `sqlite3` (instead of `aiosqlite`) for all database operations. All operations are synchronous — no `asyncio.run()` wrappers needed.

#### Scenario: Initialize database on first run
- **WHEN** the application starts and the database file does not exist
- **THEN** the system creates the database at `~/.local/share/whisper-dictate/whisper-dictate.db` using `sqlite3.connect()` with all required tables

#### Scenario: Skip initialization when database exists
- **WHEN** the application starts and the database file already exists
- **THEN** the system opens the existing database using `sqlite3.connect()` without recreating tables

#### Scenario: Create database directory if missing
- **WHEN** the application starts and the parent directory does not exist
- **THEN** the system creates the directory structure before creating the database

---

### Requirement: Database connection management
The system SHALL manage sqlite3 connections synchronously with proper lifecycle handling.

#### Scenario: Singleton database instance
- **WHEN** `get_database()` is called multiple times
- **THEN** the system returns the same database instance (singleton pattern)

#### Scenario: Lazy connection initialization
- **WHEN** the database module is imported
- **THEN** no connection is created until first database operation

#### Scenario: Connection reuse across operations
- **WHEN** multiple database operations are performed
- **THEN** the system reuses the same connection for all operations

#### Scenario: Close database connection
- **WHEN** `db.close()` is called or the context manager exits
- **THEN** the system properly closes the sqlite3 connection

---

### Requirement: Synchronous operation pattern
The system SHALL provide fully synchronous database operations without async/await or `asyncio.run()` wrappers.

#### Scenario: Direct function calls work without asyncio.run()
- **WHEN** database methods are called directly (e.g., `db.get_recordings()`)
- **THEN** the operation executes synchronously and returns the result immediately

#### Scenario: No event loop required
- **WHEN** database operations are performed
- **THEN** no asyncio event loop is created or used

#### Scenario: Thread-safe connection access
- **WHEN** the database is accessed from the main thread
- **THEN** the sqlite3 connection operates correctly with proper locking if needed
