# Sub-Agent Map

Read when: choosing reviewer or research lanes for `ce-deepen-plan`, especially when running `max-coverage`.

## Purpose
Map plan weak spots to deterministic specialist lanes so the split upstream `document-review` behavior is preserved without uncontrolled fan-out.

## Selection contract
1. Start with baseline grounding lanes.
2. Add only lanes that match the weak sections selected in Phase 1.
3. Keep the smallest set that materially improves confidence.
4. Use bounded parallel where available; otherwise run the same lanes serially.

## Baseline grounding lanes
Always include:
- `repo-research-analyst`
- `learnings-researcher`

## Plan-deepening reviewer lanes
Add by weak section signal:
- sequencing or verification ambiguity: `feasibility-reviewer`
- contradictions, drift, or broken narrative flow: `coherence-reviewer`
- scope inflation or tiering confusion: `scope-guardian-reviewer`
- challengeable product assumptions: `product-lens-reviewer`
- UI flow or interaction-heavy plan units: `design-lens-reviewer`
- auth/authz, trust boundaries, or secrets handling: `security-lens-reviewer`
- partial-state, retries, degradation, or failure handling: `reliability-reviewer`
- architecture-heavy boundary decisions: `architecture-strategist`
- public/downstream API contract impact: `api-contract-reviewer`
- persistence correctness or integrity risk: `data-integrity-guardian`
- migration-specific correctness risk: `data-migration-expert`
- rollout, rollback, and production verification depth: `deployment-verification-agent`

## Research lanes
Add only when needed:
- framework semantics or version-sensitive behavior: `framework-docs-researcher`
- cross-repo or community best-practices evidence: `best-practices-researcher`

## Max-coverage extension
For explicit exhaustive mode, optionally add:
- `adversarial-document-reviewer` for assumption stress-testing

## Execution order
1. baseline grounding lanes
2. targeted reviewer lanes by weak section
3. optional research lanes
4. max-coverage extension lanes (only when explicitly selected)
