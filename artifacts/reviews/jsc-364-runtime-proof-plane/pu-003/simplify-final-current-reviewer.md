## Simplification Analysis

### Core Purpose
This change needs to keep modeled conformance truth separate from live Codex runtime parity truth, so live preview/runtime blockers are visible without incorrectly failing the model contract.

### Findings (Severity Ordered)

#### Low: avoid list materialization for a simple pass count
- Evidence: `Infrastructure/scripts/lib/ask/skills_sdk/conformance.py:475`
- Why it is unnecessary: `len([ ... ])` allocates an intermediate list just to count matches.
- Suggested simplification: use a generator expression instead.
  - Replace with: `passed_count = sum(1 for case in cases if case.get("status") == "pass")`

#### Low: remove duplicate status-source expression in summary assembly
- Evidence: `Infrastructure/scripts/lib/ask/skills_sdk/conformance.py:483-490`
- Why it is unnecessary: `status` is recomputed with the same blockers condition already captured in `model_contract_status`.
- Suggested simplification: set `summary["status"]` directly from `model_contract_status` to reduce drift risk and duplication.

### YAGNI / Over-abstraction Watch
- Evidence: `Infrastructure/scripts/lib/ask/skills_sdk/conformance.py:58-71`
- Note: `_model_status`, `_live_status`, and `_blocked_runtime_status` add small helper indirection for fixed one-liner dict shapes. This is acceptable now because these payloads are used repeatedly, but avoid adding more wrapper layers unless payload variation actually grows.

### Residual Risks
- Live runtime parity currently depends on `preview_limitations` shape conventions; malformed entries are ignored safely, but future producer drift could silently reduce blocker visibility unless fixture coverage for additional malformed patterns is added.
- `blocked_runtime.status = "not_applicable"` for no blockers is semantically clear, but downstream consumers must not interpret it as "live parity succeeded."

### Final Verdict
No blocking simplicity issues remain for PU-003.
WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-003/simplify-final-current-reviewer.md
