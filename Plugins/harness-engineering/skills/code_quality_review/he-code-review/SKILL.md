---
name: he-code-review
description: Review PRs, branches, diffs, commits, and workflow artifacts for Codex-compatible code findings plus Harness Engineering package readiness. Use when users need traceable go/no-go synthesis, merge risk, or introduced-bug review.
metadata:
  skill-type: code_quality_review
---

# Harness Engineering Code Review

Use when package-level readiness, merge risk, release go/no-go, tracked PR closure, or Codex-compatible introduced-bug review is the core question.

Context preservation: Do not remove important context for budget trimming; move it to references and index it in `Plugins/harness-engineering/references/deferred-context-index.md`.

## Philosophy

Treat readiness as an evidence problem. Prefer concrete blockers, traceability, and live review-thread state over title, branch, CI, or resolver claims.

## When to use

Use `he-code-review` for package-level readiness review of a PR, branch, diff, commit range, or tracked delivery slice.

## Contract

- Resolve target, base, mode, local instructions, Linear/spec/plan links, acceptance IDs, CI, review threads, validation, and relevant history before judging.
- Use Codex-compatible review for introduced code bugs: `uncommitted`, `base`, `commit`, PR, or custom diff target; tight changed-line findings; `overall_correctness`.
- Use Harness readiness for delivery state: `Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`.
- Calibrate `overall_confidence_score` from evidence completeness; target `0.96` only when the 0.96 Evidence Ladder is satisfied.
- Emit concrete `P0`-`P3` readiness findings, `go`/`go-with-conditions`/`no-go`, and routing to `he-work`, `autofix`, `security-ops`, or GitHub workflow when needed.

## Inputs

- Review target: PR, branch, current diff, uncommitted changes, commit, commit range, artifact path, or delivery slice.
- Intended base branch and review mode.
- Linked Linear issue, spec or plan paths, acceptance IDs, review threads, checks, and validation evidence when available.

## Procedure

1. Run the eligibility gate: closed, draft, automated, trivial, already-reviewed, or no-review targets are ineligible unless overridden.
2. Select the mode from the Review policy index, then resolve target/base/instructions/tracker/spec/plan evidence.
3. Read the diff, surrounding code, changed-file comments, history, review context, checks, validation, and traceability evidence.
4. Apply review lenses from the policy index; verify each candidate and drop pre-existing, unchanged-line, intentional, nit-only, CI-catchable, generic, duplicate, or low-confidence issues.
5. Apply confidence caps from the policy index, then emit separate Codex-compatible code review and Harness readiness results.

## Outputs

- `schema_version: 1`.
- `codex_review`: `findings[]`, `overall_correctness`, `overall_explanation`, `overall_confidence_score`.
- `evidence_ladder`: completed checks, missing checks, confidence caps applied, and why the final score is realistic.
- `harness_readiness`: `verdict`, `linear_traceability`, `spec_plan_traceability`, `validation_state`, `review_threads`, `next_action`.
- Severity-ranked readiness findings with exact file or artifact evidence.
- Follow-up routing when implementation, security review, validation, or PR management is required.

## Linear Readiness

For tracked delivery, verify:

`Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`

Do not treat branch names, PR titles, or resolver claims as closure. A clean `go` requires behavior and validation evidence tied back to Linear and the governing artifacts.

## Validation

- Each finding needs severity, exact location, evidence, impact, confidence, and remediation.
- Codex-compatible findings must be tight, actionable, and anchored to changed lines; use absolute paths when available and line ranges small enough to fix directly.
- Block `go` for unresolved `P0`/`P1`, actionable reviewer threads, relevant failing checks, stale conflicts, missing validation, or missing Linear/spec/plan/PR traceability.
- Do not return `overall_confidence_score >= 0.96` unless target/base, local diff, changed files, instructions, surrounding code, review-thread state, validation, projection/runtime state when relevant, and unrelated-dirty-work impact are all checked or explicitly not applicable.
- For PR evidence artifacts, run `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py <artifact-path>` before returning a `go` verdict.
- Fail fast: stop at the first failed required gate and report the blocker instead of continuing past it.
- Route broad security-sensitive decisions to `security-ops` or a security reviewer.

## Constraints

- Redact secrets and keep review-only work read-focused.
- Do not comment, close, merge, push, label, resolve threads, or edit unless explicitly asked.

## Anti-patterns

- Claiming readiness from CI alone, branch names, titles, resolver claims, or vague evidence.
- Do not report pre-existing, intentional, unchanged-line, style-only, or generic test/documentation concerns as introduced code bugs.

## Examples

- "Can you inspect the open JSC-231 PR with Harness Engineering code review, including the Linear issue, spec, plan, CodeRabbit threads, and failed macOS job before I merge it?"
- "Please validate commit 7f3c2d1 on main for regressions and supply-chain risk before I cherry-pick it into the release branch."
- "Can you review my uncommitted changes against origin/main and return Codex-compatible findings plus the Harness Engineering readiness verdict?"

## Gotchas

- Do not resolve reviewer threads from this skill unless explicitly in an autofix or PR-management mode.
- If base, target, scope, or required tracker/spec/plan evidence is missing, stop instead of giving a false readiness verdict.

## References

- Review policy index: `Plugins/harness-engineering/skills/code_quality_review/he-code-review/references/review-policy-index.md`
- Full retained doctrine: `Infrastructure/references/harness-engineering/he-code-review-doctrine.md`
- Skill assets: `Plugins/harness-engineering/skills/code_quality_review/he-code-review/assets/icon-small.png`, `Plugins/harness-engineering/skills/code_quality_review/he-code-review/assets/icon-large.png`
- Subagent routing: `Plugins/harness-engineering/references/subagent-routing.md`
- Domain and QA routing: `Plugins/harness-engineering/references/domain-model-routing.md`, `Plugins/harness-engineering/references/qa-intake-routing.md`
