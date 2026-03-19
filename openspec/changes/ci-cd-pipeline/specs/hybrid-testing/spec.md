## ADDED Requirements

### Requirement: Unit tests use mocked OpenAI API
Unit tests SHALL use mock implementations of the OpenAI API to avoid requiring API keys.

#### Scenario: Mock API in unit tests
- **WHEN** unit tests execute
- **THEN** OpenAI API calls SHALL be mocked
- **AND** no real API calls SHALL be made

### Requirement: Integration tests use real OpenAI API
Integration tests marked with @pytest.mark.integration SHALL use the real OpenAI API.

#### Scenario: Real API in integration tests
- **WHEN** integration tests execute with OPENAI_API_KEY set
- **THEN** real OpenAI API calls SHALL be made
- **AND** actual transcription SHALL occur

### Requirement: Pytest integration marker exists
The project SHALL have a pytest marker named "integration" for categorizing integration tests.

#### Scenario: Integration marker registered
- **WHEN** pytest configuration is loaded
- **THEN** the "integration" marker SHALL be registered

#### Scenario: Skip integration tests in unit test run
- **WHEN** running unit tests without integration marker
- **THEN** tests marked with @pytest.mark.integration SHALL be skipped

### Requirement: Integration workflow runs on schedule
The integration workflow SHALL run automatically on a weekly schedule at Sunday 00:00 UTC.

#### Scenario: Weekly scheduled run at specific time
- **WHEN** the time is Sunday 00:00 UTC
- **THEN** the integration workflow SHALL trigger automatically
- **AND** the workflow SHALL run with the latest code from main

### Requirement: Integration workflow supports manual trigger
The integration workflow SHALL support manual triggering via workflow_dispatch.

#### Scenario: Manual workflow trigger
- **WHEN** a user triggers the workflow manually
- **THEN** the integration workflow SHALL execute

### Requirement: OPENAI_API_KEY is masked in all logs and outputs
The integration workflow SHALL mask the OPENAI_API_KEY secret in all logs, outputs, and artifacts.

#### Scenario: API key masked in workflow logs
- **GIVEN** the OPENAI_API_KEY is set as a secret
- **WHEN** the integration workflow runs
- **THEN** the API key value SHALL NOT appear in workflow logs
- **AND** the API key SHALL be replaced with "***" in any output

#### Scenario: API key masked in error messages
- **GIVEN** an API call fails during integration tests
- **WHEN** error messages are logged
- **THEN** the OPENAI_API_KEY value SHALL NOT appear in error output

### Requirement: Integration tests skip when API key is missing
The integration workflow SHALL skip integration tests gracefully when OPENAI_API_KEY is not available.

#### Scenario: Missing API key causes skip not failure
- **GIVEN** the OPENAI_API_KEY secret is not set
- **WHEN** the integration workflow runs
- **THEN** integration tests SHALL be skipped
- **AND** the workflow SHALL NOT fail due to missing API key
- **AND** a message SHALL indicate tests were skipped

### Requirement: Integration tests have timeout and retry logic
The integration workflow SHALL implement timeout and retry logic for API calls.

#### Scenario: Integration test timeout enforced
- **GIVEN** an integration test is running
- **WHEN** the test exceeds 60 seconds
- **THEN** the test SHALL be terminated
- **AND** the test SHALL be marked as failed

#### Scenario: API call retry on failure
- **GIVEN** an API call fails with a retryable error
- **WHEN** the integration test makes the API call
- **THEN** the call SHALL be retried up to 3 times
- **AND** retries SHALL use exponential backoff

#### Scenario: Retry succeeds on second attempt
- **GIVEN** an API call fails on first attempt
- **AND** the call succeeds on second attempt
- **WHEN** the integration test executes
- **THEN** the test SHALL pass after retry

### Requirement: Integration tests validate transcription results
The integration workflow SHALL validate that transcription results meet expected criteria.

#### Scenario: Transcription produces expected text
- **GIVEN** a test audio file with known content
- **WHEN** the audio is transcribed using the OpenAI API
- **THEN** the transcription SHALL contain expected keywords
- **AND** the transcription SHALL have a minimum confidence level

#### Scenario: Transcription handles audio file requirement
- **GIVEN** the integration tests require a test audio file
- **WHEN** tests are executed
- **THEN** a test audio file SHALL be available in tests/fixtures/
- **AND** the file SHALL be a valid audio format (wav or mp3)
- **AND** the file size SHALL be under 25MB

#### Scenario: Transcription failure handling
- **GIVEN** an invalid or corrupted audio file
- **WHEN** transcription is attempted
- **THEN** the test SHALL handle the error gracefully
- **AND** appropriate error information SHALL be logged
