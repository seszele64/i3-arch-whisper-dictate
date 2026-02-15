# Research: Persistent Notification Feature

**Feature**: Persistent Notification During Recording  
**Date**: 2026-02-15

## Technical Decisions

### Decision 1: Use dunstify for persistent notifications

**Chosen**: dunstify with specific flags

**Rationale**: 
- dunstify is the correct tool for i3/sway environments with dunst
- -t 0 makes notification persistent (never auto-dismiss)
- -u critical ensures high visibility
- -p returns notification ID for updates
- -r allows updating notification body

**Alternatives considered**:
- notify-send: Does not support persistent notifications well
- D-Bus directly: More complex, overkill for this use case

---

### Decision 2: Notification ID tracking for updates

**Chosen**: Store notification ID and use for updates

**Rationale**:
- Enables real-time transcription text updates
- Single notification stays visible, body content changes

---

### Decision 3: Graceful fallback to notify-send

**Chosen**: Check dunstify availability, fallback if not available

**Rationale**: Per Constitution - Reliability is NON-NEGOTIABLE
- Must handle cases where dunst is not installed
- Should not fail silently - log warnings

---

### Decision 4: Stack tags for simpler updates

**Chosen**: Use stack tags as alternative to notification IDs

**Rationale**:
- Simpler implementation - no ID tracking needed
- dunst replaces notifications with same stack tag

---

## Technical Specifications

### Dunstify Command Reference

| Flag | Description |
|------|-------------|
| -t 0 | Persistent - never auto-dismiss |
| -u critical | Critical urgency for visibility |
| -p | Print notification ID to stdout |
| -r | Replace existing notification |
| -C | Close notification |
| -A | Add action button |

---

## Error Handling

| Scenario | Handling |
|----------|----------|
| dunstify not found | Fall back to notify-send |
| dunst daemon not running | Use ensure_dunst_running() |
| Notification fails | Log warning, continue |
