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

- Treat readiness and code review as evidence problems, not title, branch-name, CI, or resolver-claim problems.
- Resolve target, base, review mode, local instructions, Linear/spec/plan links, acceptance IDs, CI, review threads, and validation evidence before judging.
- Build one evidence pack from diff/base, changed files, local instructions, GitHub discussion, review threads, Linear issue, spec, plan, acceptance IDs, checks, validation, and relevant history.
- For Codex-compatible review, mirror native review semantics: target `uncommitted`, `base`, `commit`, or custom PR/diff review; report only actionable introduced bugs with tight changed-line locations and `overall_correctness`.
- For Harness readiness, rank only concrete readiness issues as `P0`-`P3`; discard style-only, speculative, duplicate, and protected-artifact cleanup notes.
- Emit `go`, `go-with-conditions`, or `no-go` with exact evidence and routing to `he-work`, `autofix`, `security-ops`, or GitHub workflow when needed.

## Inputs

- Review target: PR, branch, current diff, uncommitted changes, commit, commit range, artifact path, or delivery slice.
- Intended base branch and review mode.
- Linked Linear issue, spec or plan paths, acceptance IDs, review threads, checks, and validation evidence when available.

## Procedure

1. Run the eligibility gate before deep review: closed, draft, automated, trivial, already-reviewed, or explicitly no-review items should be reported as ineligible unless the user asks to override.
2. Select the nearest mode from the local review policy index before doing deeper work.
3. Resolve target, base, mode, local instruction files, Linear issue, spec, plan, and acceptance IDs.
4. Read the diff/files/artifacts deeply enough to understand behavior, including surrounding code and changed-file comments.
5. Apply independent lenses: instruction compliance, introduced obvious bugs, relevant history/blame, previous PR or review context, code-comment invariants, breaking changes, change size, context safety, testing evidence, and security-sensitive surfaces.
6. Verify each candidate issue against the evidence pack; drop pre-existing, unchanged-line, intentional, nit-only, CI-catchable, generic, or low-confidence findings.
7. Check reviewer threads, bot comments, CI, validation, Linear/spec/plan traceability, and security-sensitive surfaces.
8. Emit separate Codex-compatible code review and Harness readiness results.

## Outputs

- `schema_version: 1`.
- `codex_review` for introduced code bugs:
  - `findings[]` with `title`, `body`, `confidence_score`, `priority`, and `code_location.absolute_file_path` plus `code_location.line_range`.
  - `overall_correctness`: `patch is correct` or `patch is incorrect`.
  - `overall_explanation` and `overall_confidence_score`.
- `harness_readiness` for delivery state: `verdict`, `linear_traceability`, `spec_plan_traceability`, `validation_state`, `review_threads`, and `next_action`.
- Severity-ranked readiness findings with exact file or artifact evidence.
- Follow-up routing when implementation, security review, validation, or PR management is required.

## Linear Readiness

For tracked delivery, verify:

`Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`

Do not treat branch names, PR titles, or resolver claims as closure. A clean `go` requires behavior and validation evidence tied back to Linear and the governing artifacts.

## Validation

- Each finding needs severity, exact location, evidence, impact, confidence, and remediation.
- Codex-compatible findings must be tight, actionable, and anchored to changed lines; use absolute paths when available and line ranges small enough to fix directly.
- Keep only high-confidence candidate issues after verification. If an issue depends on uncertain intent, previous behavior, or external state, state the limitation rather than inflating severity.
- Block `go` for unresolved `P0`/`P1`, actionable reviewer threads, relevant failing checks, stale conflicts, missing validation, or missing Linear/spec/plan/PR traceability.
- For PR evidence artifacts, run `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py <artifact-path>` before returning a `go` verdict.
- Stop at the first failed required gate; do not proceed past a blocker.
- Route broad security-sensitive decisions to `security-ops` or a security reviewer.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not claim readiness without repository evidence.
- Keep review-only work read-focused unless the user explicitly requests mutation.
- Do not comment, close, merge, push, label, or resolve threads unless the user explicitly asks for PR management.

## Anti-patterns

- Treating passing CI alone as merge readiness.
- Approving tracked PRs without Linear/spec/plan/PR traceability.
- Reporting vague findings without concrete code or artifact evidence.
- Reporting pre-existing, intentional, unchanged-line, style-only, or generic test/documentation concerns as introduced code bugs.

## Examples

- "Can you inspect the open JSC-231 PR with Harness Engineering code review, including the Linear issue, spec, plan, CodeRabbit threads, and failed macOS job before I merge it?"
- "Please validate commit 7f3c2d1 on main for regressions and supply-chain risk before I cherry-pick it into the release branch."
- "Can you review my uncommitted changes against origin/main and return Codex-compatible findings plus the Harness Engineering readiness verdict?"

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
