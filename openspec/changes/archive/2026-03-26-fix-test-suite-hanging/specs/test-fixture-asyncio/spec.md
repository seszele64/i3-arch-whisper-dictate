## ADDED Requirements

### Requirement: pytest-asyncio strict mode configuration
The system SHALL configure pytest-asyncio in strict mode with function-scoped event loop scope to prevent event loop conflicts during test execution.

#### Scenario: pytest-asyncio operates in strict mode
- **WHEN** pytest-asyncio plugin is loaded
- **THEN** it SHALL operate in strict mode requiring explicit async markers on all async tests
- **AND** event loops SHALL be function-scoped, creating a new loop for each test function

#### Scenario: Async tests without explicit markers fail in strict mode
- **WHEN** an async test function lacks `@pytest.mark.asyncio` marker
- **THEN** the test SHALL fail with an error indicating strict mode requires explicit markers
- **AND** the test suite SHALL NOT hang due to implicit event loop handling

### Requirement: Session-scoped autouse fixtures removed
The system SHALL remove session-scoped autouse fixtures (`cleanup_sounddevice`, `cleanup_aiosqlite`) from conftest.py that attempt to manage event loops after tests complete, as these fixtures cause hanging when combined with pytest-asyncio event loop handling.

#### Scenario: Conflicting fixtures removed from conftest.py
- **WHEN** conftest.py is loaded
- **THEN** it SHALL NOT contain session-scoped autouse fixtures that call `loop.run_until_complete()` or `asyncio.run()` after test completion
- **AND** existing tests that rely on cleanup SHALL use function-scoped fixtures instead

### Requirement: Function-scoped async cleanup fixture
The system SHALL provide a function-scoped async cleanup fixture that replaces the removed session-scoped cleanup fixtures, ensuring proper resource cleanup within each test's event loop scope.

#### Scenario: Function-scoped cleanup replaces session-scoped cleanup
- **WHEN** a test requires async resource cleanup
- **THEN** a function-scoped fixture with proper async cleanup SHALL be available
- **AND** the fixture SHALL use `request.addfinalizer()` or `request链` for cleanup within the same event loop

### Requirement: asyncio.run() calls converted to pytest-asyncio patterns
The system SHALL convert direct `asyncio.run()` calls in test files to use `@pytest.mark.asyncio` decorated test functions with `async`/`await` patterns.

#### Scenario: test_database_update.py uses pytest-asyncio markers
- **WHEN** test_database_update.py is executed
- **THEN** all async tests SHALL use `@pytest.mark.asyncio` decorator
- **AND** tests SHALL NOT call `asyncio.run()` directly
- **AND** tests SHALL use `await` for async operations within the test function

### Requirement: pytest-timeout configuration
The system SHALL configure pytest-timeout with a 30-second default timeout to prevent hanging tests from blocking the full test suite.

#### Scenario: Default timeout prevents hanging tests
- **WHEN** a test takes longer than 30 seconds to complete
- **THEN** pytest SHALL terminate the test with a timeout error
- **AND** the test suite SHALL continue executing remaining tests

#### Scenario: Slow tests have tiered timeout overrides
- **WHEN** specific tests require longer execution time
- **THEN** those tests MAY use `@pytest.mark.timeout(seconds)` to override the default
- **AND** the override SHALL be set to an appropriate value for the specific test

### Requirement: Module mocking uses patch.dict()
The system SHALL fix module mocking in test_audio_converter.py to use `patch.dict()` instead of direct module replacement, preventing event loop conflicts during mock operations.

#### Scenario: test_audio_converter.py uses patch.dict for module mocks
- **WHEN** test_audio_converter.py mocks module-level objects
- **THEN** it SHALL use `patch.dict()` to modify module dictionaries
- **AND** the mock SHALL NOT replace the entire module or interfere with event loop state

### Requirement: Global state reset includes _recording_notification
The system SHALL enhance the global state reset fixture to include `_recording_notification` in addition to existing state variables, ensuring complete state isolation between tests.

#### Scenario: Global state fixture resets all test state
- **WHEN** a test requires clean global state
- **THEN** the reset fixture SHALL clear `_recording_notification` along with other global state
- **AND** the fixture SHALL be function-scoped to ensure isolation

## Acceptance Criteria

| # | Criterion | Verification |
|---|-----------|--------------|
| 1 | Full test suite completes without hanging | Run `pytest` on entire test suite and confirm all tests complete |
| 2 | Individual test files pass independently | Run each test file separately and verify all pass |
| 3 | pytest-asyncio strict mode is enforced | Tests without `@pytest.mark.asyncio` fail with proper error |
| 4 | Session-scoped autouse fixtures are removed | conftest.py does not contain `cleanup_sounddevice` or `cleanup_aiosqlite` as autouse fixtures |
| 5 | Function-scoped cleanup fixture is available | Tests requiring async cleanup can use a function-scoped fixture |
| 6 | asyncio.run() is not used in test files | No `asyncio.run()` calls remain in test_database_update.py |
| 7 | pytest-timeout is configured with 30s default | pytest.ini or pyproject.toml contains timeout configuration |
| 8 | test_audio_converter.py uses patch.dict() | Mock operations use `patch.dict()` instead of module replacement |
| 9 | Global state fixture includes _recording_notification | Reset fixture clears `_recording_notification` between tests |
| 10 | No event loop conflicts during test execution | Tests run with function-scoped event loops without conflicts |
