## 1. Setup GitHub Actions Workflows

- [x] 1.1 Create `.github/workflows/` directory structure
- [x] 1.2 Create `.github/workflows/ci.yml` with push/PR triggers
- [x] 1.3 Create `.github/workflows/integration.yml` with schedule trigger

## 2. Configure CI Workflow

- [x] 2.1 Add Python 3.11, 3.12, 3.13 to CI test matrix
- [x] 2.2 Add Ubuntu runner configuration to CI workflow
- [x] 2.3 Add Ruff linting step to CI workflow
- [x] 2.4 Add pytest execution step with mocked dependencies
- [x] 2.5 Add coverage report generation to CI workflow
- [x] 2.6 Configure workflow to fail on linting or test errors

## 3. Configure Integration Workflow

- [x] 3.1 Add weekly schedule trigger (Sunday 00:00 UTC)
- [x] 3.2 Add workflow_dispatch trigger for manual runs
- [x] 3.3 Add Ubuntu, Arch Linux, Debian, and Fedora container configurations
- [x] 3.4 Configure OPENAI_API_KEY secret access
- [x] 3.5 Add integration test execution step

## 4. Setup Hybrid Testing

- [x] 4.1 Register "integration" pytest marker in pytest.ini or pyproject.toml
- [x] 4.2 Update existing integration tests with @pytest.mark.integration marker
- [x] 4.3 Verify unit tests use mocked OpenAI API
- [x] 4.4 Configure unit test run to skip integration tests

## 5. Documentation and Visibility

- [x] 5.1 Add CI status badge to README.md
- [x] 5.2 Add Python version badges to README.md
- [x] 5.3 Document CI/CD setup in project documentation
- [x] 5.4 Add OPENAI_API_KEY secret configuration instructions

## 6. Validation and Testing

- [x] 6.1 Verify CI workflow triggers on push
- [x] 6.2 Verify CI workflow triggers on pull request
- [x] 6.3 Verify Ruff linting enforcement works
- [x] 6.4 Verify test matrix covers all Python versions
- [x] 6.5 Verify integration workflow can be triggered manually
- [x] 6.6 Verify coverage report is generated
