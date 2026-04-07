# Sub-Agent Map

Read when: choosing reviewer or research lanes for `ce-deepen-spec`, especially when running `max-coverage`.

## Purpose
Map spec weak spots to deterministic specialist lanes so the split upstream `document-review` behavior is preserved without uncontrolled fan-out.

## Selection contract
1. Start with baseline contract-grounding lanes.
2. Add only lanes that match the weak sections selected in Phase 1.
3. Keep the smallest lane set that materially improves contract confidence.
4. Use bounded parallel where available; otherwise run the same lanes serially.

## Baseline contract-grounding lanes
Always include:
- `repo-research-analyst`
- `learnings-researcher`
- `spec-flow-analyzer`

## Spec-deepening reviewer lanes
Add by weak section signal:
- boundary ownership or architecture contracts: `architecture-strategist`
- contradictions, drift, or broken contract narrative: `coherence-reviewer`
- scope growth and non-goal erosion: `scope-guardian-reviewer`
- product requirement fit and outcome clarity: `product-lens-reviewer`
- UI contract, interaction states, and VAC quality: `design-lens-reviewer`
- auth/authz, trust boundaries, and abuse gaps: `security-lens-reviewer`
- failure model, retries, degradation, and partial-state hazards: `reliability-reviewer`
- public/downstream API contract impact: `api-contract-reviewer`
- data constraints, migrations, and persistence safety: `data-integrity-guardian` or `data-migration-expert`
- rollout and production verification expectations: `deployment-verification-agent`

## Research lanes
Add only when needed:
- framework semantics or version-sensitive behavior: `framework-docs-researcher`
- cross-repo or community best-practices evidence: `best-practices-researcher`

## Max-coverage extension
For explicit exhaustive mode, optionally add:
- `adversarial-document-reviewer` for assumption stress-testing

## Execution order
1. baseline contract-grounding lanes
2. targeted reviewer lanes by weak section
3. optional research lanes
4. max-coverage extension lanes (only when explicitly selected)
