## ADDED Requirements

### Requirement: Database initialization on first run
The system SHALL create the SQLite database and all required tables on first run if they do not exist.

#### Scenario: Initialize database on first run
- **WHEN** the application starts and the database file does not exist
- **THEN** the system creates the database at `~/.local/share/whisper-dictate/whisper-dictate.db` with all required tables

#### Scenario: Skip initialization when database exists
- **WHEN** the application starts and the database file already exists
- **THEN** the system opens the existing database without recreating tables

#### Scenario: Create database directory if missing
- **WHEN** the application starts and the parent directory does not exist
- **THEN** the system creates the directory structure before creating the database

---

### Requirement: Database schema: logs table
The system SHALL use `aiosqlite` library for async SQLite operations.

#### Scenario: Create logs table with proper schema
- **WHEN** the database is initialized
- **THEN** the system creates a `logs` table with the following schema:
  - `id` INTEGER PRIMARY KEY AUTOINCREMENT
  - `level` TEXT NOT NULL (DEBUG, INFO, WARNING, ERROR)
  - `message` TEXT NOT NULL
  - `source` TEXT NOT NULL (module name, e.g., `whisper_dictate.audio`)
  - `timestamp` TEXT NOT NULL (ISO 8601 format)
  - `metadata_json` TEXT (optional JSON-serialized metadata)

---

### Requirement: Database schema versioning
The system SHALL track the database schema version to enable future migrations.

#### Scenario: Store schema version in database
- **WHEN** the database is initialized
- **THEN** the system stores the current schema version in a `schema_versions` table

#### Scenario: Detect schema version mismatch
- **WHEN** the application starts and the stored schema version differs from the expected version
- **THEN** the system runs necessary migration scripts to upgrade the schema

---

### Requirement: Recording metadata storage
The system SHALL store recording metadata in the database after transcription.

#### Scenario: Store recording metadata after transcription
- **WHEN** a recording is successfully transcribed
- **THEN** the system stores the recording file path, timestamp, duration, and format in the `recordings` table

#### Scenario: Retrieve recording by ID
- **WHEN** a request is made to retrieve a recording by its ID
- **THEN** the system returns the recording metadata including file path, timestamp, and duration

#### Scenario: List all recordings with pagination
- **WHEN** a request is made to list all recordings
- **THEN** the system returns a paginated list of recordings ordered by timestamp descending

---

### Requirement: Recording duration calculation
The system SHALL calculate the actual audio file duration after recording completes.

#### Scenario: Calculate duration from audio file after recording
- **GIVEN** a recording has been created in the database with duration=NULL
- **WHEN** the recording stops and the audio file is finalized
- **THEN** the system SHALL calculate the actual duration from the audio file and update the recording entry

#### Scenario: Use soundfile to determine duration
- **WHEN** calculating recording duration
- **THEN** the system SHALL use the soundfile library to read the audio file's actual duration in seconds

---

### Requirement: Transcript storage
The system SHALL store transcripts associated with recordings in the database.

#### Scenario: Store transcript after transcription
- **WHEN** a recording is transcribed successfully
- **THEN** the system stores the transcript text, language, model used, and timestamp in the `transcripts` table linked to the recording

#### Scenario: Retrieve transcript by recording ID
- **WHEN** a request is made to retrieve a transcript by recording ID
- **THEN** the system returns the transcript text and metadata

#### Scenario: Update transcript
- **WHEN** a user updates an existing transcript
- **THEN** the system updates the transcript record with new text and records the update timestamp

---

### Requirement: Database integrity check
The system SHALL verify database integrity on startup.

#### Scenario: Run integrity check on startup
- **WHEN** the application starts
- **THEN** the system runs `PRAGMA integrity_check` and logs any issues found

#### Scenario: Handle corrupted database
- **WHEN** the integrity check finds corruption
- **THEN** the system logs an error and attempts to recover or recreate the database
