---
status: complete
priority: p2
issue_id: '004'
tags:
  - code-review
  - security
  - governance
dependencies: []
---

## Problem Statement
Policy and signature paths are user-overridable via CLI, and signature validation only checks policy-file hash equality with provided sig file. This allows self-signed alternate policy files to bypass intended canonical reviewer governance.

## Findings
- In /Users/jamiecraik/dev/agent-skills/scripts/human_promote_recursive_run.sh:35-36 and 78-84, callers can override --policy-file and --policy-sig-file.
- In /Users/jamiecraik/dev/agent-skills/scripts/human_promote_recursive_run.sh:221-235 and validate_recursive_promotion.py:116-125, validation ensures only that sig == sha256(policy_raw), not that policy is trusted canonical content.
- A caller can pass an arbitrary allowlist policy + matching hash signature to satisfy checks.

## Proposed Solutions
### Option 1: Disallow policy path overrides in production flow
- **Pros:** Strongest governance guarantee with minimal complexity.
- **Cons:** Reduces flexibility for local experiments.
- **Effort:** Small
- **Risk:** Low

### Option 2: Pin expected policy digest/public key and verify canonical trust
- **Pros:** Supports verified policy updates while retaining integrity checks.
- **Cons:** Requires key/digest rotation process.
- **Effort:** Medium
- **Risk:** Medium

### Option 3: Gate overrides behind explicit dev-only flag with audit event
- **Pros:** Preserves flexibility and improves observability.
- **Cons:** Still weaker than fully pinned policy in some environments.
- **Effort:** Medium
- **Risk:** Medium

## Recommended Action


## Technical Details
### Affected files/components
- `/Users/jamiecraik/dev/agent-skills/scripts/human_promote_recursive_run.sh`
- `/Users/jamiecraik/dev/agent-skills/utilities/skill-creator/scripts/validate_recursive_promotion.py`
- `/Users/jamiecraik/dev/agent-skills/docs/skill-graphs/governance/recursive-loop-approvers.yaml`

## Acceptance Criteria
- [ ] Promotion gate cannot be approved using arbitrary external policy/sig paths in standard workflow.
- [ ] Validation proves policy trust against canonical source (or signed key), not just hash pairing.
- [ ] Audit logs show when non-canonical policy is attempted and block decision.

## Work Log
- 2026-02-24: Implemented and validated fix in repository code.
- 2026-02-24: Created from PR #18 multi-agent code review synthesis.

## Resources
- PR: https://github.com/jscraik/Agent-Skills/pull/18
- Commit: 1c5f11d
- Known pattern docs:
  - `/Users/jamiecraik/dev/agent-skills/docs/skill-graphs/index.md`
  - `/Users/jamiecraik/dev/agent-skills/docs/skill-graphs/telemetry/daily-outputs.md`
  - `/Users/jamiecraik/dev/agent-skills/docs/skill-graphs/schemas/gate-contract.schema.md`
