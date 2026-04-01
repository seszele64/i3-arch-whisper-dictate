## 1. Phase 1: Rewrite database.py (Days 1-2)

- [x] 1.1 Replace `import aiosqlite` with `import sqlite3` in database.py
- [x] 1.2 Convert `Database` class: change `async def` methods to `def` (synchronous)
- [x] 1.3 Replace `await cursor.execute()` calls with `cursor.execute()`
- [x] 1.4 Replace `async with` context managers with `with` (synchronous)
- [x] 1.5 Change `_connection` type from `aiosqlite.Connection` to `sqlite3.Connection`
- [x] 1.6 Convert `__aenter__`/`__aexit__` to `__enter__`/`__exit__` (sync context manager)
- [x] 1.7 Update `__init__.py` to export synchronous `Database` class
- [x] 1.8 Verify WAL mode is preserved: execute `PRAGMA journal_mode=WAL`
- [x] 1.9 Verify schema migrations still work with sqlite3
- [x] 1.10 Run `uv run pytest` to verify database tests pass
- [x] 1.11 Run `uv run ruff check whisper_dictate/database.py` for linting

## 2. Phase 2: Update Service Files (Days 2-4)

### 2.1 Update dictation.py (~7 asyncio.run() calls)

- [x] 2.1.1 Remove `asyncio.run()` wrapper from dictation.py database calls
- [x] 2.1.2 Update any async method signatures to synchronous
- [x] 2.1.3 Remove `asyncio` import if no longer needed
- [x] 2.1.4 Run `uv run ruff check whisper_dictate/dictation.py`

### 2.2 Update cli.py (~9 asyncio.run() calls)

- [x] 2.2.1 Remove `asyncio.run()` wrapper from cli.py database calls
- [x] 2.2.2 Update any async method signatures to synchronous
- [x] 2.2.3 Remove `asyncio` import if no longer needed
- [x] 2.2.4 Run `uv run ruff check whisper_dictate/cli.py`

### 2.3 Update toggle_dictate.py (~15 asyncio.run() calls)

- [x] 2.3.1 Remove `asyncio.run()` wrapper from toggle_dictate.py database calls
- [x] 2.3.2 Update any async method signatures to synchronous
- [x] 2.3.3 Remove `asyncio` import if no longer needed
- [x] 2.3.4 Run `uv run ruff check whisper_dictate/toggle_dictate.py`

### 2.4 Update cli_helpers.py

- [x] 2.4.1 Remove `with_database` decorator entirely (no longer needed with sync DB)
- [x] 2.4.2 Update all callers to use `get_database()` directly instead of the decorator
- [x] 2.4.3 Run `uv run ruff check whisper_dictate/cli_helpers.py`

### 2.5 Update db_logging.py

- [x] 2.5.1 Remove `asyncio.run()` wrapper from db_logging.py database calls
- [x] 2.5.2 Update any async method signatures to synchronous
- [x] 2.5.3 Remove `asyncio` import if no longer needed
- [x] 2.5.4 Run `uv run ruff check whisper_dictate/db_logging.py`

### 2.6 Update audio_storage.py

- [x] 2.6.1 Remove `asyncio.run()` wrapper from audio_storage.py database calls
- [x] 2.6.2 Update any async method signatures to synchronous
- [x] 2.6.3 Remove `asyncio` import if no longer needed
- [x] 2.6.4 Run `uv run ruff check whisper_dictate/audio_storage.py`

### 2.7 Integration verification

- [x] 2.7.1 Run full application smoke test (start CLI, verify no "Event loop is closed" error)
- [x] 2.7.2 Run `uv run ruff check whisper_dictate/` on entire package

## 3. Phase 3: Update Tests (Days 4-5)

- [ ] 3.1 Convert async pytest fixtures to synchronous fixtures in test files
- [ ] 3.2 Remove `pytest.mark.asyncio` decorators from test functions
- [ ] 3.3 Remove `pytest.mark.asyncio` import if present
- [ ] 3.4 Update test assertions as needed for synchronous operations
- [ ] 3.5 Remove any `async def test_` functions that are now sync
- [ ] 3.6 Run `uv run pytest` to verify all tests pass
- [ ] 3.7 Run `uv run ruff check tests/` for linting

## 4. Phase 4: Remove aiosqlite Dependency (Day 5)

- [ ] 4.1 Remove `aiosqlite` from `pyproject.toml` dependencies
- [ ] 4.2 Remove `aiosqlite` from any `requirements.txt` or lock files
- [ ] 4.3 Clean up any remaining `async`-related imports across the codebase
- [ ] 4.4 Search for any remaining `asyncio.run()` calls and remove
- [ ] 4.5 Run `uv run ruff check .` on entire project
- [ ] 4.6 Run `uv run pytest` for final verification
- [ ] 4.7 Verify no "Event loop is closed" errors occur during full application workflow

## 5. Verification & Rollback Preparation

- [ ] 5.1 Commit changes to git branch with descriptive message
- [ ] 5.2 Run end-to-end CLI workflow test (record, transcribe, view history)
- [ ] 5.3 Verify WAL mode is functioning correctly on existing database
- [ ] 5.4 Document rollback steps (revert to aiosqlite implementation if needed)
