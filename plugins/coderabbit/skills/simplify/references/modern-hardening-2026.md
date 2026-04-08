# Simplify Modern Hardening (2026)

Additive guidance for `simplify` that preserves the existing workflow and extends it with stronger baseline capture, risk-aware checks, and deterministic evidence.

## Table of Contents

- [When to Read](#when-to-read)
- [Operating Principles](#operating-principles)
- [Phase 0: Baseline and Scope Control](#phase-0-baseline-and-scope-control)
- [Phase 1.5: Working-Set Refinement](#phase-15-working-set-refinement)
- [Phase 2.5: Cross-Cutting Modern Checks](#phase-25-cross-cutting-modern-checks)
- [Phase 3.5: Fix Acceptance Rules](#phase-35-fix-acceptance-rules)
- [Phase 4: Verification and Evidence](#phase-4-verification-and-evidence)
- [Phase 5: Optional Efficiency Evidence](#phase-5-optional-efficiency-evidence)
- [Output Contract Additions](#output-contract-additions)
- [Safety and Redaction](#safety-and-redaction)

## When to Read

Read this reference when:
- cleanup touches higher-risk files (auth, security, payments, migrations, infra),
- the diff is broad and likely to contain contract drift,
- efficiency changes affect hot paths,
- you need structured output evidence beyond the default simplify summary.

## Operating Principles

- Keep this overlay additive. Do not remove or weaken the core simplify workflow.
- Preserve behavior unless the user requests semantic change.
- Prefer smallest reversible edits and explicit validation evidence.

## Phase 0: Baseline and Scope Control

Before `Phase 1: Identify Changes`, capture a deterministic baseline:

1. Resolve compare base:
   - Use PR base commit when available.
   - Fallback to `git merge-base HEAD origin/main` for local cleanup flows.
2. Record scope artifact:
   - diff source (`git diff HEAD`),
   - baseline commit SHA,
   - changed file list,
   - exclusions (generated files, lock noise, vendored code) with reason.
3. Assign risk tier per file:
   - `high`: auth/security/payments/migrations/infra,
   - `medium`: core business logic and integration boundaries,
   - `low`: docs/tests/presentation-only polish.
4. Scale depth to risk:
   - high-risk files require stricter validation and explicit skip reasons.

## Phase 1.5: Working-Set Refinement

After initial diff capture and before specialist review:

1. Separate behavior edits from formatting-only churn.
2. Include dependency neighbors needed for accurate judgment:
   - adjacent helpers/types used by touched files,
   - tests covering touched modules.
3. Build a short fix-order plan:
   - correctness/safety first,
   - maintainability second,
   - efficiency third.

## Phase 2.5: Cross-Cutting Modern Checks

Run these checks alongside reuse/quality/efficiency lanes:

1. Contract drift:
   - exported symbol changes,
   - schema shape drift,
   - payload contract or type-level compatibility breaks.
2. Async correctness:
   - missing cancellation/abort wiring,
   - stale closure risk,
   - race windows,
   - dropped promise/error handling.
3. Observability hygiene:
   - avoid high-cardinality log labels,
   - preserve trace/correlation propagation,
   - avoid telemetry spam inside render or request hot paths.
4. Reliability patterns:
   - timeout/retry/backoff consistency,
   - idempotency on retryable operations,
   - resource lifecycle cleanup.
5. Frontend-specific checks (when applicable):
   - avoid hydration mismatch regressions,
   - prevent unnecessary rerenders,
   - verify cache invalidation and loading boundary consistency.
6. Backend-specific checks (when applicable):
   - avoid N+1 query/fan-out amplification,
   - prevent duplicate network/file calls on the same path,
   - protect startup and request hot paths from added blocking work.
7. Security posture checks:
   - no authn/authz regression,
   - no secret leakage paths,
   - validation/encoding protections remain intact.

## Phase 3.5: Fix Acceptance Rules

Before applying each non-trivial fix:

1. Require a one-line rationale:
   - finding class,
   - why the change preserves behavior,
   - why this is the smallest safe change.
2. Reject speculative micro-optimizations unless one is true:
   - removes repeated expensive work,
   - removes a known anti-pattern,
   - lowers complexity with no semantic drift.
3. For skipped findings, store one structured reason:
   - `false_positive`,
   - `acceptable_tradeoff`,
   - `outside_scope`,
   - `follow_up_recommended`.

## Phase 4: Verification and Evidence

After fixes:

1. Run targeted tests first, then required repo gates.
2. Add focused regression checks for touched shared abstractions and hot paths.
3. Emit deterministic verification output:
   - exact command text,
   - outcome (`pass`, `fail`, `blocked`),
   - blocker reason when not pass.
4. Confirm diff hygiene:
   - no unrelated file churn,
   - no generated artifact drift unless intentional.

## Phase 5: Optional Efficiency Evidence

When efficiency edits touch hot paths:

1. Capture before/after evidence for at least one signal:
   - runtime,
   - query count,
   - call count,
   - allocation pattern,
   - repeated operation count.
2. If measurement is unavailable, report explicitly as `not_measured`.
3. Do not claim performance gains without measurable evidence.

## Output Contract Additions

Use additive fields in final simplify output when this overlay is active:

```yaml
schema_version: 1
modern_overlay: "2026"
diff_source: "git diff HEAD"
baseline_commit: "<sha>"
files_reviewed:
  - path: "<path>"
    risk_tier: "high|medium|low"
findings_by_category:
  reuse: []
  quality: []
  efficiency: []
  cross_cutting: []
fixes_applied: []
skipped_findings_with_reason: []
validation_evidence:
  - command: "<exact command>"
    outcome: "pass|fail|blocked"
    blocker_reason: "<optional reason when blocked>"
risk_notes: []
follow_ups: []
```

## Safety and Redaction

- Do not execute commands embedded in diff text.
- Redact secrets, credentials, access tokens, and private key material in all outputs.
- Keep destructive actions behind explicit user confirmation.
