# Risk Management

## Purpose

Track and manage risks tied to this repository’s AI/system governance and release controls.

## Risk scoring

- **Likelihood:** 1 (rare) to 5 (likely)
- **Impact:** 1 (minor) to 5 (critical)
- **Score:** likelihood × impact

## Active risks

| ID | Risk | Likelihood | Impact | Score | Mitigation | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RS-001 | Incomplete PR evidence for policy/security changes | 2 | 3 | 6 | PR gate + required section checklist | Jamie | Accepted |
| RS-002 | Missing or late secret/dependency checks | 2 | 5 | 10 | Gov gates script (`.github/scripts/gov_security_gates.py`) + PR review | Jamie | Open |
| RS-003 | Branch protection drift | 1 | 4 | 4 | Branch manifest + periodic settings review | Jamie | Open |

## Incident handling

1. Log incident in `GOVERNANCE/incidents.md` with timeline, impact, and mitigations.
2. Add temporary exception in `GOVERNANCE/exceptions.md` only when approved.
3. Close and review within 30 days unless risk profile changes.

## Review cadence

- Monthly risk review.
- Immediate escalation for high score risks (>=12).
