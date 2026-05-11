---
schema_version: 1
artifact_id: agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec-technical-review
artifact_type: he-code-review
type: he-code-review
canonical_slug: agent-skills-jsc-167-ask-bootstrap-command-discoverability
title: Agent Skills JSC-167 Ask Bootstrap Command Discoverability Spec Technical Review
harness_stage: he-code-review
status: complete
date: 2026-05-10
origin: .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md
reviewed_artifact: .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md
traceability_required: true
linear_status: existing
linear_issue: JSC-167
linear_issue_url: https://linear.app/jscraik/issue/JSC-167/harden-ask-bootstrap-and-command-discoverability
linear_team: JSC
linear_workspace: Jscraik
linear_project: agent-skills
linear_milestone: Command surface and ask reliability
linear_parent_issue_title: "Harden ask bootstrap and command discoverability"
review_result: approved_for_he_plan
---

# Agent Skills JSC-167 Ask Bootstrap Command Discoverability Spec Technical Review

## Review Verdict

Approved for `he-plan`.

The deepened spec is now strong enough for planning. It keeps the slice bounded
to `JSC-167`, requires proof for the failure modes Linear names, blocks silent
global shell mutation, keeps `JSC-168` and `JSC-169` as defer routes rather than
in-scope work, and requires deterministic docs and shim-identity evidence before
closure.

No blocking findings remain.

## Reviewed Artifacts

- `.harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md`
- `.harness/linear/agent-skills-linear-plan.md`
- `Docs/agents/5-minute-success-path.md`
- `README.md`
- `AGENTS.md`
- `bin/ask`
- `Infrastructure/bin/ask`
- `Infrastructure/scripts/lib/ask/commands/repo.py`
- `Plugins/harness-engineering/skills/he-spec/SKILL.md`
- `Plugins/harness-engineering/skills/he-code-review/SKILL.md`
- `Plugins/harness-engineering/references/document-review-finding-tiers.md`

## Linear Work Item Contract

| Field | Value |
| --- | --- |
| Linear issue | `JSC-167` |
| URL | https://linear.app/jscraik/issue/JSC-167/harden-ask-bootstrap-and-command-discoverability |
| Team | `JSC` |
| Workspace | `Jscraik` |
| Project | `agent-skills` |
| Milestone | `Command surface and ask reliability` |
| Parent issue title | `Harden ask bootstrap and command discoverability` |
| Reviewed artifact | `.harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md` |
| Review result | Approved for `he-plan`; not approved for implementation closure |

## Linear / Spec / Plan / PR Traceability

| Linear issue | Source acceptance IDs | Plan units | Acceptance IDs | PR evidence |
| --- | --- | --- | --- | --- |
| `JSC-167` | SA1-SA12 | PLAN-JSC167-001 through PLAN-JSC167-005 | SA1-SA12 | Spec technical review approves `he-plan`; PR evidence is not available because implementation has not started. |

## Findings

### Finding 1: Wrong `ask` Shim Proof Could Pass Against Another Checkout

Severity: High
Status: Fixed in spec
Finding tier: `safe_auto`

Evidence:

- The first deepened spec accepted `ask repo status --json` as a shim smoke
  without requiring proof that `ask` resolved to this checkout.
- The fixed spec now requires resolved path and repo identity fields in the
  bootstrap proof output, adds an invariant that `repo_root_resolved` or
  `command -v ask` must prove the intended repo root, adds CF9 for wrong global
  shims, and adds a stop rule for missing shim identity proof.

Why it mattered:

`ask` could resolve to an unrelated global command and still exit successfully,
creating false confidence in PATH discoverability.

Review result:

Resolved. `he-plan` must now include repo-identity proof for any claimed
`ask` shim success.

### Finding 2: JSC-168/JSC-169 Boundary Was Too Easy To Pull Into JSC-167

Severity: Medium
Status: Fixed in spec
Finding tier: `safe_auto`

Evidence:

