# JSC-391 Parent V1 Acceptance Crosswalk

Schema: jsc-391-parent-v1-crosswalk.v1
Phase: PU-006
Created: 2026-06-04T09:09:42Z
Parent spec: .harness/specs/2026-06-03-skills-sdk-v1-product-spec.md
JSC-391 plan: .harness/plan/2026-06-03-jsc-391-agent-first-skills-sdk-scaffold-refactor-plan.md

## Decision Boundary

This crosswalk maps parent V1 SA-024 through SA-029 to current JSC-391 scaffold evidence before feature implementation planning. A row is marked `satisfied` only when current artifacts and executable checks directly cover the acceptance statement. A row is marked `accepted_deferral` only when JSC-391 intentionally records a non-feature placeholder or separate follow-up with enough evidence to prevent false readiness. A row is marked `blocked_parent_acceptance` when parent acceptance still requires evidence outside the current scaffold slice.

## Crosswalk

| Parent ID | Parent Acceptance Text | Status | Evidence | Notes |
| --- | --- | --- | --- | --- |
| SA-024 | Agent-first scaffold gate is accepted before feature implementation planning. | satisfied | .harness/decisions/2026-06-03-jsc-391-skills-sdk-path-map-adr.md; Docs/reference/skills-sdk/modules.md; Infrastructure/tests/test_skills_sdk_scaffold.py; .harness/evidence/jsc-391-agent-first-skills-sdk-scaffold-refactor/receipt-comparison.json | The scaffold gate has a path-map ADR, module map, placeholders, fixtures, feature-leak tests, and post-change receipts. |
| SA-025 | Inferential, computational, and hybrid work-mode tags are accepted before implementation planning. | satisfied | Docs/reference/skills-sdk/modules.md; .harness/evidence/jsc-391-agent-first-skills-sdk-scaffold-refactor/module-ownership-map.json; Infrastructure/tests/test_skills_sdk_scaffold.py | Work-mode terms are defined in the module contract and guarded by scaffold tests. No runtime feature behavior is implied. |
| SA-026 | Sensor placement and probability/impact/detectability risk model are accepted before implementation planning. | satisfied | Docs/reference/skills-sdk/modules.md; .harness/evidence/jsc-391-agent-first-skills-sdk-scaffold-refactor/placeholders/risk.json; Infrastructure/config/schemas/skills-sdk/risk-placeholder.v1.schema.json; Infrastructure/tests/test_skills_sdk_scaffold.py | Risk vocabulary and placeholder shape are accepted for planning; risk calculation remains future feature work. |
| SA-027 | Receipt proof metadata is accepted before implementation planning. | satisfied | Docs/reference/skills-sdk/modules.md; .harness/evidence/jsc-391-agent-first-skills-sdk-scaffold-refactor/placeholders/receipts.json; Infrastructure/config/schemas/skills-sdk/receipt-placeholder.v1.schema.json; .harness/evidence/jsc-391-agent-first-skills-sdk-scaffold-refactor/post-change-receipts.json | Receipt proof metadata and redaction boundaries are represented by schema-backed placeholders and live compatibility receipts. |
| SA-028 | Module routing and progressive-disclosure contracts are accepted before implementation planning. | satisfied | .harness/evidence/jsc-391-agent-first-skills-sdk-scaffold-refactor/module-ownership-map.json; Docs/reference/skills-sdk/modules.md; Infrastructure/tests/test_skills_sdk_scaffold.py | Routing rows name owning modules, public contracts, collaborators, hidden internals, and tests consume the map. |
| SA-029 | P1/P2 adversarial review findings require computational proof, accepted deferral, or evidence-backed non-applicability. | accepted_deferral | Docs/goals/jsc-391-agent-first-skills-sdk-scaffold-refactor/state.yaml; artifacts/reviews/jsc-391-agent-first-skills-sdk-scaffold-refactor/pu-002/coordinator-summary.md | Per user scope update, agent-swarm/adversarial review is tracked as a separate follow-up lane, not a per-slice close blocker. No current P1/P2 adversarial findings are accepted as resolved by this scaffold slice. |

## Open Parent Acceptance Rows

No SA-024 through SA-028 row remains `blocked_parent_acceptance` for scaffold planning evidence. SA-029 is an `accepted_deferral` because the requested swarm review lane was explicitly split out and cannot be treated as completed by local review artifacts.

## Truth Lanes

- Local artifact truth: post-change receipts, comparison, module map, placeholders, schemas, fixtures, and tests are present in the worktree.
- Local validation truth: focused pytest and JSON/crosswalk checks must pass in PU-006 closeout.
- Runtime projection truth: repo doctor, skills prove, and changed closeout remain blocked by unchanged isolated-worktree projection/command-handle setup debt.
- PR/CI truth: not checked in PU-006.
- Linear truth: not mutated in PU-006.
- Merge readiness: not claimed.
