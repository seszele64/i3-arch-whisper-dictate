# Rollback Guide: sync-sqlite3-migration

This document describes how to revert from the sqlite3 synchronous implementation back to the aiosqlite asynchronous implementation if needed.

---

## 1. When to Rollback

Consider rolling back if you encounter any of the following scenarios:

- **Data Corruption**: Unexpected database errors, missing records, or integrity violations that cannot be resolved
- **Performance Issues**: Significant throughput degradation or responsiveness problems under load
- **Unexpected Errors**: Recurring connection errors, lock timeouts, or unexplained crashes
- **Event Loop Issues**: If the original "Event loop is closed" errors return and cannot be fixed through other means
- **Concurrency Requirements**: Future features require true async database operations that cannot be met with sync sqlite3
- **Compatibility Issues**: Integration problems with other async systems that cannot be resolved

---

## 2. Quick Rollback (Git Revert)

### Option A: Switch to Main Branch

If the migration branch (`fix/aiosqlite-event-loop-closed`) has not been merged and main still has the aiosqlite implementation:

```bash
git checkout main
```

### Option B: Revert Specific Commits

If changes have been committed but need to be preserved in history:

```bash
# List recent commits to find the migration commit
git log --oneline

# Revert the migration commit(s)
git revert <commit-hash>
```

### Option C: Reset to Previous State

**Warning**: Only use if changes have not been pushed to a shared remote.

```bash
# Soft reset (preserves staged changes)
git reset --soft HEAD~<number-of-commits>

# Hard reset (destroys all changes - use with caution!)
git reset --hard HEAD~<number-of-commits>
```

---

## 3. Manual Rollback Steps

If git operations are not possible, manually restore the following:

### 3.1 Restore Dependencies in `pyproject.toml`

Add back the async dependencies:

```toml
[dependencies]
# Add back
aiosqlite = "^0.20.0"

[project.optional-dependencies]
dev = [
    # Add back
    "pytest-asyncio>=0.21.0",
]
```

### 3.2 Restore `whisper_dictate/database.py`

Restore the async patterns:

```python
import aiosqlite
import asyncio
from contextlib import asynccontextmanager

# Restore async context manager
@asynccontextmanager
async def get_database():
    async with aiosqlite.connect(DB_PATH) as db:
        # ... async initialization
        yield db

# Restore async functions
async def get_all_dictations():
    async with get_database() as db:
        # ... restore async queries

async def save_dictation(...):
    async with get_database() as db:
        # ... restore async inserts

async def delete_dictation(...):
    async with get_database() as db:
        # ... restore async deletes
```

### 3.3 Restore `whisper_dictate/dictation.py`

Add back `asyncio.run()` wrappers:

```python
import asyncio

# Wrap async calls
asyncio.run(self.transcriber.save_transcription(...))
asyncio.run(self._log_event("transcription_completed", ...))
```

### 3.4 Restore `whisper_dictate/cli.py`

Add back `asyncio.run()` wrappers for database operations:

```python
asyncio.run(show_history())
asyncio.run(export_dictations(...))
```

### 3.5 Restore `whisper_dictate/toggle_dictate.py`

Add back `asyncio.run()` wrappers:

```python
asyncio.run(self._stop_recording())
asyncio.run(self._cleanup_database())
```

### 3.6 Restore `whisper_dictate/cli_helpers.py`

Restore the `with_database` decorator:

```python
import asyncio
from functools import wraps

def with_database(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper

# Usage
@with_database
async def show_history():
    async with get_database() as db:
        # ...
```

### 3.7 Restore `whisper_dictate/db_logging.py`

Add back `asyncio.run()` wrappers:

```python
asyncio.run(log_event(...))
```

### 3.8 Restore `whisper_dictate/audio_storage.py`

Add back `asyncio.run()` wrappers:

```python
asyncio.run(log_to_database(...))
```

### 3.9 Restore Test Files

Restore async test fixtures and decorators:

```python
import pytest
import pytest_asyncio
from whisper_dictate.database import get_database

# Restore async fixture
@pytest_asyncio.fixture
async def test_db():
    async with get_database() as db:
        yield db

# Restore async test marker
@pytest.mark.asyncio
async def test_something(test_db):
    # ...
```

### 3.10 Restore `pytest-asyncio` in Test Configuration

In `pyproject.toml` or `pytest.ini`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

---

## 4. Data Safety Notes

### WAL Mode Protection

The migration uses SQLite's WAL (Write-Ahead Logging) mode, which:
- Ensures no data corruption during concurrent access
- Allows simultaneous reads during writes
- Provides automatic crash recovery

### Database File Compatibility

Both sqlite3 and aiosqlite use the identical SQLite database format:
- **No schema changes** were made during migration
- **No data conversion** is required
- **No migration scripts** are needed

### Existing Data

All existing data is fully compatible with both implementations:
- Records created with aiosqlite will read correctly with sqlite3
- Records created with sqlite3 will read correctly with aiosqlite
- No data export or import is required for rollback

---

## 5. Files Modified During Migration

### Primary Changes

| File | Changes Made |
|------|--------------|
| `whisper_dictate/database.py` | Full rewrite from async to sync patterns |
| `pyproject.toml` | Removed aiosqlite and pytest-asyncio dependencies |

### Consumer File Updates

| File | Changes Made |
|------|--------------|
| `whisper_dictate/dictation.py` | Removed asyncio.run() wrappers |
| `whisper_dictate/cli.py` | Removed asyncio.run() wrappers |
| `whisper_dictate/toggle_dictate.py` | Removed asyncio.run() wrappers |
| `whisper_dictate/cli_helpers.py` | Removed with_database decorator |
| `whisper_dictate/db_logging.py` | Removed asyncio.run() wrappers |
| `whisper_dictate/audio_storage.py` | Removed asyncio.run() wrappers |

### Test File Updates

All test files in `tests/` were converted from:
- `async def` to `def`
- `await` to direct calls
- `pytest.mark.asyncio` decorators removed
- Async fixtures converted to sync fixtures

---

## 6. Verification After Rollback

After completing the rollback, verify the restoration:

### Run Tests

```bash
uv run pytest
```

Expected: All tests pass with the async implementation

### Verify CLI Functionality

```bash
uv run whisper-dictate history list
```

Expected: Command completes successfully, showing dictation history

### Check for Original Issue

```bash
# Run the application and check logs
uv run whisper-dictate

# Look for "Event loop is closed" errors
```

Expected: No event loop errors should appear

### Verify Async Behavior

```python
# Quick sanity check in Python
import asyncio
import aiosqlite

async def test():
    async with aiosqlite.connect("test.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")
        await db.commit()

asyncio.run(test())
```

Expected: No errors during async database operations

---

## 7. Contact & Support

If rollback is needed due to a bug in the migration:
1. Document the specific error encountered
2. Collect relevant logs and stack traces
3. File an issue with the rollback steps used
4. The migration can be re-attempted after fixing identified issues

---

*Last updated: 2026-04-02*
