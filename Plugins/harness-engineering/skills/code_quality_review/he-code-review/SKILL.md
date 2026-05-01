---
name: he-code-review
description: Review PRs, branches, diffs, and workflow artifacts for package-level go/no-go readiness with severity-ranked synthesis. Use when users need readiness synthesis rather than detailed technical-risk critique.
metadata:
  skill-type: code_quality_review
---

# Harness Engineering Code Review

Use when package-level readiness, merge risk, release go/no-go, or tracked PR closure is the core question.

Context preservation: Do not remove important context for budget trimming; move it to references and index it in `Plugins/harness-engineering/references/deferred-context-index.md`.

## Philosophy

Treat readiness as an evidence problem. Prefer concrete blockers, traceability, and live review-thread state over title, branch, CI, or resolver claims.

## When to use

Use `he-code-review` for package-level readiness review of a PR, branch, diff, commit range, or tracked delivery slice.

## Contract

- Treat readiness as an evidence problem, not a title, branch-name, CI, or resolver-claim problem.
- Resolve target, base, mode, Linear/spec/plan links, acceptance IDs, CI, review threads, and validation evidence before judging.
- Build one evidence pack from diff/base, changed files, GitHub discussion, review threads, Linear issue, spec, plan, acceptance IDs, checks, and validation.
- Rank only concrete readiness issues as `P0`-`P3`; discard style-only, speculative, duplicate, and protected-artifact cleanup notes.
- Emit `go`, `go-with-conditions`, or `no-go` with exact evidence and routing to `he-work`, `autofix`, `security-ops`, or GitHub workflow when needed.

## Inputs

- Review target: PR, branch, diff, commit range, artifact path, or delivery slice.
- Intended base branch and review mode.
- Linked Linear issue, spec or plan paths, acceptance IDs, review threads, checks, and validation evidence when available.

## Procedure

1. Select the nearest mode from the local review policy index before doing deeper work.
2. Resolve target, base, mode, Linear issue, spec, plan, and acceptance IDs.
3. Read the diff/files/artifacts deeply enough to understand behavior.
4. Check reviewer threads, bot comments, CI, validation, Linear/spec/plan traceability, and security-sensitive surfaces.
5. Rank findings and emit the readiness verdict.

## Outputs

- `schema_version: 1`.
- Severity-ranked readiness findings with exact file or artifact evidence.
- A `go`, `go-with-conditions`, or `no-go` recommendation.
- Follow-up routing when implementation, security review, validation, or PR management is required.

## Linear Readiness

For tracked delivery, verify:

`Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`

Do not treat branch names, PR titles, or resolver claims as closure. A clean `go` requires behavior and validation evidence tied back to Linear and the governing artifacts.

## Validation

- Each finding needs severity, exact location, evidence, impact, confidence, and remediation.
- Block `go` for unresolved `P0`/`P1`, actionable reviewer threads, relevant failing checks, stale conflicts, missing validation, or missing Linear/spec/plan/PR traceability.
- For PR evidence artifacts, run `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py <artifact-path>` before returning a `go` verdict.
- Stop at the first failed required gate; do not proceed past a blocker.
- Route broad security-sensitive decisions to `security-ops` or a security reviewer.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not claim readiness without repository evidence.
- Keep review-only work read-focused unless the user explicitly requests mutation.

## Anti-patterns

- Treating passing CI alone as merge readiness.
- Approving tracked PRs without Linear/spec/plan/PR traceability.
- Reporting vague findings without concrete code or artifact evidence.

## Examples

- "Can you inspect the open JSC-231 PR with Harness Engineering code review, including the Linear issue, spec, plan, CodeRabbit threads, and failed macOS job before I merge it?"
- "Please validate commit 7f3c2d1 on main for regressions and supply-chain risk before I cherry-pick it into the release branch."

## Gotchas

- Do not treat passing CI alone as merge readiness.
- Do not resolve reviewer threads from this skill unless explicitly in an autofix or PR-management mode.
- Keep security-sensitive or policy-sensitive concerns routed to the appropriate specialist.
- If the base, target, review scope, or required tracker/spec/plan evidence is missing, stop and request that source instead of giving a false readiness verdict.

## References

- Review policy index: `Plugins/harness-engineering/skills/code_quality_review/he-code-review/references/review-policy-index.md`
- Full retained doctrine: `Infrastructure/references/harness-engineering/he-code-review-doctrine.md`
- Skill assets: `Plugins/harness-engineering/skills/code_quality_review/he-code-review/assets/icon-small.png`, `Plugins/harness-engineering/skills/code_quality_review/he-code-review/assets/icon-large.png`
- Subagent routing: `Plugins/harness-engineering/references/subagent-routing.md`
- Domain and QA routing: `Plugins/harness-engineering/references/domain-model-routing.md`, `Plugins/harness-engineering/references/qa-intake-routing.md`
