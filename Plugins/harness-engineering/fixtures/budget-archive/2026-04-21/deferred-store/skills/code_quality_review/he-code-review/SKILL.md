---
name: he-code-review
description: Review PRs, branches, diffs, and workflow artifacts for package-level go/no-go readiness with severity-ranked synthesis. Use when users need readiness synthesis rather than detailed technical-risk critique.
metadata:
  skill-type: code_quality_review
---

# he-code-review Entry

Use when package-level readiness, merge risk, release go/no-go, or tracked PR closure is the core question.

Context preservation: Do not remove important context for budget trimming; move it to references and index it in `Plugins/harness-engineering/references/deferred-context-index.md`.

## Philosophy

- Prefer concrete blockers over broad commentary.
- Treat readiness as an evidence problem, not a title or branch-name problem.

## When to use

Use `he-code-review` when the user wants a package-level readiness verdict for a PR, branch, diff, or delivery slice.

## Required inputs

- PR, branch, diff, commit range, or artifact path under review.
- Intended base branch, linked Linear issue, spec or plan paths, and acceptance IDs when tracked work is involved.
- Available CI, reviewer-thread, and validation evidence.

## Deliverables

- Severity-ranked readiness findings with exact file or artifact evidence.
- A `go`, `go-with-conditions`, or `no-go` recommendation.
- Clear follow-up routing to `he-work`, `autofix`, `security-ops`, or GitHub PR workflow when required.

## Core Contract

- Resolve target, base, mode, and plan/spec links before judging.
- Build an evidence pack from diff/base, changed files, checks, validations, review threads, Linear issue, branch/PR, spec, plan, and acceptance IDs.
- Rank only concrete readiness issues as `P0`-`P3`; discard style-only, speculative, duplicate, and protected-artifact cleanup notes.
- Emit `go`, `go-with-conditions`, or `no-go`.
- Keep broad review read-focused unless an explicit mode permits safe autofix.

## Procedure

1. Resolve target, base, mode, Linear issue, spec, plan, and acceptance IDs.
2. Build the evidence pack from diff, checks, validation, and review threads.
3. Rank concrete findings and emit the readiness verdict.

## Linear Readiness

For tracked delivery, verify:

`Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`

Do not treat branch names, PR titles, or resolver claims as closure. A clean `go` requires behavior and validation evidence tied back to Linear and the governing artifacts.

## Validation

- Each finding needs severity, exact location, evidence, impact, confidence, and remediation.
- Block `go` for unresolved `P0`/`P1`, actionable reviewer threads, relevant failing checks, stale conflicts, missing validation, or missing Linear/spec/plan/PR traceability.
- For PR evidence artifacts, run `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py <artifact-path>` before returning a `go` verdict.
- Route broad security-sensitive decisions to `security-ops` or a security reviewer.
- Stop at the first failed gate.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not claim readiness without repository evidence.
- Keep broad reviews read-focused unless an explicit mode permits mutation.

## Anti-patterns

- Treating CI alone as merge readiness.
- Approving tracked PRs without Linear/spec/plan/PR traceability.
- Reporting vague findings without a concrete code or artifact path.

## Examples

- "Review this PR and verify it closes the linked Linear QA issue."
- "Check this branch against origin/main and give the go/no-go call."

## Failure mode

If the base, target, review scope, or required tracker/spec/plan evidence is missing, stop and request that source instead of giving a false readiness verdict.

## Gotchas

- Do not treat passing CI alone as merge readiness.
- Do not resolve reviewer threads from this skill unless explicitly in an autofix or PR-management mode.
- Keep security-sensitive or policy-sensitive concerns routed to the appropriate specialist.

## References

- Full guide: `Plugins/harness-engineering/fixtures/preserved-context/skills/he-code-review/SKILL.full.md`
- Review flow: `Plugins/harness-engineering/fixtures/preserved-context/skills/he-code-review/references/codex-review-flow.md`
- Review modes: `Plugins/harness-engineering/fixtures/preserved-context/skills/he-code-review/references/review-modes.md`
- Subagent routing: `Plugins/harness-engineering/references/subagent-routing.md`
- Domain and QA routing: `Plugins/harness-engineering/references/domain-model-routing.md`, `Plugins/harness-engineering/references/qa-intake-routing.md`
