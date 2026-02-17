# Feature Specification: Real-time/Streaming transcription during recording

**Feature Branch**: `002-streaming-transcription`
**Created**: 2026-02-15
**Status**: Draft
**Input**: User description: "Transcribe audio in chunks during the recording session to provide incremental transcription results, rather than waiting for the entire recording to complete."

## Clarifications

### Session 2026-02-15

- **Q**: Should we use OpenAI Realtime API or chunk-based approach for streaming transcription?  
  **A**: Use chunk-based approach - incrementally send recorded audio chunks to Whisper API rather than using the Realtime API. This involves:
  - Recording audio in overlapping chunks (5-10 seconds with 2-second overlap)
  - Sending chunks to Whisper API as they become available
  - Merging partial transcriptions using longest common sequence (LCS) algorithm
  - Displaying incremental results in the notification

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See transcription while recording (Priority: P1)

As a user, I want to see transcription text appear in real-time while I am recording, so that I can verify the system is working correctly and see my words being captured as I speak.

**Why this priority**: This is the core value proposition of the feature - eliminating the wait time after recording and providing immediate feedback to the user. Without this, the feature delivers no value.

**Independent Test**: Can be fully tested by starting a recording, speaking for a few seconds, and observing that transcription text appears in the notification before recording stops.

**Acceptance Scenarios**:

1. **Given** the user has started recording, **When** the user speaks for at least 5 seconds, **Then** partial transcription text appears in the notification within 3 seconds of speech ending
2. **Given** transcription is displaying in real-time, **When** the user continues speaking, **Then** new text is appended to the existing transcription in the notification
3. **Given** the user is recording with real-time transcription active, **When** the user stops recording, **Then** the final complete transcription is available within 1 second

---

### User Story 2 - Seamless chunk boundary handling (Priority: P2)

As a user, I want the transcription to flow naturally across audio chunks without repeated or missing words, so that the final result reads as a coherent continuous text.

**Why this priority**: While real-time display is the primary goal, poor chunk handling would create a frustrating user experience with garbled or repetitive text. This ensures quality output.

**Independent Test**: Can be tested by recording a continuous paragraph of speech and verifying the final transcription contains no duplicate phrases at chunk boundaries and no missing words.

**Acceptance Scenarios**:

1. **Given** the user is recording continuous speech, **When** audio is processed in chunks, **Then** the final merged transcription contains no duplicate words or phrases at chunk boundaries
2. **Given** the user is recording continuous speech, **When** audio is processed in chunks, **Then** no words are lost at chunk boundaries
3. **Given** the user pauses mid-sentence, **When** a chunk boundary occurs during the pause, **Then** the transcription correctly resumes without duplication when speech continues

---

### User Story 3 - Cost-efficient transcription (Priority: P3)

As a user, I want the system to minimize redundant processing of the same audio, so that my usage costs remain reasonable while still getting accurate real-time results.

**Why this priority**: Cost efficiency is important for sustainability but secondary to functionality. This can be implemented after the core feature works.

**Independent Test**: Can be tested by measuring the total audio duration sent for transcription versus the actual recording duration - overhead should be within acceptable limits.

**Acceptance Scenarios**:

1. **Given** a 60-second recording, **When** processed with chunk overlap for accuracy, **Then** the total audio sent for transcription does not exceed 75 seconds (25% overhead maximum)
2. **Given** the system is configured for cost optimization, **When** processing chunks, **Then** overlap duration is minimized while maintaining transcription accuracy above 95%

---

### Edge Cases

- What happens when the user speaks very briefly (less than a chunk duration)?
- How does the system handle network interruptions during streaming transcription?
- What happens when the user pauses for an extended period during recording?
- How does the system handle very rapid speech that may be cut at chunk boundaries?
- What happens if the transcription service is temporarily unavailable during recording?
- How does the system handle overlapping speech or multiple speakers at chunk boundaries?
- What happens when the notification reaches its maximum displayable text length during a long recording?
- How does the system handle ambiguous words that span across chunk boundaries?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST transcribe audio incrementally during the recording session, not waiting for recording to complete
- **FR-002**: System MUST display partial transcription results in the notification interface as they become available
- **FR-003**: System MUST merge partial transcriptions from consecutive chunks without duplicate words or phrases
- **FR-004**: System MUST ensure no words are lost at chunk boundaries during the merge process
- **FR-005**: System MUST complete final transcription within 1 second of recording stop
- **FR-006**: System MUST handle audio chunks of variable duration based on natural speech pauses
- **FR-007**: System MUST maintain transcription accuracy of at least 95% compared to non-streaming transcription
- **FR-008**: System MUST gracefully handle extended pauses in speech without losing context
- **FR-009**: System MUST provide visual indication that transcription is in progress
- **FR-010**: System MUST make the final complete transcription available to the user after recording stops

### Key Entities *(include if feature involves data)*

- **Audio Chunk**: A segment of recorded audio sent for transcription, characterized by duration, sequence order, and audio data
- **Partial Transcription**: The text result from a single audio chunk, including metadata about its position in the overall recording
- **Merged Transcription**: The accumulated and deduplicated text from all processed chunks, representing the current state of the full transcription
- **Chunk Boundary**: The transition point between two consecutive audio chunks, requiring special handling to avoid duplication or loss

## Scope

### IN Scope

- Chunk-based incremental transcription using standard Whisper API (not Realtime API)
- Core real-time transcription functionality during active recording sessions
- Incremental audio chunking and processing with configurable chunk sizes
- Merging and deduplication of partial transcription results
- Display of partial transcription results in the notification interface
- Handling of natural speech pauses and variable chunk durations
- Support for recordings up to 10 minutes in duration
- Single-speaker transcription scenarios
- Online transcription with network connectivity

### OUT of Scope

- Multi-language support and automatic language detection
- Speaker diarization (identifying who spoke when)
- Multi-speaker identification and separation
- Offline transcription without network connectivity
- Audio preprocessing (noise cancellation, echo reduction)
- Transcription of pre-recorded audio files
- Real-time translation of transcribed text
- Persistent storage of transcription history
- Integration with third-party note-taking applications
- Support for recording durations exceeding 10 minutes

## Assumptions

- User has a working microphone with sufficient audio quality for speech recognition
- System has sufficient memory for audio buffering during recording sessions
- Transcription service supports standard API calls with audio file uploads (not requiring WebSocket/streaming connections)
- Network connectivity is available during recording for transcription API access
- User speaks clearly enough for speech recognition to function effectively
- Notification system has adequate display capacity for showing partial transcriptions
- Transcription service maintains reasonable availability and response times

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Transcription text appears in the notification within 3 seconds of speech completion during recording
- **SC-002**: Final transcription is available within 1 second of the user stopping the recording
- **SC-003**: Zero duplicate words or phrases exist at chunk boundaries in the final transcription
- **SC-004**: Word error rate at chunk boundaries does not exceed 5% compared to non-streaming transcription
- **SC-005**: Total audio data sent for transcription does not exceed 125% of actual recording duration (25% maximum overhead)
- **SC-006**: 95% of users report that real-time transcription feels responsive and useful
- **SC-007**: Transcription accuracy for streaming matches non-streaming accuracy within 2% for recordings up to 5 minutes
- **SC-008**: System handles recordings up to 10 minutes without degradation in transcription quality or notification performance
