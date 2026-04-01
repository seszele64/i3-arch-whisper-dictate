## Why

The whisper-dictate CLI application crashes with "RuntimeError: Event loop is closed" errors during dictation workflows. This is caused by a fundamental architectural mismatch: the synchronous CLI code calls async database operations via `asyncio.run()` 39+ times across 7 files, creating new event loops each time while aiosqlite's background worker thread remains bound to the first (now closed) loop. This error is not a band-aid fixable issue — it requires replacing the async database layer with a synchronous one that matches the CLI application's nature.

## What Changes

- **Remove aiosqlite dependency** — Replace async SQLite wrapper with Python's standard library `sqlite3`
- **Rewrite Database class** — Convert all async methods to synchronous equivalents while preserving WAL mode, migration logic, and integrity checks
- **Remove all `asyncio.run()` calls** — Replace 39+ `asyncio.run()` wrappers with direct synchronous calls across dictation.py, cli.py, toggle_dictate.py, cli_helpers.py, db_logging.py, and audio_storage.py
- **Update test suite** — Convert async test fixtures and test cases to synchronous equivalents
- **Remove async infrastructure** — Delete event loop management code, async context managers, and related utilities

## Capabilities

### New Capabilities
- `sync-database-operations`: Synchronous database layer using Python's standard library sqlite3 with WAL mode for crash recovery, connection management, schema migrations, and integrity checks

### Modified Capabilities
- `002-database-persistence`: Implementation changes from async to sync — requirements (data persistence, schema migrations, integrity checks) remain unchanged

## Impact

**Affected Code:**
- `whisper_dictate/database.py` — Full rewrite (async → sync)
- `whisper_dictate/dictation.py` — Remove asyncio.run() wrappers (~7 calls)
- `whisper_dictate/cli.py` — Remove asyncio.run() wrappers (~9 calls)
- `whisper_dictate/toggle_dictate.py` — Remove asyncio.run() wrappers (~15 calls)
- `whisper_dictate/cli_helpers.py` — Remove asyncio.run() wrappers (~3 calls)
- `whisper_dictate/db_logging.py` — Remove asyncio.run() wrappers (~2 calls)
- `whisper_dictate/audio_storage.py` — Remove asyncio.run() wrappers (~3 calls)

**Dependencies:**
- Remove: `aiosqlite`
- No new dependencies (sqlite3 is in Python stdlib)

**Breaking Changes:** None — internal implementation change only, CLI interface unchanged

**Risk:** Low — synchronous sqlite3 is battle-tested; WAL mode preserves crash recovery guarantees

**Estimated Effort:** 5-7 days
