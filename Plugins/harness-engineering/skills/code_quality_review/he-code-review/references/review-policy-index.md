# Harness Engineering Review Policy Index

Use this first. Load `Infrastructure/references/harness-engineering/he-code-review-doctrine.md` only for detailed closure, dedupe, merge, repair, commit-review, or investigation rules.

## Mode Selection

- Codex-compatible review: introduced-bug review for `uncommitted`, `base`, `commit`, PR, or custom diff targets; returns `findings[]`, `overall_correctness`, `overall_explanation`, and `overall_confidence_score`.
- Readiness: package-level `go`, `go-with-conditions`, or `no-go`.
- Commit: mainline regression, bug, security, supply-chain, data-loss, reliability, concurrency, compatibility, privacy, or concrete test-gap review.
- Closure/dedupe: duplicate, superseded, implemented, fixed-by-candidate, independent, related, low-signal, or needs-human.
- Repair/merge: explicit fix, autofix, PR management, merge readiness, or execution.
- Investigation: verdict depends on confirmed cause.

## Eligibility Gate

Before deep review, classify closed, draft, automated, trivial, already-reviewed, or explicitly no-review targets as ineligible unless the user asks to override. Re-check eligibility before any requested PR comment or mutation.

## Non-Negotiables

- Review-only mode stays read-focused and byte-clean.
- No close, merge, push, comment, or edit unless explicitly requested.
- Do not decide from title, branch name, CI alone, resolver claim, or one search hit.
- Discover applicable local instruction files for root and touched paths before judging compliance.
- Treat GitHub discussion, review threads, bot findings, Linear, spec, plan, acceptance IDs, and validation as evidence.
- Tracked work must prove `Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`.
- For Codex-compatible findings, report only actionable issues introduced by the target and anchor them to tight changed-line ranges.
- Filter pre-existing, unchanged-line, intentional, style-only, CI-catchable, generic, duplicate, and low-confidence concerns.
- Run or require `he_linear_traceability_lint.py` before a clean `go` on PR evidence artifacts.
- Route security-sensitive items to `security-ops` or a security reviewer.
- Preserve contributor credit, likely-owner routing, and reopen paths in closure or replacement recommendations.

## Review Lenses

- Instruction compliance against applicable local guidance.
- Introduced obvious bugs and regression paths in the diff.
- Relevant history, blame, previous PRs, review comments, and changed-file code comments.
- Breaking API, CLI, configuration, serialization, migration, permission, or rollout changes.
- Change-size, context-safety, focused testing, validation, and security/supply-chain evidence.

## Blocking Conditions

Block `go` or merge for unresolved `P0`/`P1`, actionable threads, relevant failing checks, stale conflicts, missing validation, missing traceability, security/supply-chain concerns, or unrelated churn. Failing checks do not block classification.

## Output

- Codex review: `findings[]`, `overall_correctness`, `overall_explanation`, `overall_confidence_score`.
- Findings: severity, location, evidence, impact, confidence, remediation.
- Harness readiness: `go`, `go-with-conditions`, or `no-go`.
- Commit review: changed files, code read, checks run/skipped, limitations, findings or clean report.
- Repair/execute: target, live state, classification, refs, idempotency key, evidence.

## Context Preservation

Detailed policy moved out of active load, not discarded: `Infrastructure/references/harness-engineering/he-code-review-doctrine.md`.
Use `he-code-review` when the user wants a package-level readiness verdict for a PR, branch, diff, or delivery slice.
