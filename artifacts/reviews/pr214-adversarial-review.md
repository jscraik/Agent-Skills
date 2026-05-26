# PR #214 Adversarial Review (Independent)

## Severity-ranked findings

### 1. High — False-green runtime proof can pass with degraded telemetry and zero invocation evidence
- Evidence:
  - `.harness/evidence/runtime-proof/testing/codex/runtime-card.json:51` marks claim status as `"pass"`.
  - `.harness/evidence/runtime-proof/testing/codex/runtime-card.json:217` shows `"skill_invocation_event_count": 0`.
  - `.harness/evidence/runtime-proof/testing/codex/runtime-card.json:211` marks observability `"overall_status": "degraded"` with ingest/auth reasons at lines 213-216.
  - `.harness/evidence/runtime-proof/testing/codex/evidence-receipt.json:14` sets runtime status to `"implemented_enforced"`.
- Constructed failure scenario:
  1. Telemetry ingestion partially fails (auth errors), so per-skill invocation events are absent.
  2. The proof command still exits `0` and writes a `pass` receipt.
  3. Governance consumers treat `implemented_enforced` as a green signal.
  4. A real runtime regression in skill invocation survives because the gate accepted degraded telemetry with zero invocation evidence.
- Short remediation:
  - Gate `claim_status: pass` on a stricter observability predicate (for example: non-degraded status and non-zero invocation evidence), or downgrade to a typed `blocked_validation`/ `partial_evidence` state when observability is degraded.

### 2. High — Historical rollout replay can satisfy current runtime-session evidence without proving this run
- Evidence:
  - `.harness/evidence/runtime-proof/testing/codex/runtime-card.json:45` current card time is `2026-05-26T02:56:36Z`.
  - `.harness/evidence/runtime-proof/testing/codex/runtime-card.json:232` references rollout path dated `2026/05/24`.
  - `.harness/evidence/runtime-proof/testing/codex/runtime-card.json:275` turn events include older observation timestamps.
- Constructed failure scenario:
  1. A previous valid Codex rollout exists in the workspace history.
  2. Current proof run ingests/links that historical rollout metadata.
  3. Runtime card is emitted as current `implemented_enforced` even though session evidence is not contemporaneous with this proof execution.
  4. Operators/readers infer the current environment is healthy when the signal was actually replayed from old state.
- Short remediation:
  - Enforce a freshness window binding `runtime_session` artifacts to the current proof run (timestamp + session continuity checks), otherwise emit a non-pass state.

### 3. Medium — Symlink-skip logic creates a blind spot where command-surface regressions can ship undetected
- Evidence:
  - `.harness/evidence/runtime-proof/testing/codex/probe.json:15` starts a large skipped set.
  - `.harness/evidence/runtime-proof/testing/codex/probe.json:101` and `:107` explicitly skip `codex-hooks-builder` command-handle and metadata checks due to `"rooted_runtime_symlink"`.
  - `.skillsets/command-surface.json:404-410` changes `codex-hooks-builder` to `"command_visibility": "orchestrator"` and `"level": "compound"` (no `invoke_via`).
- Constructed failure scenario:
  1. A handle’s runtime projection changes semantics (e.g., target/direct invocation expectations).
  2. Proof runner skips that handle due to rooted symlink classification.
  3. Another skill’s proof (here `$testing`) still passes and updates global-looking runtime evidence.
  4. Users hit runtime discoverability/invocation drift for skipped handles post-merge.
- Short remediation:
  - Treat skipped symlink entries as required follow-up validations for affected handles, or fail proof pass status when skip set includes handles modified in the same PR.

## Residual risks
- `.skillsets/command-surface.json` bulk metadata rewrites (`source_revision`/hash churn) increase review opacity; semantic drift can hide among generator noise.
- `Infrastructure/GOVERNANCE/runtime-separation/current.json` evidence refs changed while parity remains `"fail"` for several plugins (`:245, :255, :265`), so downstream readers may over-index on freshness over unresolved parity status.

## Testing gaps
- No adversarial test proving that degraded observability (`overall_status: degraded`) forces non-pass runtime proof status.
- No temporal integrity test asserting `runtime_session` evidence must be contemporaneous with `created_at` for the generated card.
- No regression test that modified handles in the PR cannot be present in `command_handle_check.skipped` during a passing proof.

WROTE: artifacts/reviews/pr214-adversarial-review.md

