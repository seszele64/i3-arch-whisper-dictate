# ADR 1: Mock Factory Pattern for Async Resources

## Status

Proposed

## Context

Tests frequently need to mock async database and storage interfaces. Manual mock configuration is error-prone and leads to incomplete mocks, causing test failures. Each test that needs a mock database or storage object must manually set up the async methods, return values, and side effects, which creates:
- Inconsistent mock behavior across tests
- Duplicated setup code
- High maintenance burden when interfaces change
- Test fragility where changes to the interface break multiple tests

## Decision

Create `create_mock_database()` and `create_mock_audio_storage()` factory functions in `tests/helpers.py`.

These factory functions will:
1. Return pre-configured mock objects with all required async methods
2. Provide sensible default return values for common operations
3. Support customization via parameters for test-specific behavior
4. Ensure all mocks implement the same interface as the real implementations

## Consequences

- **Positive**: Centralized mock configuration - all mock setup logic is in one place
- **Positive**: Single source of truth for default mock behavior
- **Positive**: Easy to update all tests when interface changes (only one place to modify)
- **Positive**: Reduces code duplication across test files
- **Negative**: Additional test infrastructure to maintain
- **Negative**: Requires coordination between interface changes and mock updates

## Related Files

- `tests/helpers.py` - New file to contain factory functions
- `tests/conftest.py` - May use these factories in shared fixtures
