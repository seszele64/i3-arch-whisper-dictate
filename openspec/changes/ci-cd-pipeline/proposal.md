## Why

The i3-arch-whisper-dictate project currently lacks automated testing and validation. This creates risk of regressions when making changes and makes it difficult to ensure compatibility across different Python versions and Linux distributions. A CI/CD pipeline is needed to automate testing, linting, and provide confidence in code quality.

## What Changes

- Create GitHub Actions workflow for continuous integration (CI)
- Set up test matrix across Python 3.11, 3.12, 3.13
- Set up OS matrix for Ubuntu (primary), Arch, Debian, and Fedora (scheduled)
- Integrate Ruff linting enforcement in CI
- Implement hybrid testing strategy with mocked unit tests and scheduled integration tests
- Add status badges to README for build visibility
- Create pytest integration markers for test categorization

## Capabilities

### New Capabilities
- `ci-workflow`: GitHub Actions workflows for automated testing and linting
- `test-matrix`: Multi-version Python and OS testing configuration
- `hybrid-testing`: Unit tests with mocks and scheduled integration tests with real API

### Modified Capabilities
- None (this is infrastructure-only, no behavioral changes to application code)

## Impact

- New `.github/workflows/` directory for workflow definitions
- `ci.yml` workflow runs on every push and PR
- `integration.yml` workflow runs on schedule with real OpenAI API
- `pyproject.toml` or `pytest.ini` may need updates for marker configuration
- README.md will include status badges
- Requires `OPENAI_API_KEY` secret for integration tests
