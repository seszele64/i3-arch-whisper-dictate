## 1. Setup GitHub Actions Workflows

- [ ] 1.1 Create `.github/workflows/` directory structure
- [ ] 1.2 Create `.github/workflows/ci.yml` with push/PR triggers
- [ ] 1.3 Create `.github/workflows/integration.yml` with schedule trigger

## 2. Configure CI Workflow

- [ ] 2.1 Add Python 3.11, 3.12, 3.13 to CI test matrix
- [ ] 2.2 Add Ubuntu runner configuration to CI workflow
- [ ] 2.3 Add Ruff linting step to CI workflow
- [ ] 2.4 Add pytest execution step with mocked dependencies
- [ ] 2.5 Add coverage report generation to CI workflow
- [ ] 2.6 Configure workflow to fail on linting or test errors

## 3. Configure Integration Workflow

- [ ] 3.1 Add weekly schedule trigger (Sunday 00:00 UTC)
- [ ] 3.2 Add workflow_dispatch trigger for manual runs
- [ ] 3.3 Add Ubuntu, Arch Linux, Debian, and Fedora container configurations
- [ ] 3.4 Configure OPENAI_API_KEY secret access
- [ ] 3.5 Add integration test execution step

## 4. Setup Hybrid Testing

- [ ] 4.1 Register "integration" pytest marker in pytest.ini or pyproject.toml
- [ ] 4.2 Update existing integration tests with @pytest.mark.integration marker
- [ ] 4.3 Verify unit tests use mocked OpenAI API
- [ ] 4.4 Configure unit test run to skip integration tests

## 5. Documentation and Visibility

- [ ] 5.1 Add CI status badge to README.md
- [ ] 5.2 Add Python version badges to README.md
- [ ] 5.3 Document CI/CD setup in project documentation
- [ ] 5.4 Add OPENAI_API_KEY secret configuration instructions

## 6. Validation and Testing

- [ ] 6.1 Verify CI workflow triggers on push
- [ ] 6.2 Verify CI workflow triggers on pull request
- [ ] 6.3 Verify Ruff linting enforcement works
- [ ] 6.4 Verify test matrix covers all Python versions
- [ ] 6.5 Verify integration workflow can be triggered manually
- [ ] 6.6 Verify coverage report is generated
