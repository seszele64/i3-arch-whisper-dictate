## Why

The persistent "recording started" notification fails to close properly when dunstify becomes unavailable after the notification was opened. The `close()` method in `PersistentNotification` attempts to run `dunstify -C` without first checking if dunstify is available on the system, causing the close operation to fail silently or throw errors.

## What Changes

- Add `is_dunstify_available()` check to the `close()` method in `PersistentNotification` class (lines 555-575 of `whisper_dictate/notifications.py`)
- Return True with warning log if dunstify is not available when attempting to close (consistent with open() method behavior)
- Ensure consistent behavior with the `open()` method which already has this check
- Update notify_recording_persistent_stop() (lines 675-676) to log warning when no notification ID is found instead of returning True silently

## Capabilities

### New Capabilities
- None (this is a bug fix, not a new capability)

### Modified Capabilities
- `001-persistent-notification`: Fix the close() method to check dunstify availability before attempting to close

## Impact

- **File**: `whisper_dictate/notifications.py`
- **Class**: `PersistentNotification`
- **Method**: `close()` (lines 555-575)
- **Related**: Module-level `close_recording_notification()` function (lines 670-676)
- **Testing**: May need to verify existing tests pass or add edge case tests for dunstify unavailability during close
