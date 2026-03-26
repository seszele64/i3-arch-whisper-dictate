## Why

The test suite hangs indefinitely when run as a full suite, even though individual test files pass successfully. This blocks CI/CD pipelines and makes iterative development painful. The root cause is conflicting event loop management between session-scoped autouse fixtures in conftest.py and pytest-asyncio's event loop handling, combined with tests using `asyncio.run()` directly instead of pytest-asyncio markers.

## What Changes

- **Remove** conflicting session-scoped autouse fixtures (`cleanup_sounddevice`, `cleanup_aiosqlite`) from conftest.py that try to manage event loops after tests complete
- **Convert** `asyncio.run()` calls in test_database_update.py to use `@pytest.mark.asyncio` with proper async test patterns
- **Add** pytest-timeout configuration with 30s default timeout and tiered overrides for slow tests
- **Configure** pytest-asyncio in strict mode with function-scoped loop scope
- **Fix** module mocking in test_audio_converter.py to use `patch.dict()` instead of direct module replacement
- **Enhance** global state reset fixture to include `_recording_notification`
- **Add** function-scoped async cleanup fixture as replacement for removed session-scoped fixtures

## Capabilities

### New Capabilities
- `test-fixture-asyncio`: Test infrastructure configuration for proper asyncio event loop management in pytest, including strict mode, function-scoped loops, and timeout handling

### Modified Capabilities
<!-- No requirement-level changes to existing capabilities -->

## Impact

- **Test infrastructure**: conftest.py (fixture restructuring), pytest configuration (pyproject.toml or pytest.ini)
- **Test files**: test_database_update.py, test_audio_converter.py
- **Dependencies**: Adds pytest-asyncio (strict mode) and pytest-timeout
- **No API or production code changes**
