# Final Architecture Review — JSC-351 PU011

## Findings (severity-ranked)

No actionable findings.

## Architecture overview

- Command-surface generation remains rooted-manifest driven, with compatibility alias projection layered on top of canonical handles ([Infrastructure/scripts/lifecycle-and-sync/command_surface.py:482](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lifecycle-and-sync/command_surface.py:482), [Infrastructure/scripts/lifecycle-and-sync/command_surface.py:514](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lifecycle-and-sync/command_surface.py:514)).
- First-level system bridge suppression is scoped to generated command-handle emission and does not alter canonical handle resolution, preserving ownership boundaries between rooted manifests and bridge compatibility lanes ([Infrastructure/scripts/lifecycle-and-sync/command_surface.py:137](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lifecycle-and-sync/command_surface.py:137), [Infrastructure/scripts/lifecycle-and-sync/command_surface.py:212](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lifecycle-and-sync/command_surface.py:212)).

## Change assessment

- Folded compatibility aliases are restored through a single projection function, while intentionally hidden aliases remain excluded through an explicit deny set ([Infrastructure/scripts/lifecycle-and-sync/command_surface.py:42](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lifecycle-and-sync/command_surface.py:42), [Infrastructure/scripts/lifecycle-and-sync/command_surface.py:50](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lifecycle-and-sync/command_surface.py:50), [Infrastructure/scripts/lifecycle-and-sync/command_surface.py:175](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lifecycle-and-sync/command_surface.py:175)).
- Rooted sync security tests now cover symlink, directory, and file-shaped first-level bridge artifacts and assert pruning semantics, which closes the previously leaky runtime projection edge ([Infrastructure/tests/test_ask_skills_sync_security.py:462](/Users/jamiecraik/dev/agent-skills/Infrastructure/tests/test_ask_skills_sync_security.py:462), [Infrastructure/tests/test_ask_skills_sync_security.py:487](/Users/jamiecraik/dev/agent-skills/Infrastructure/tests/test_ask_skills_sync_security.py:487), [Infrastructure/tests/test_ask_skills_sync_security.py:518](/Users/jamiecraik/dev/agent-skills/Infrastructure/tests/test_ask_skills_sync_security.py:518)).

## Compliance check

- Component boundary integrity: upheld. Canonical handles are still built from manifest report; bridge-specific pruning is additive and localized ([Infrastructure/scripts/lifecycle-and-sync/command_surface.py:485](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lifecycle-and-sync/command_surface.py:485), [Infrastructure/scripts/lifecycle-and-sync/command_surface.py:496](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lifecycle-and-sync/command_surface.py:496)).
- API/contract stability: upheld. Committed command-surface projection parity test remains in place, with rooted source as the contract ([Infrastructure/tests/test_command_surface_handles.py:703](/Users/jamiecraik/dev/agent-skills/Infrastructure/tests/test_command_surface_handles.py:703)).
- Pattern consistency: upheld. Generated command-handle count and rooted provenance in committed surface align with expected projection mode ([.skillsets/command-surface.json:2](/Users/jamiecraik/dev/agent-skills/.skillsets/command-surface.json:2), [.skillsets/command-surface.json:3](/Users/jamiecraik/dev/agent-skills/.skillsets/command-surface.json:3), [.skillsets/command-surface.json:4](/Users/jamiecraik/dev/agent-skills/.skillsets/command-surface.json:4)).

## Risk analysis

- Low residual risk: alias policy is encoded across both mapping and hidden-deny lists; future drift is possible if one list changes without corresponding tests.
- Current mitigation is acceptable for this slice because committed projection parity and explicit alias expectations are test-covered, including exclusion of `he-phase-heartbeat` from visible handles ([Infrastructure/tests/test_command_surface_handles.py:65](/Users/jamiecraik/dev/agent-skills/Infrastructure/tests/test_command_surface_handles.py:65), [Infrastructure/tests/test_command_surface_handles.py:76](/Users/jamiecraik/dev/agent-skills/Infrastructure/tests/test_command_surface_handles.py:76)).

## Recommendations

1. Keep alias restore/hide policy centralized in one policy surface as a follow-up refactor only if churn increases; no blocker for PU011 closeout.
2. Preserve the rooted projection parity test as a required gate for future command-surface changes.

WROTE: artifacts/reviews/jsc-351-pu011/final-architecture.md

