## 1. Database Infrastructure

- [ ] 1.1 Create database module with aiosqlite integration
- [ ] 1.2 Implement database schema (recordings, transcripts, logs, state, schema_versions tables)
- [ ] 1.3 Add database initialization logic with version tracking
- [ ] 1.4 Implement schema migration system
- [ ] 1.5 Add database integrity check on startup

## 2. Audio Storage

- [ ] 2.1 Create audio storage directory management module
- [ ] 2.2 Implement date-based directory structure creation
- [ ] 2.3 Add audio file save functionality after transcription
- [ ] 2.4 Implement unique filename generation with timestamp
- [ ] 2.5 Add audio file retrieval by recording ID
- [ ] 2.6 Implement audio file cleanup on transcript deletion

## 3. Database Logging

- [ ] 3.1 Create database-backed logging handler
- [ ] 3.2 Integrate dual logging (file + database)
- [ ] 3.3 Implement log query functionality
- [ ] 3.4 Add log filtering (by level, source, date range)
- [ ] 3.5 Implement log retention cleanup

## 4. Transcription History CLI

- [ ] 4.1 Create `history` command group
- [ ] 4.2 Implement `history list` with pagination
- [ ] 4.3 Implement `history show <id>` for full details
- [ ] 4.4 Add `history search <query>` functionality
- [ ] 4.5 Implement `history delete <id>` with confirmation

## 5. Logs CLI

- [ ] 5.1 Create `logs` command group
- [ ] 5.2 Implement `logs list` with filtering options (--level, --source, --from, --to, --limit)
- [ ] 5.3 Add `logs export <filename>` functionality

## 6. State Migration

- [ ] 6.1 Create migration detection for existing state files
- [ ] 6.2 Implement config migration from JSON to database
- [ ] 6.3 Add state migration (notification IDs, etc.)
- [ ] 6.4 Implement backup of original files before migration
- [ ] 6.5 Add migration status tracking to prevent re-running
- [ ] 6.6 Implement rollback on migration failure

## 7. Integration and Testing

- [ ] 7.1 Integrate persistence layer with DictationService
- [ ] 7.2 Update audio recorder to save files instead of delete
- [ ] 7.3 Add new dependencies to requirements.txt
- [ ] 7.4 Run tests and fix any issues
- [ ] 7.5 Verify all CLI commands work correctly
