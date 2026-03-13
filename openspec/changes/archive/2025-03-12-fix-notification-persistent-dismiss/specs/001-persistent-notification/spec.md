## MODIFIED Requirements

### Requirement: Recording notification uses stack tag for persistence
The system SHALL send recording notifications using dunst stack tags (x-dunst-stack-tag) instead of notification IDs to ensure reliable cross-process notification management.

#### Scenario: Start recording notification
- **GIVEN** the system is ready to start recording
- **WHEN** notify_recording_start() is called
- **THEN** the system sends a persistent notification with stack tag "whisper-dictate-recording" and critical urgency
- **AND** the notification timeout is set to 0 (infinite/persistent)
- **AND** the notification urgency is set to critical

#### Scenario: Stop recording notification
- **GIVEN** a recording notification is currently displayed with stack tag "whisper-dictate-recording"
- **WHEN** notify_recording_stop() is called
- **THEN** the system sends a replacement notification with the same stack tag
- **AND** the new notification has a 2-second timeout so it auto-dismisses
- **AND** the original persistent notification is automatically replaced

---

### Requirement: Graceful handling when notification daemon is unavailable
The system SHALL handle gracefully when the notification daemon (dunstify) is unavailable, both when opening and closing notifications.

#### Scenario: Open notification when dunstify is unavailable
- **WHEN** recording starts and dunstify is NOT available
- **THEN** the system logs a warning and returns False without errors

#### Scenario: Close notification when dunstify is unavailable
- **WHEN** recording stops and dunstify is NOT available
- **THEN** the system logs a warning and returns False without errors

---

### Requirement: Stack tag approach eliminates ID tracking issues
The system SHALL use dunst stack tags to manage recording notifications, eliminating the need to track and persist notification IDs.

#### Scenario: Notification replacement via stack tag
- **GIVEN** a notification with stack tag "whisper-dictate-recording" is displayed
- **WHEN** another notification with the same stack tag is sent
- **THEN** the new notification automatically replaces the existing one

#### Scenario: Cross-process notification management
- **GIVEN** the recording notification was sent by a previous script invocation
- **WHEN** a new script invocation sends a notification with the same stack tag
- **THEN** the new notification replaces the old one without requiring ID file persistence
