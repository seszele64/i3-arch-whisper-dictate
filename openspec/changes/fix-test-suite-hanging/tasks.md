# Tasks: fix-test-suite-hanging

## 1. Configuration Setup

- [x] 1.1 Create pyproject.toml with asyncio_mode=strict, asyncio_default_fixture_loop_scope=function, and timeout=30
  - **File**: `pyproject.toml` (new file)
  - **Reference**: Design.md lines 95-100 (Decision 3, 4)
  - **Verification**: Run `pytest --collect-only` to confirm strict mode is active

## 2. conftest.py Modifications

- [x] 2.1 Remove cleanup_sounddevice session-scoped autouse fixture
  - **File**: `conftest.py`
  - **Lines**: 254-269
  - **Reference**: Design.md lines 50, 240-246 (Decision 1)
  - **Verification**: `grep -n "cleanup_sounddevice" conftest.py` returns no fixture definition

- [x] 2.2 Remove cleanup_aiosqlite session-scoped autouse fixture
  - **File**: `conftest.py`
  - **Lines**: 272-333
  - **Reference**: Design.md lines 50, 240-246 (Decision 1)
  - **Verification**: `grep -n "cleanup_aiosqlite" conftest.py` returns no fixture definition

- [x] 2.3 Enhance reset_persistent_notification_state to clear _recording_notification
  - **File**: `conftest.py`
  - **Reference**: Design.md lines 161-168, 243 (Decision 6)
  - **Verification**: Fixture saves/restores `notifications_module.PersistentNotification._recording_notification`

- [x] 2.4 Add async_cleanup function-scoped fixture for async resource cleanup
  - **File**: `conftest.py`
  - **Reference**: Design.md lines 178-196, 244 (Decision 7)
  - **Verification**: `async_cleanup` fixture available; uses `request.addfinalizer()` pattern

## 3. test_database_update.py Conversions

- [x] 3.1 Add @pytest.mark.asyncio decorator to all async test methods in TestUpdateTranscript
  - **File**: `tests/test_database_update.py`
  - **Reference**: Design.md lines 70-80, 259-262 (Decision 2)
  - **Verification**: All async test methods have `@pytest.mark.asyncio` decorator

- [x] 3.2 Replace asyncio.run(...) calls with await expressions
  - **File**: `tests/test_database_update.py`
  - **Reference**: Design.md lines 71-80 (Decision 2)
  - **Verification**: No `asyncio.run()` calls remain in the file

- [x] 3.3 Change test method definitions from `def` to `async def`
  - **File**: `tests/test_database_update.py`
  - **Reference**: Design.md lines 71-80 (Decision 2)
  - **Verification**: All async test methods are defined as `async def`

## 4. test_audio_converter.py Mock Fix

- [x] 4.1 Replace direct sys.modules manipulation with patch.dict() in mock_pydub_in_sys_modules
  - **File**: `tests/test_audio_converter.py`
  - **Reference**: Design.md lines 129-151, 264-265 (Decision 5)
  - **Verification**: Fixture uses `with patch.dict(sys.modules, {"pydub": mock_module}):` pattern

## 5. Verification

- [ ] 5.1 Run individual test files to confirm they pass
  - **Command**: `pytest tests/test_database_update.py -v && pytest tests/test_audio_converter.py -v`
  - **Reference**: Acceptance Criteria #1, #2 (spec.md lines 74-75)
  - **Verification**: All tests in both files pass

- [ ] 5.2 Run full test suite to confirm no hanging
  - **Command**: `pytest --timeout=30`
  - **Reference**: Acceptance Criteria #1 (spec.md line 74)
  - **Verification**: Suite completes without hanging, all tests finish within timeout

- [ ] 5.3 Verify pytest-asyncio strict mode is enforced
  - **Command**: `pytest --collect-only`
  - **Reference**: Acceptance Criteria #3, #6 (spec.md lines 76, 79)
  - **Verification**: Tests without `@pytest.mark.asyncio` are not collected as async tests

- [ ] 5.4 Confirm session-scoped autouse fixtures are removed
  - **Command**: `grep -E "(cleanup_sounddevice|cleanup_aiosqlite).*autouse" conftest.py`
  - **Reference**: Acceptance Criteria #4 (spec.md line 77)
  - **Verification**: No results returned

- [ ] 5.5 Confirm pytest-timeout is configured with 30s default
  - **Command**: `grep -E "^timeout\s*=" pytest.ini`
  - **Reference**: Acceptance Criteria #7 (spec.md line 80)
  - **Verification**: `timeout = 30` is present in pytest.ini

- [ ] 5.6 Confirm patch.dict() is used in test_audio_converter.py
  - **Command**: `grep -n "patch.dict" tests/test_audio_converter.py`
  - **Reference**: Acceptance Criteria #8 (spec.md line 81)
  - **Verification**: `patch.dict` is found in mock_pydub_in_sys_modules fixture

- [ ] 5.7 Confirm global state fixture includes _recording_notification
  - **Command**: `grep -A5 "reset_persistent_notification_state" conftest.py | grep "_recording_notification"`
  - **Reference**: Acceptance Criteria #9 (spec.md line 82)
  - **Verification**: `_recording_notification` is saved and restored in the fixture
