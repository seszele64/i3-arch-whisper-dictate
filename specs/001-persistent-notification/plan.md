# Implementation Plan: Persistent Notification During Recording

**Branch**: `001-persistent-notification` | **Date**: 2026-02-15 | **Spec**: specs/001-persistent-notification/spec.md
**Input**: Feature specification from `/specs/001-persistent-notification/spec.md`

## Summary

Implement persistent notifications for the whisper-dictate recording feature using dunstify. The notification will remain visible during the entire recording session, display live transcription updates, and provide a stop action button. Falls back gracefully to notify-send if dunst is unavailable.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: dunstify (notifications), dunst (daemon), subprocess (for CLI)  
**Storage**: N/A - stateless notification display  
**Testing**: pytest (existing test suite)  
**Target Platform**: Linux (Arch Linux with i3 window manager)  
**Project Type**: Single CLI tool  
**Performance Goals**: <1 second notification display latency (Constitution: Latency First)  
**Constraints**: Must handle dunst daemon unavailability gracefully  
**Scale/Scope**: Single-user desktop application

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| Latency First (<1 second) | ✅ PASS | Notification appears immediately via dunstify |
| Reliability (graceful errors) | ✅ PASS | Falls back to notify-send if dunst unavailable |
| Privacy & Security | ✅ PASS | No audio data persisted in notifications |
| Configuration Over Hardcoding | ✅ PASS | Uses existing config system |
| Clean, Testable Code | ✅ PASS | Adding unit tests for new functionality |

## Project Structure

### Documentation (this feature)

```
specs/001-persistent-notification/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API contracts)
└── tasks.md             # Phase 2 output (implementation tasks)
```

### Source Code (repository root)

```
whisper_dictate/
├── notifications.py     # [MODIFY] Add persistent notification class
├── dunst_monitor.py     # [EXISTING] Already handles dunst availability
├── audio.py             # [EXISTING] Audio recording
├── transcription.py     # [EXISTING] Transcription service
├── config.py            # [EXISTING] Configuration
└── __init__.py         # [MODIFY] Export new classes

toggle_dictate.py        # [MODIFY] Use persistent notifications

tests/
├── test_notifications.py # [MODIFY] Add persistent notification tests
└── [existing tests]      # [KEEP] Existing test coverage
```

**Structure Decision**: Single Python project - existing structure is adequate. No new directories needed.

## Technical Approach

### Core Implementation

1. **PersistentNotification class** in `notifications.py`:
   - Uses dunstify with `-t 0` for indefinite timeout
   - Uses `-u critical` for high visibility
   - Uses `-p` to get notification ID for updates
   - Uses `-r <id>` to update notification body
   - Uses `-C <id>` to close notification

2. **Recording notification integration**:
   - Show persistent notification when recording starts
   - Update notification body with transcription text
   - Close notification when recording stops

3. **Fallback handling**:
   - Check if dunstify available (shutil.which)
   - Fall back to notify-send if unavailable
   - Log warnings for debugging

### Key Changes

| File | Change |
|------|--------|
| `whisper_dictate/notifications.py` | Add `PersistentNotification` class |
| `toggle_dictate.py` | Use persistent notifications during recording |
| `tests/test_notifications.py` | Add tests for persistent notifications |

## Complexity Tracking

| Complexity | Why Needed | Simpler Alternative |
|------------|-----------|---------------------|
| Notification ID tracking | Required for updating notification body | Cannot update without ID |
| Dunstify vs notify-send | dunstify required for persistent + updates | notify-send lacks these features |

No violations - all complexity is justified by feature requirements.

---

## Phase 0: Research Summary

Based on prior research, the following technical decisions were made:

| Decision | Rationale |
|----------|-----------|
| Use dunstify with `-t 0` | Ensures notification stays visible indefinitely |
| Use `-u critical` | Maximizes visibility per Constitution |
| Use notification IDs | Enables real-time transcription updates |
| Fallback to notify-send | Graceful degradation per Constitution |
| Action buttons via `-A` | Enables stop-recording from notification |

---

## Implementation Phases

### Phase 1: Core Notification System
- Add PersistentNotification class to notifications.py
- Implement send, update, close methods
- Add fallback handling

### Phase 2: Integration
- Integrate with toggle_dictate.py
- Show notification on recording start
- Update with transcription (future feature)
- Close on recording stop

### Phase 3: Testing
- Add unit tests for PersistentNotification
- Verify fallback behavior
- Test notification lifecycle
