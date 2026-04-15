# Technical Review Findings

## Target

- Artifact: pull request diff
- Scope reference: PR #123
- Review mode: code-diff

## Findings

### F1
- Severity: P1
- Location: services/symphony/orchestrator.py:244
- Why it matters: Stale running entries can block dispatch and skew retry accounting.
- Recommended minimal fix: Remove stale running map entry before scheduling retry in all abnormal exits.
- Confidence: 0.87

### F2
- Severity: P2
- Location: Infrastructure/tests/symphony/test_orchestrator_retries.py:88
- Why it matters: Missing terminal-transition coverage leaves regression risk.
- Recommended minimal fix: Add a reconciliation test that transitions active->terminal while retry timer is queued.
- Confidence: 0.74

## Open Questions / Assumptions

- Assumes tracker refresh semantics remain consistent during pagination.

## Change Summary

- No code changed yet; this artifact captures actionable review findings.

## Residual Risks

- Concurrent worker exits may still race if state updates happen outside orchestrator authority.
