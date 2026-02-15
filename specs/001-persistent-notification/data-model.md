# Data Model: Persistent Notification Feature

**Feature**: Persistent Notification During Recording  
**Date**: 2026-02-15

## Entities

### RecordingState

Represents the current state of the recording session.

| Field | Type | Description |
|-------|------|-------------|
| status | enum | idle, recording, processing |
| started_at | datetime | When recording started |
| notification_id | int/null | ID of persistent notification |

**State Transitions**:
- idle -> recording: User starts recording
- recording -> processing: User stops recording, audio being transcribed
- processing -> idle: Transcription complete

---

### NotificationConfig

Configuration for persistent notifications.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| timeout | int | 0 | 0 = persistent (never dismiss) |
| urgency | string | critical | low, normal, critical |
| stack_tag | string | recording | dunst stack tag for updates |

---

### NotificationMessage

The content displayed in the notification.

| Field | Type | Description |
|-------|------|-------------|
| summary | string | Title (e.g., "Recording...") |
| body | string | Transcription text or status |
| has_stop_action | bool | Whether stop button is available |

---

## Relationships

```
RecordingState 1--1 NotificationConfig
RecordingState 1--0..1 Notification (active notification)
```

---

## Validation Rules

- notification_id must be positive integer when status is recording
- timeout must be 0 for persistent notifications
- urgency must be one of: low, normal, critical
