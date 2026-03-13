## ADDED Requirements

### Requirement: View transcription history
The system SHALL provide a command to view past transcriptions.

#### Scenario: List recent transcriptions
- **WHEN** the user runs the `history` command without options
- **THEN** the system displays a list of recent transcriptions with date, time, and preview of text (first 50 characters)

#### Scenario: Limit history results
- **WHEN** the user runs `history --limit N`
- **THEN** the system displays only the N most recent transcriptions

#### Scenario: Filter history by date
- **WHEN** the user runs `history --date YYYY-MM-DD`
- **THEN** the system displays only transcriptions from that specific date

---

### Requirement: View full transcript details
The system SHALL provide detailed view of individual transcripts.

#### Scenario: View transcript by ID
- **WHEN** the user runs `history show <id>`
- **THEN** the system displays the full transcript text, audio file path, duration, language, and timestamp

#### Scenario: View transcript with audio file
- **WHEN** the user runs `history show <id> --audio`
- **THEN** the system displays the transcript details along with the path to the saved audio file

---

### Requirement: Search transcripts
The system SHALL provide search functionality for transcripts.

#### Scenario: Search transcripts by text content
- **WHEN** the user runs `history search <query>`
- **THEN** the system searches transcript text and displays matching transcriptions with the query highlighted

#### Scenario: Case-insensitive search
- **WHEN** the user searches for a term
- **THEN** the search is case-insensitive and matches partial words

---

### Requirement: Delete transcript from history
The system SHALL allow deletion of transcripts from history.

#### Scenario: Delete single transcript
- **WHEN** the user runs `history delete <id>`
- **THEN** the system removes the transcript from the database and deletes the associated audio file

#### Scenario: Confirm deletion
- **WHEN** the user attempts to delete a transcript
- **THEN** the system prompts for confirmation before deletion
