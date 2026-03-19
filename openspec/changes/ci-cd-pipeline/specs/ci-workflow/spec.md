## ADDED Requirements

### Requirement: CI workflow triggers on push and pull request
The CI workflow SHALL trigger on every push to any branch and on every pull request.

#### Scenario: Push triggers workflow
- **WHEN** a developer pushes code to any branch
- **THEN** the CI workflow SHALL execute

#### Scenario: Pull request triggers workflow
- **WHEN** a pull request is opened or updated
- **THEN** the CI workflow SHALL execute

### Requirement: CI workflow runs linting with Ruff
The CI workflow SHALL run Ruff linting and fail if any linting errors are found.

#### Scenario: Linting passes
- **WHEN** code has no linting errors
- **THEN** the linting job SHALL pass

#### Scenario: Linting fails
- **WHEN** code has linting errors
- **THEN** the linting job SHALL fail
- **AND** the workflow SHALL be marked as failed

### Requirement: CI workflow runs unit tests with pytest
The CI workflow SHALL run pytest unit tests using mocked dependencies.

#### Scenario: Unit tests pass
- **WHEN** all unit tests pass
- **THEN** the test job SHALL pass

#### Scenario: Unit tests fail
- **WHEN** any unit test fails
- **THEN** the test job SHALL fail
- **AND** the workflow SHALL be marked as failed

### Requirement: CI workflow generates coverage report
The CI workflow SHALL generate a test coverage report.

#### Scenario: Coverage report generated
- **WHEN** tests complete successfully
- **THEN** a coverage report SHALL be generated
- **AND** coverage percentage SHALL be reported

### Requirement: Coverage report meets minimum threshold
The CI workflow SHALL enforce a minimum code coverage threshold of 80%.

#### Scenario: Coverage meets threshold
- **GIVEN** the codebase has 80% or higher coverage
- **WHEN** tests complete successfully
- **THEN** the coverage check SHALL pass
- **AND** the workflow SHALL continue

#### Scenario: Coverage below threshold
- **GIVEN** the codebase has less than 80% coverage
- **WHEN** tests complete
- **THEN** the coverage check SHALL fail
- **AND** the workflow SHALL be marked as failed

#### Scenario: Coverage artifacts uploaded
- **WHEN** coverage report is generated
- **THEN** the HTML coverage report SHALL be uploaded as an artifact
- **AND** the artifact SHALL be accessible for download

### Requirement: CI workflow implements concurrency control
The CI workflow SHALL cancel in-progress runs when a new push occurs to the same branch.

#### Scenario: Concurrent run cancellation
- **GIVEN** a workflow run is in progress on a branch
- **WHEN** a new push occurs to the same branch
- **THEN** the in-progress run SHALL be cancelled
- **AND** a new workflow run SHALL start

### Requirement: CI workflow implements dependency caching
The CI workflow SHALL cache pip dependencies between runs to improve performance.

#### Scenario: Cache hit improves performance
- **GIVEN** pip dependencies are cached from a previous run
- **WHEN** the workflow runs with the same dependencies
- **THEN** dependencies SHALL be restored from cache
- **AND** pip install time SHALL be reduced

#### Scenario: Cache miss installs fresh dependencies
- **GIVEN** no cached dependencies exist
- **WHEN** the workflow runs
- **THEN** dependencies SHALL be installed fresh
- **AND** the cache SHALL be updated for future runs

### Requirement: CI workflow exports test results as artifacts
The CI workflow SHALL export test results in JUnit XML format as artifacts.

#### Scenario: JUnit XML artifact generation
- **WHEN** tests complete
- **THEN** test results SHALL be exported in JUnit XML format
- **AND** the XML file SHALL be uploaded as an artifact
- **AND** the artifact SHALL be accessible for analysis

### Requirement: CI workflow installs project dependencies
The CI workflow SHALL install the project and all its dependencies before running tests.

#### Scenario: Project installation
- **GIVEN** the repository is checked out
- **WHEN** the setup step executes
- **THEN** the project SHALL be installed in editable mode
- **AND** all dependencies from pyproject.toml SHALL be installed

### Requirement: CI workflow uses Ruff configuration from pyproject.toml
The CI workflow SHALL run `ruff check .` using the configuration defined in pyproject.toml.

#### Scenario: Ruff uses project configuration
- **GIVEN** pyproject.toml contains Ruff configuration
- **WHEN** the linting job executes
- **THEN** Ruff SHALL read configuration from pyproject.toml
- **AND** linting SHALL apply project-specific rules

### Requirement: CI workflow provides README badges
The CI workflow SHALL support README badges for build status and Python version support.

#### Scenario: CI status badge reflects main branch
- **GIVEN** the CI workflow is configured
- **WHEN** viewing the README on the main branch
- **THEN** a CI status badge SHALL display the current build status
- **AND** the badge SHALL link to the workflow results

#### Scenario: Python version badge
- **GIVEN** Python 3.11, 3.12, and 3.13 are supported
- **WHEN** viewing the README
- **THEN** a Python version badge SHALL display supported versions
- **AND** the badge SHALL indicate compatibility

### Requirement: CI workflow runs on all branches
The CI workflow SHALL run on all branches and exclude tag pushes.

#### Scenario: Push to feature branch triggers workflow
- **WHEN** code is pushed to any branch
- **THEN** the CI workflow SHALL execute

#### Scenario: Tag push excluded
- **WHEN** a tag is pushed
- **THEN** the CI workflow SHALL NOT execute
