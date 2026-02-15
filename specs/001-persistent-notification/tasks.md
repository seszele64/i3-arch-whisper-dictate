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
- [ ] Check if shutil.which works for dunstify detection
- [ ] File: whisper_dictate/notifications.py
- [ ] Status: pending

### T2: Add dunstify fallback to notify-send
- [ ] Implement is_dunstify_available() helper
- [ ] Implement send_dunstify() with fallback
- [ ] File: whisper_dictate/notifications.py
- [ ] Status: pending

---

## Phase 2: Core Notification System

### T3: Create PersistentNotification class
- [ ] Implement constructor with notification_id tracking
- [ ] Implement send_persistent() method
- [ ] Implement update() method using stack tags
- [ ] Implement close() method
- [ ] File: whisper_dictate/notifications.py
- [ ] Status: pending

### T4: Add helper functions for recording notifications
- [ ] notify_recording_persistent_start()
- [ ] notify_recording_persistent_update()
- [ ] notify_recording_persistent_stop()
- [ ] File: whisper_dictate/notifications.py
- [ ] Status: pending

### T5: Add error handling and logging
- [ ] Log warnings when dunstify unavailable
- [ ] Log notification failures
- [ ] File: whisper_dictate/notifications.py
- [ ] Status: pending

### T5b: Add notification action button for stopping recording (FR-005)
- [ ] Add stop action to notification using -A "stop,Stop Recording" flag
- [ ] Handle action callback to stop recording
- [ ] Document that action requires dunst context menu (Ctrl+Shift+.)
- [ ] File: whisper_dictate/notifications.py
- [ ] Status: pending

---

## Phase 3: Integration

### T6: Integrate with toggle_dictate.py
- [ ] Import new notification functions
- [ ] Replace notify_recording_started with persistent version
- [ ] Add close on stop
- [ ] File: toggle_dictate.py
- [ ] Status: pending

### T7: Test notification lifecycle
- [ ] Start recording -> notification appears
- [ ] Stop recording -> notification closes
- [ ] Status: pending

### T8: Handle edge cases
- [ ] Multiple rapid start/stop
- [ ] Notification daemon crash during recording
- [ ] Status: pending

---

## Phase 4: Testing

### T9: Add unit tests for PersistentNotification
- [ ] Test send_persistent()
- [ ] Test update()
- [ ] Test close()
- [ ] Test fallback behavior
- [ ] File: tests/test_notifications.py
- [ ] Status: pending

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
