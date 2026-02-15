# Implementation Tasks: Persistent Notification Feature

**Feature**: Persistent Notification During Recording  
**Date**: 2026-02-15

## Task Overview

| Phase | Tasks | Description |
|-------|-------|-------------|
| Setup | T1-T2 | Project setup and dependencies |
| Core | T3-T5b | Implement notification system |
| Integration | T6-T8 | Connect with recording flow |
| Testing | T9-T11 | Add tests and verify |

---

## Phase 1: Setup

### T1: Verify dunstify availability check
- [x] Check if shutil.which works for dunstify detection
- [x] File: whisper_dictate/notifications.py
- [x] Status: complete

### T2: Add dunstify fallback to notify-send
- [x] Implement is_dunstify_available() helper
- [x] Implement send_dunstify() with fallback
- [x] File: whisper_dictate/notifications.py
- [x] Status: complete

---

## Phase 2: Core Notification System

### T3: Create PersistentNotification class
- [x] Implement constructor with notification_id tracking
- [x] Implement send_persistent() method
- [x] Implement update() method using stack tags
- [x] Implement close() method
- [x] File: whisper_dictate/notifications.py
- [x] Status: complete

### T4: Add helper functions for recording notifications
- [x] notify_recording_persistent_start()
- [x] notify_recording_persistent_update()
- [x] notify_recording_persistent_stop()
- [x] File: whisper_dictate/notifications.py
- [x] Status: complete

### T5: Add error handling and logging
- [x] Log warnings when dunstify unavailable
- [x] Log notification failures
- [x] File: whisper_dictate/notifications.py
- [x] Status: complete

### T5b: Add notification action button for stopping recording (FR-005)
- [ ] Add stop action to notification using -A "stop,Stop Recording" flag
- [ ] Handle action callback to stop recording
- [ ] Document that action requires dunst context menu (Ctrl+Shift+.)
- [ ] File: whisper_dictate/notifications.py
- [ ] Status: pending

---

## Phase 3: Integration

### T6: Integrate with toggle_dictate.py
- [x] Import new notification functions
- [x] Replace notify_recording_started with persistent version
- [x] Add close on stop
- [x] File: toggle_dictate.py
- [x] Status: complete

### T7: Test notification lifecycle
- [x] Start recording -> notification appears
- [x] Stop recording -> notification closes
- [x] Status: complete

### T8: Handle edge cases
- [x] Multiple rapid start/stop
- [x] Notification daemon crash during recording
- [x] Status: complete

---

## Phase 4: Testing

### T9: Add unit tests for PersistentNotification
- [x] Test send_persistent()
- [x] Test update()
- [x] Test close()
- [x] Test fallback behavior
- [x] File: tests/test_notifications.py
- [x] Status: complete

### T10: Run existing tests
- [ ] pytest tests/
- [ ] Verify no regressions
- [ ] Status: pending

### T11: Manual testing
- [ ] Test with actual recording
- [ ] Verify notification persistence
- [ ] Status: pending

---

## Dependencies

- T1 must complete before T2
- T2 must complete before T3
- T3-T5 must complete before T5b
- T5b must complete before T6
- T6-T8 must complete before T9

---

## Notes

- Using stack tags for notification updates (simpler than ID tracking)
- Fallback to notify-send ensures reliability
- All tests must pass before marking phase complete