- The spec already marked dependency environment setup and lazy command imports
  out of scope, but the acceptance text could be read as requiring active
  diagnostics for those adjacent issues.
- The fixed spec narrows SA10 to preserving raw failure evidence and returning a
  defer route only when those failures are encountered. CF5 and CF6 now
  explicitly forbid implementing dependency setup or lazy-loading architecture
  in this slice.

Why it mattered:

An implementation plan could have expanded into dependency management or command
loading architecture while appearing to satisfy the bootstrap spec.

Review result:

Resolved. `JSC-168` and `JSC-169` remain separate Linear work.

### Finding 3: Docs Proof Was Too Manual For A Drift-Prone Surface

Severity: Medium
Status: Fixed in spec
Finding tier: `safe_auto`

Evidence:

- The first deepened spec allowed "docs contract review" as an alternative to
  executable docs proof for SA6.
- The fixed spec requires deterministic docs contract validation or executable
  docs smoke, and states that manual review alone is not sufficient.

Why it mattered:

The core failure mode is command-path drift across README, the 5-minute path,
and validation/preflight surfaces. Manual review is useful context, but it is
not a closure-grade proof loop.

Review result:

Resolved. `he-plan` must name the deterministic docs assertion or executable
docs smoke it will use.

## Current Spec Strengths

### Scope Is Properly Bounded

Severity: Informational
Status: Pass

Evidence:

- The spec selects only `JSC-167`.
- `JSC-168`, `JSC-169`, `ask start`, `ask doctor --fix`, runtime projections,
  broad `ask` module cleanup, and cross-repo install policy are out of scope.
- Stop rules block global shell profile mutation, lazy import refactors, and
  dependency-contract implementation.

Operational impact:

The next `he-plan` should not drift into adjacent command architecture work.

### Failure Proof Is Now Characterized

Severity: Informational
Status: Pass

Evidence:

- The spec defines CF1 through CF9 for happy path, non-executable entrypoint,
  PATH-less shell, correct shim, wrong shim, dependency failures, optional-import
  failures, docs drift, and idempotence.
- SA9 and SA11 make negative proof and machine-readable output blocking
  acceptance criteria.

Operational impact:

Implementation must falsify the actual first-run failure modes instead of only
proving the current checkout is healthy.

### Linear Traceability Is Sufficient For Planning

Severity: Informational
Status: Pass

Evidence:

- The spec carries `linear_issue: JSC-167`, canonical `agent-skills` project,
  milestone `Command surface and ask reliability`, live labels, and live delta
  status.
- Linear Acceptance Traceability maps every Linear acceptance statement to
  concrete SA IDs.

Operational impact:

The next stage can create a plan without re-running tracker selection.

## Residual Risks

- The plan still needs to choose the exact canonical bootstrap command name.
- The plan must decide whether entrypoint/discoverability reporting lives in
  preflight, repo doctor, or both.
- Closure remains blocked until implementation supplies real CF2, CF3, CF9,
  deterministic docs, and idempotence evidence.

## Handoff

```yaml
schema_version: 1
interactive_status: autonomous_assumption
selection_evidence:
  - .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md
  - .harness/linear/agent-skills-linear-plan.md
  - Linear JSC-167 live issue read from prior gate
route: he-plan
stage: he-code-review
scope: JSC-167 ask bootstrap and command discoverability spec review
traceability:
  linear_issue: JSC-167
  reviewed_artifact: .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md
  review_artifact: .harness/review/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec-technical-review.md
validation:
  required:
    - python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md .harness/review/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec-technical-review.md
    - python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md .harness/review/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec-technical-review.md
    - python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md .harness/review/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec-technical-review.md
safe_to_continue: true
blocked_reason: null
blackboard_delta:
  current_slice: JSC-167 ready for he-plan
  review_result: approved_for_he_plan
  closure_requires:
    - CF2 non-executable entrypoint proof
    - CF3 PATH-less fallback proof
    - CF9 wrong-shim identity proof
    - deterministic docs contract proof
    - idempotence and no-global-mutation proof
```
