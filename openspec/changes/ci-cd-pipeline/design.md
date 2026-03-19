## Context

The i3-arch-whisper-dictate project is a Python application that provides voice dictation functionality using OpenAI's Whisper API. Currently, testing is manual and there's no automated validation of code quality or cross-platform compatibility.

Current state:
- Tests exist in `tests/` directory using pytest
- Ruff is configured for linting
- No automated CI/CD in place
- Manual testing only

## Goals / Non-Goals

**Goals:**
- Automate testing on every push and pull request
- Enforce code quality through automated linting
- Ensure compatibility across Python 3.11, 3.12, 3.13
- Validate functionality on multiple Linux distributions
- Provide visibility into build status via README badges
- Support both fast feedback (mocked tests) and thorough validation (real API tests)

**Non-Goals:**
- Branch protection rules (manual for now)
- Deployment automation (out of scope)
- CD (continuous deployment) - only CI
- Windows/macOS support (Linux only for now)

## Decisions

### GitHub Actions as CI Platform
**Decision**: Use GitHub Actions for CI
**Rationale**: Native GitHub integration, free for public repos, extensive marketplace
**Alternatives considered**: GitLab CI (requires migration), Travis CI (less popular now), Jenkins (self-hosted complexity)

### Hybrid Testing Strategy
**Decision**: Split tests into unit (mocked) and integration (real API)
**Rationale**: Unit tests provide fast feedback without API costs; integration tests validate real behavior
**Implementation**:
- Unit tests: Run on every push/PR with mocked OpenAI API
- Integration tests: Run on schedule (weekly) with real OPENAI_API_KEY
- Use `@pytest.mark.integration` marker to categorize tests

### OS Matrix Strategy
**Decision**: Ubuntu primary in CI, all 4 distros in scheduled runs
**Rationale**: Ubuntu is fastest and most common; full matrix on schedule catches distro-specific issues
**Distributions**: Ubuntu (primary), Arch Linux (rolling), Debian (stable), Fedora (bleeding-edge)

### Linting Enforcement
**Decision**: Use Ruff for linting in CI
**Rationale**: Already configured in project, fast, comprehensive
**Enforcement**: CI fails if `ruff check .` finds any issues

## Risks / Trade-offs

**[Risk] Integration tests require OPENAI_API_KEY secret** → Mitigation: Store in GitHub Secrets, only used in scheduled runs, not on PRs from forks

**[Risk] Arch Linux testing may be unstable (rolling release)** → Mitigation: Use scheduled runs only, not blocking PRs

**[Risk] Real API tests incur costs** → Mitigation: Weekly schedule only, short test duration, mock-heavy coverage

**[Risk] Test flakiness with real API** → Mitigation: Retry logic in workflow, timeout settings, fallback to mock tests for PRs

## Migration Plan

1. Create `.github/workflows/ci.yml` - Immediate effect on next push
2. Create `.github/workflows/integration.yml` - Scheduled runs begin
3. Add pytest markers to existing tests
4. Update README.md with badges
5. Validate with test PR

## Open Questions

- What day/time should integration tests run? ~~(Suggest: Weekly on Sunday 00:00 UTC)~~ **Resolved: Sunday 00:00 UTC**
- Should integration tests notify on failure? (Suggest: Issue creation) **Out of Scope: Notification on failure is not implemented in this iteration**
