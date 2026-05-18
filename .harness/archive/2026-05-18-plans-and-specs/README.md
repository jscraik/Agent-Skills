# 2026-05-18 Plans And Specs Archive

This archive keeps stale Harness Engineering plan, spec, and Linear-routing artifacts out of the active .harness/plan, .harness/specs, and .harness/linear surfaces without deleting the evidence.

## Archive Rule

Move an artifact here when it is completed, superseded, archived in Linear, or explicitly untracked/proposed with no live Linear destination. Keep artifacts in the active directories when Linear still has an open execution issue or when the file is the current source artifact for that issue.

## Linear Sync Evidence

Checked with the Linear plugin on 2026-05-18:

| Linear issue | Live status | Archive decision |
| --- | --- | --- |
| JSC-329 Harden skills doctor contract fixture for context7 | Triage | Kept active plan/spec and local Linear plan. |
| JSC-246 Build repo surface contract and agent capability control-plane golden paths | Todo | Kept active plan/spec. |
| JSC-167 Harden ask bootstrap and command discoverability | Backlog | Kept active plan/spec. |
| JSC-305 Productize HE front door and runtime contract | Todo | Kept active local Linear plan. |
| JSC-306 Add HE setup/status front door | Todo | Kept active local Linear plan through JSC-305 plan. |
| JSC-284 Decompose skills command module | Done | Archived ask-control-plane decomposition plan/spec. |
| JSC-285 Map skills command responsibilities | Done | Archived with JSC-284 decomposition source. |
| JSC-299 Repair HE trust defects before new capability | Archived in Linear | Archived HE trust defect repair plan/spec and Linear plan. |

## Archived Groups

- Conditional HE Gate Selection: untracked draft with no Linear destination.
- First-Principles Contract: proposed/uncreated Linear route, superseded by later tracked SDK and golden-path work.
- First-Principles Factory Gate Phases 1-4: old proposed/phase artifacts with no live Linear destination in this repo surface.
- HE Trust Defect Repair: local plan/spec points at JSC-299, which is archived in Linear.
- Ask Control Plane Decomposition: JSC-284/JSC-285 are completed in Linear.

## Remaining Active Surfaces

- .harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md
- .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md
- .harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md
- .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md
- .harness/plan/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-plan.md
- .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md
- .harness/linear/2026-05-11-agent-skills-he-product-front-door-runtime-contract-linear-plan.md
- .harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md
- .harness/linear/agent-skills-linear-plan.md
