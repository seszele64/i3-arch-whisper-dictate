## Context

The `PersistentNotification` class in `whisper_dictate/notifications.py` provides persistent desktop notifications using dunstify. The `open()` method correctly checks if dunstify is available before attempting to send a notification (line 406), but the `close()` method (lines 555-575) lacks this check.

This inconsistency causes the following issue:
1. User starts recording → `open()` is called → notification sent via dunstify
2. For some reason dunstify becomes unavailable (uninstalled, path change, etc.)
3. User stops recording → `close()` is called → tries to run `dunstify -C` → fails because dunstify binary doesn't exist

## Goals / Non-Goals

**Goals:**
- Add `is_dunstify_available()` check to the `close()` method before attempting to close
- Maintain consistent behavior with the `open()` method
- Log appropriate warning when dunstify is unavailable during close
- Ensure no errors are thrown when dunstify is not available

**Non-Goals:**
- Add new functionality or capabilities
- Modify the notification display or behavior
- Change the fallback behavior (notify-send) - this is already handled in `open()`

## Decisions

1. **Check dunstify availability in close() before subprocess call**
   - Rationale: Consistent with `open()` method pattern (line 406)
   - Alternative considered: Check availability at the start of close() and return early if not available, similar to how open() handles it

2. **Return True (success) when dunstify is unavailable**
   - Rationale: If dunstify isn't available, there's nothing to close. The notification likely never appeared or was already closed by other means. Returning True prevents unnecessary error handling upstream.
   - Alternative: Return False to indicate failure - rejected because it would cause unnecessary error propagation for a non-critical operation

3. **Log a warning when dunstify is unavailable during close**
   - Rationale: Provides visibility into the state for debugging without being overly noisy

4. **Update notify_recording_persistent_stop() to log warning when no notification ID found**
   - Rationale: Currently returns True silently when saved ID is empty/corrupted, making failures invisible. Logging a warning provides debugging visibility.
   - This function calls PersistentNotification.close() internally, so the dunstify check fix will apply, but the ID validation still needs explicit warning

## Risks / Trade-offs

- **Risk**: If dunstify becomes unavailable between open() and close(), the notification may remain visible on screen
  - **Mitigation**: This is an edge case. The notification would have been created with dunstify originally, so it should be closeable with dunstify. If dunstify is removed mid-session, the user would need to manually close the notification.

- **Risk**: None significant - this is a simple, localized fix with clear precedent from the existing `open()` method

- **Risk**: notify_recording_persistent_stop() returns True even when no notification was actually closed
  - **Mitigation**: Added explicit warning log so the issue is visible for debugging
