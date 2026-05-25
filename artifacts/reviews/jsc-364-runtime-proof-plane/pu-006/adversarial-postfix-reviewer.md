# Adversarial Postfix Review - PU-006

## Findings (severity-ranked)

No blocking adversarial findings identified in the post-fix PU-006 scope.

Post-fix checks requested in the handoff are consistent with the current code paths:
- source identity now derives from resolver source path when available
- runtime failure mapping distinguishes reachability failures as `blocked_runtime`
- explicit runtime targets (`codex` or `agents`) emit schema-valid evidence artifacts

## Residual Risks

1. Last-write-wins evidence replacement under concurrent proofs (advisory)
- Scenario:
  1. Two operators run `./bin/ask skills proof <same-handle> --runtime-target codex` concurrently.
  2. Both runs write to the same fixed artifact files under `.harness/evidence/runtime-proof/<handle>/codex/`.
  3. The later run overwrites probe/receipt/card outputs from the earlier run.
  4. A closeout consumer reading only path presence sees valid artifacts but loses earlier run context.
- Evidence:
  - `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:96` (deterministic per-handle/per-target evidence path)
  - `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:322`
  - `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:325` (unversioned write sequence)
- Remediation:
  - Keep canonical latest paths, but also emit an append-only run index (timestamped pointer or receipt log) so concurrent executions preserve an audit trail.

2. Recovery guidance contract drift for non-runtime gate failures (advisory)
- Scenario:
  1. A proof fails on a non-runtime gate such as resolver/command-handle generation and maps to `stale_or_drifted`.
  2. `recovery_plan.reason` is copied from generic `runtime_failure.recovery_guidance`, currently tuned to sync/link steps.
  3. Operators follow runtime-link recovery even when the true defect is resolver or projection generation.
  4. Repeated retries can hide root-cause classification and delay proper remediation.
- Evidence:
  - `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:73` (status mapping branch to `stale_or_drifted`)
  - `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:186`
  - `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:190` (recovery reason sourced from generic runtime_failure guidance)
  - `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:521`
  - `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:523` (single sync-focused guidance payload)
- Remediation:
  - Derive recovery guidance by failed gate class (resolver vs generated handle vs runtime link) so `stale_or_drifted` receipts recommend the right first corrective action.

## Validation ownership classification for observed broader gate failure

- `python3 -m pytest Infrastructure/tests -q` failing with `ModuleNotFoundError: yaml` remains environment/tooling failure (pre-existing), not introduced by these postfix edits.

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-006/adversarial-postfix-reviewer.md

