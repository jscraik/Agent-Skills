## Simplification Analysis

### Core Purpose
PU-006 needs `skills proof --runtime-target codex` to always emit schema-valid runtime evidence artifacts (RuntimeCard, EvidenceReceipt, ArtifactRecord, probe), including durable typed `blocked_runtime` details when Codex runtime is unavailable.

### Severity-Ranked Findings

#### LOW: Duplicate artifact metadata assembly adds maintenance surface
- Evidence: `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:139`, `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:156`
- Why this is unnecessary complexity:
  - `artifact_record` and `probe_record` repeat nearly identical envelope fields (`source_identity`, `workspace_root`, `actor_type`, `mutation_scope`, `visibility_status`, `generated_by`, `validation_status`).
  - Any future schema extension must be edited in multiple places, increasing drift risk.
- Suggested simplification:
  - Add one tiny local helper (for example `_artifact_envelope(...)`) that fills shared fields and accepts only the changing fields (`artifact_id`, `artifact_type`, `path`, `consumer_contract`).
  - Keep output schema identical; only remove assembly duplication.

#### LOW: Runtime display strings are recomputed repeatedly
- Evidence: `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:93`, `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:119`, `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:175`, `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:230`
- Why this is unnecessary complexity:
  - `_runtime_display_name(runtime_target)` is called across many string templates in one function.
  - This is minor, but it adds visual noise and makes the message block harder to scan.
- Suggested simplification:
  - Compute `runtime_name = _runtime_display_name(runtime_target)` once near function entry and reuse.

#### LOW: Evidence-path emission in `skills_proof` mutates proof payload after assignment
- Evidence: `Infrastructure/scripts/lib/ask/commands/skills_impl.py:1318`, `Infrastructure/scripts/lib/ask/commands/skills_impl.py:1319`
- Why this is unnecessary complexity:
  - `runtime_evidence` is stored in `result.data`, then also injected into `proof` in-place.
  - This is functionally fine, but mixes “raw proof result” with “presentation/output augmentation” and makes reasoning about payload ownership less obvious.
- Suggested simplification:
  - Build a shallow merged output object for `result.data["proof"]` rather than mutating the original proof object, or keep `runtime_evidence` only at top-level output and leave `proof` untouched.

### Non-Findings (Important)
- No blocking simplicity issues were found that should stop merge.
- The current implementation correctly prioritizes explicit evidence durability over minimal LOC, which is appropriate for this governance surface.
- Artifact outputs in `.harness/evidence/runtime-proof/context7/codex/` are coherent and contract-aligned for the blocked-runtime scenario.

### Residual Risks
- The main risk is schema drift from duplicated literal structures, not runtime correctness.
- Broad test suite execution remains partially blocked by pre-existing local dependency drift (`ModuleNotFoundError: yaml`), so only scoped proof-path confidence is demonstrated in this lane.

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-006/simplify-reviewer.md

