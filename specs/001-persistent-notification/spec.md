# Feature Specification: Persistent Notification During Recording

**Feature Branch**: `001-persistent-notification`  
**Created**: 2026-02-15  
**Status**: Draft  
**Input**: User description: "Persistent notification during recording"

## User Scenarios & Testing

### User Story 1 - Notification appears and stays visible during recording (Priority: P1)

As a user, I want a notification to appear immediately when I start recording and remain visible for the entire duration of recording, so that I can easily see that recording is active without having to remember it myself.

**Why this priority**: This is the core value proposition of the feature - users currently have to remember they are recording because notifications disappear. This directly addresses the main user pain point.

**Independent Test**: Can be fully tested by starting a recording and verifying a notification appears and stays visible until recording stops.

**Acceptance Scenarios**:

1. **Given** the application is idle, **When** the user initiates recording, **Then** a persistent notification immediately appears displaying recording status.

2. **Given** a recording is in progress with a visible notification, **When** the user continues recording for any duration, **Then** the notification remains visible and does not disappear.

3. **Given** a recording is in progress, **When** the user stops the recording, **Then** the persistent notification closes.

---

### User Story 2 - Real-time transcription updates in notification (Priority: P2)

As a user, I want the notification to show live transcription text as it becomes available during recording, so that I can see what is being transcribed in real-time.

**Why this priority**: Provides immediate feedback on transcription quality and allows users to verify accuracy before stopping recording.

**Independent Test**: Can be tested by speaking during recording and observing the notification body update with transcribed text.

**Acceptance Scenarios**:

1. **Given** recording is in progress with a persistent notification, **When** speech is transcribed, **Then** the notification body updates to show the transcribed text.

2. **Given** more speech is transcribed during recording, **When** new text becomes available, **Then** the notification body replaces previous text with the new transcription.

---

### User Story 3 - Stop recording from notification (Priority: P3)

As a user, I want to be able to stop recording directly from the notification, so that I have a convenient way to end recording without using keyboard shortcuts.

**Why this priority**: Provides an additional, intuitive way to stop recording using the notification interface the user is already interacting with.

**Independent Test**: Can be tested by clicking or activating a stop action in the notification and verifying recording stops.

**Acceptance Scenarios**:

1. **Given** a recording is in progress with a persistent notification showing a stop action, **When** the user activates the stop action, **Then** recording stops and notification closes.

---

### Edge Cases

- What happens when the notification system (dunst) is not running?
- How does the system handle notifications if multiple recordings are attempted?
- What happens if the notification server crashes during recording?
- How does the system behave if the transcription service is unavailable?

## Requirements

### Functional Requirements

- **FR-001**: System MUST display a notification immediately when recording starts
- **FR-002**: System MUST keep the notification visible for the entire duration of recording (no auto-dismiss)
- **FR-003**: System MUST close the notification when recording stops
- **FR-004**: System MUST update the notification body with transcription text as it becomes available
- **FR-005**: System MUST provide a way to stop recording directly from the notification interface
- **FR-006**: System MUST handle gracefully when the notification daemon is unavailable
- **FR-007**: System MUST ensure only one persistent notification exists at a time during recording

### Key Entities

- **RecordingState**: Represents the current state of recording (idle, recording, processing)
- **Notification**: Represents the persistent display element showing recording status and transcription
- **TranscriptionText**: Represents the transcribed text content that updates during recording

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can verify recording is active by looking at the notification within 1 second of starting recording
- **SC-002**: The persistent notification remains visible throughout recordings of any duration (tested up to 10 minutes)
- **SC-003**: 100% of recording sessions result in a visible persistent notification from start to stop
- **SC-004**: Transcription text updates appear in the notification within 2 seconds of speech being transcribed
- **SC-005**: Users successfully stop recording via notification action in at least 95% of attempts

## Assumptions

- The notification system (dunst) is the primary target for this feature
- Users have keyboard shortcuts bound to start/stop recording (existing functionality)
- The notification urgency level should be set high enough to ensure visibility
- Notification updates should not cause visual flicker or distraction
