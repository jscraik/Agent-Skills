# Adversarial Final Review - PU-006

## Findings (severity-ranked)

No blocking adversarial findings identified in the reviewed PU-006 scope.

The explicit runtime-evidence write path composes correctly with `skills_proof` and preserves expected failure semantics:
- explicit `--runtime-target codex|agents` emits typed artifacts
- `--runtime-target any` skips evidence emission without leaking partial artifacts
- runtime link/readiness failures are represented as `blocked_runtime` with schema-valid evidence outputs

## Residual Risks

1. Last-write-wins evidence overwrite risk (advisory)
- Scenario:
  1. Two operators run `./bin/ask skills proof <same-handle> --runtime-target codex` near-simultaneously.
  2. Both executions target the same fixed artifact paths under `.harness/evidence/runtime-proof/<handle>/codex/`.
  3. The later write atomically replaces the earlier run’s probe/receipt/card snapshot.
  4. Coordinators consuming only path-presence may miss that earlier evidence was superseded.
- Evidence:
  - `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:92` (deterministic evidence_dir by handle/runtime_target)
  - `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:318` to `:321` (unversioned overwrite writes)
- Suggested remediation:
  - Keep current canonical paths for latest truth, but optionally append a timestamped run copy (or immutable event log pointer) to preserve short-term execution history for closeout audits.

2. External validator dependency in tests (advisory)
- Scenario:
  1. Runtime-card tests spawn `validate_runtime_cards.py` via subprocess.
  2. If runtime env/module resolution differs from the unit-test interpreter environment, tests can fail even when runtime-card serialization is correct.
  3. This creates a composition failure where verification plumbing, not feature behavior, blocks CI confidence.
- Evidence:
  - `Infrastructure/tests/test_command_surface_handles.py:675` to `:693` (subprocess-based validator invocation)
- Suggested remediation:
  - Keep end-to-end validator coverage, but consider a small in-process schema assertion helper for core fields to reduce false negatives from interpreter/environment drift.

## Validation ownership classification for observed gate failure

- `python3 -m pytest Infrastructure/tests -q` ModuleNotFoundError: yaml -> environment/tooling failure (pre-existing), unrelated to this PU-006 change set.

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-006/adversarial-final-reviewer.md
