## Why

Currently, audio recordings are deleted immediately after transcription, and there is no way to review past transcriptions or access recorded audio files. The application lacks persistent storage for transcripts, logs, and application state, which limits debugging capabilities and prevents users from accessing historical dictation data. This change will add comprehensive persistence capabilities using SQLite for structured data and filesystem storage for audio files.

## What Changes

- Add SQLite database for storing metadata, transcripts, logs, and application state
- Create filesystem storage for audio recordings at `~/.local/share/whisper-dictate/recordings/`
- Implement CLI commands for viewing history (`history` command) and logs (`logs` command)
- Migrate from JSON-based state files to database-backed state
- Add database-backed logging system with structured log storage
- Save audio recordings after transcription instead of deleting them

## Capabilities

### New Capabilities

- **database-persistence**: SQLite database for storing metadata, transcripts, logs, and application state
- **audio-storage**: Filesystem storage for audio recordings with organized directory structure
- **transcript-history**: CLI commands for viewing transcription history and accessing past transcripts
- **structured-logging**: Database-backed logging system with searchable log entries
- **state-migration**: Migration from existing JSON state files to database storage

### Modified Capabilities

- None - this is a new capability set

## Impact

- New dependency: `aiosqlite` for async SQLite operations
- New directory structure: `~/.local/share/whisper-dictate/recordings/`
- Database file: `~/.local/share/whisper-dictate/whisper-dictate.db`
- CLI changes: New `history` and `logs` subcommands added
  - `history` subcommands: `history show <id>`, `history search <query>`, `history delete <id>`
  - `logs` subcommands: `logs --level`, `logs --source`, `logs --from`, `logs --to`, `logs --limit`
- Existing config files may need migration to database
