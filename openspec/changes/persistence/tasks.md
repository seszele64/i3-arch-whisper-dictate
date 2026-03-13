## 1. Database Infrastructure

- [x] 1.1 Create database module with aiosqlite integration
- [x] 1.2 Implement database schema (recordings, transcripts, logs, state, schema_versions tables)
- [x] 1.3 Add database initialization logic with version tracking
- [x] 1.4 Implement schema migration system
- [x] 1.5 Add database integrity check on startup

## 2. Audio Storage

- [x] 2.1 Create audio storage directory management module
- [x] 2.2 Implement date-based directory structure creation
- [x] 2.3 Add audio file save functionality after transcription
- [x] 2.4 Implement unique filename generation with timestamp
- [x] 2.5 Add audio file retrieval by recording ID
- [x] 2.6 Implement audio file cleanup on transcript deletion

## 3. Database Logging

- [x] 3.1 Create database-backed logging handler
- [x] 3.2 Integrate dual logging (file + database)
- [x] 3.3 Implement log query functionality
- [x] 3.4 Add log filtering (by level, source, date range)
- [x] 3.5 Implement log retention cleanup

## 4. Transcription History CLI

- [x] 4.1 Create `history` command group
- [x] 4.2 Implement `history list` with pagination
- [x] 4.3 Implement `history show <id>` for full details
- [x] 4.4 Add `history search <query>` functionality
- [x] 4.5 Implement `history delete <id>` with confirmation

## 5. Logs CLI

- [x] 5.1 Create `logs` command group
- [x] 5.2 Implement `logs list` with filtering options (--level, --source, --from, --to, --limit)
- [x] 5.3 Add `logs export <filename>` functionality

## 6. State Migration

- [x] 6.1 Create migration detection for existing state files
- [x] 6.2 Implement config migration from JSON to database
- [x] 6.3 Add state migration (notification IDs, etc.)
- [x] 6.4 Implement backup of original files before migration
- [x] 6.5 Add migration status tracking to prevent re-running
- [x] 6.6 Implement rollback on migration failure

## 7. Integration and Testing

- [x] 7.1 Integrate persistence layer with DictationService
- [x] 7.2 Update audio recorder to save files instead of delete
- [x] 7.3 Add new dependencies to requirements.txt
- [x] 7.4 Run tests and fix any issues
- [x] 7.5 Verify all CLI commands work correctly
