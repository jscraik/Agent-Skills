## Simplification Analysis

### Core Purpose
Ensure `skills proof --runtime-target <value>` routes runtime-target validation through the runtime adapter layer so failures emit structured proof-plane JSON (`command-handle-proof.v2` + `skill-runtime-failure.v1`) instead of argparse-only choice errors.

### Findings (Severity-Ordered)

1. INFO — Implementation path is already minimal and correctly scoped  
   - Evidence: `Infrastructure/bin/ask:148` removes argparse `choices` and keeps argument surface unchanged.  
   - Why this is simple: one-line boundary move pushes validation to the deeper runtime proof layer without adding new flags, wrappers, or compatibility shims.  
   - Remediation: none required.

2. LOW — Governance artifacts are heavy for this slice, but not a PU-001 code complexity regression  
   - Evidence: `docs/goals/jsc-364-agent-skills-codex-runtime-proof-plane/state.yaml:94` onward introduces broad multi-slice task scaffolding; `.harness/plan/2026-05-24-jsc-364-agent-skills-codex-runtime-proof-plane-governed-implementation-prompt.md:198` onward defines an extensive lifecycle.  
   - Why this matters: these files increase process surface area and review load, but they do not increase runtime/CLI complexity for PU-001 itself.  
   - Remediation: if governance overhead becomes recurring drag, trim lifecycle text in a dedicated governance cleanup task, not in this implementation slice.

### YAGNI Review
- No YAGNI violation found in tracked source change.
- No extra abstraction, helper layer, or speculative extension introduced in `Infrastructure/bin/ask`.

### Residual Risks
- Error discoverability shifts from argparse choice validation to runtime adapter output; this is intentional for proof-plane contracts, but future maintainers should preserve this boundary and avoid reintroducing parser-level choice gating.

### Decision
- Slice status from simplify gate: **can proceed**.
- Blocking findings: **none**.

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-001/simplify-reviewer.md
