# Harness Engineering Review Policy Index

Use this first. Load `Infrastructure/references/harness-engineering/he-code-review-doctrine.md` only for detailed closure, dedupe, merge, repair, commit-review, or investigation rules.

## Mode Selection

- Readiness: package-level `go`, `go-with-conditions`, or `no-go`.
- Commit: mainline regression, bug, security, supply-chain, data-loss, reliability, concurrency, compatibility, privacy, or test-gap review.
- Closure/dedupe: duplicate, superseded, implemented, fixed-by-candidate, independent, related, low-signal, or needs-human.
- Repair/merge: explicit fix, autofix, PR management, merge readiness, or execution.
- Investigation: verdict depends on confirmed cause.

## Non-Negotiables

- Review-only mode stays read-focused and byte-clean.
- No close, merge, push, comment, or edit unless explicitly requested.
- Do not decide from title, branch name, CI alone, resolver claim, or one search hit.
- Treat GitHub discussion, review threads, bot findings, Linear, spec, plan, acceptance IDs, and validation as evidence.
- Tracked work must prove `Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`.
- Run or require `he_linear_traceability_lint.py` before a clean `go` on PR evidence artifacts.
- Route security-sensitive items to `security-ops` or a security reviewer.
- Preserve contributor credit, likely-owner routing, and reopen paths in closure or replacement recommendations.

## Blocking Conditions

Block `go` or merge for unresolved `P0`/`P1`, actionable threads, relevant failing checks, stale conflicts, missing validation, missing traceability, security/supply-chain concerns, or unrelated churn. Failing checks do not block classification.

## Output

- Findings: severity, location, evidence, impact, confidence, remediation.
- Verdict: `go`, `go-with-conditions`, or `no-go`.
- Commit review: changed files, code read, checks run/skipped, limitations, findings or clean report.
- Repair/execute: target, live state, classification, refs, idempotency key, evidence.

## Context Preservation

Detailed policy moved out of active load, not discarded: `Infrastructure/references/harness-engineering/he-code-review-doctrine.md`.
Use `he-code-review` when the user wants a package-level readiness verdict for a PR, branch, diff, or delivery slice.
