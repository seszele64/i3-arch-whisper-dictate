# ADR 2: Dependency Injection for Services

## Status

Proposed

## Context

`DictationService` currently uses lazy property access to create database and audio storage singletons:

```python
@property
def _database(self):
    if self._db is None:
        self._db = Database(...)
    return self._db
```

This pattern makes tests require `patch()` for dependency replacement:
```python
@patch('DictationService._database', new_callable=property)
def test_something(self, mock_db):
    ...
```

This approach:
- Makes tests harder to write and maintain
- Requires understanding of property patching nuances
- Creates implicit dependencies that aren't visible in the constructor
- Makes it difficult to inject custom implementations for testing edge cases

## Decision

Add optional constructor parameters for `database` and `audio_storage` to enable direct injection during tests while maintaining lazy initialization for production use.

The implementation will:
1. Accept optional `database` and `audio_storage` parameters in `__init__`
2. Store injected instances directly if provided
3. Lazily create instances only when needed and no instance was provided
4. Maintain backward compatibility with existing code

Example:
```python
class DictationService:
    def __init__(self, database=None, audio_storage=None, ...):
        self._database = database
        self._audio_storage = audio_storage
        # ... rest of init
    
    @property
    def _database(self):
        if self._db is None:
            self._db = Database(...)  # Lazy creation for production
        return self._db
```

## Consequences

- **Positive**: Tests become simpler - no patching required, just pass mocks to constructor
- **Positive**: Explicit dependencies - constructor signature shows what's needed
- **Positive**: Better test isolation - each test can have its own instances
- **Positive**: Enables testing with real implementations (not just mocks)
- **Negative**: Larger constructor signature
- **Negative**: Need to handle None vs injected instances carefully

## Related Files

- `src/services/dictation.py` - Main service to modify
- `tests/test_dictation.py` - Tests that will be simplified
