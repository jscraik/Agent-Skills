# Agent Skills Ask Control Plane Decomposition Spec Technical Review

## Review Scope

Reviewed artifact:

- `.harness/specs/agent-skills-ask-control-plane-decomposition-spec.md`

Primary source evidence:

- `.harness/linear/agent-skills-linear-plan.md`
- `.harness/refactors/ask-control-plane-decomposition.md`
- `.harness/refactors/proof-driven-skill-promotion.md`
- `.harness/core/architecture-invariants.md`
- `.harness/core/routing-invariants.md`
- `.harness/core/execution-invariants.md`
- `Infrastructure/scripts/lib/ask/commands/skills.py`
- `Infrastructure/scripts/lib/ask/commands/plugins.py`

Review question:

Does the deepened spec give a future agent enough precise, evidence-backed requirements to implement the first extraction safely without widening scope or preserving command-module coupling under a new name?

## Verdict

Status: approved with one resolved review correction.

The spec is now technically usable for `he-plan`. It identifies a bounded first extraction, cites live code seams, names the current plugin-cache call sites, records baseline command behavior, and adds acceptance criteria that prevent both output drift and shallow-service theater.

Linear traceability is now active through parent issue `JSC-284` and child issues `JSC-285`, `JSC-286`, and `JSC-287`.

## Findings

### Resolved: Plugin cache extraction could preserve command-module coupling

Severity: High before correction; resolved in current spec.

Evidence:

- `Infrastructure/scripts/lib/ask/commands/skills.py:20` imports `_copy_directory_contents`, `_load_local_marketplace`, and `_materialize_first_level_skill_aliases` from `ask.commands.plugins`.
- The selected extraction moves plugin-cache behavior out of `commands/skills.py`.
- If the new service imported those helpers directly from `ask.commands.plugins` without constraint, the architecture would still couple one command module's service path to another command module.

Impact:

- A superficial extraction would reduce line count while preserving hidden command-to-command dependency.
- Future agents could mistake the service for a deep module even though key behavior remains owned by `ask.commands.plugins`.
- This would violate the spec's own anti-pattern: service modules that become pass-through wrappers only.

Correction made:

- The spec now requires the implementation to either move shared helpers to a neutral module or record a temporary `ask.commands.plugins` dependency with explicit follow-up and no import cycle.
- Added acceptance ID `SA-ASK-013` to verify the service does not preserve command-module coupling through a wrapper.

## Technical Adequacy Checks

| Check | Result | Evidence |
|---|---|---|
| Selected slice is bounded | Pass | Spec limits implementation to responsibility mapping, plugin cache extraction, and proof taxonomy ADR. |
| Live code seams are concrete | Pass | Spec references `skills.py:57`, `skills.py:65`, `skills.py:2349`, `skills.py:2400`, `skills.py:2413`, `skills.py:2435`, `skills.py:2928`, and `skills.py:2978`. |
| Baseline behavior is observable | Pass | Spec requires `skills sync --scope workspace --dry-run --json`, `skills resolve`, `skills list`, and `repo doctor` baselines. |
| Existing repo blocker is separated from migration risk | Pass | Spec records current `repo doctor` blocker as catalog parity `count_mismatch` and acceptance ID `SA-ASK-010` prevents misattribution. |
| Output contract is concrete enough | Pass | Spec names dry-run fields and plugin-cache log patterns that must not drift. |
| Scope excludes later phases | Pass | Spec explicitly excludes catalog/projection extraction, proof enforcement, routing/improvement extraction, and governance compression. |
| Rollback conditions are useful | Pass | Spec blocks unexpected robot JSON drift, plugin cache regression, import churn, and accidental phase widening. |
| Linear status is honest | Pass | `linear_status: created`; parent tracker is `JSC-284`, with child issues `JSC-285`, `JSC-286`, and `JSC-287`. |

## Implementation Risks

| Risk | Severity | Why it matters | Required mitigation |
|---|---|---|---|
| Mutable `plan`/`logs` coupling makes the first service less deep than ideal | Medium | Preserving the signature lowers migration risk but keeps some workflow shape in the service boundary. | Accept for first pass; require later cleanup only after behavior parity is proven. |
| Plugin helper ownership is still unclear | High | Helpers currently live in `ask.commands.plugins`; importing them from the new service can preserve hidden coupling. | Enforce `SA-ASK-013`. |
| Existing catalog parity drift can obscure regression signal | Medium | `repo doctor` already fails, so broad validation cannot be treated as a new implementation failure by itself. | Compare blocker class before/after; require no worse or different doctor failure. |
| Dry-run output may include generated root-skill deletion noise | Low | The baseline command reports more than plugin cache behavior. | Validate plugin-cache-specific fields/logs separately from unrelated plan entries. |
| Proof taxonomy ADR could expand into enforcement work | Medium | It runs in parallel but must not deepen `skills.py`. | Keep ADR acceptance to terms/lifecycle states only; enforcement remains later milestone. |

## Acceptance ID Review

| Acceptance ID | Review result |
|---|---|
| SA-ASK-001 | Strong; requires actual responsibility map. |
| SA-ASK-002 | Strong; baseline capture is specific and pre-move. |
| SA-ASK-003 | Strong after adding `skills sync --scope workspace --dry-run --json`. |
| SA-ASK-004 | Strong; keeps command adapter role explicit. |
| SA-ASK-005 | Strong; blocks shallow wrapper extraction. |
| SA-ASK-006 | Strong; prevents projection/catalog scope creep. |
| SA-ASK-007 | Adequate; ADR remains parallel and non-enforcing. |
| SA-ASK-008 | Strong; requires eval before closure. |
| SA-ASK-009 | Strong; rollback evidence required. |
| SA-ASK-010 | Strong; handles current doctor blocker honestly. |
| SA-ASK-011 | Strong; protects cache root layout. |
| SA-ASK-012 | Strong; prevents accidental later-phase migration. |
| SA-ASK-013 | Required; added during review to prevent command-module coupling laundering. |

## Recommended Plan Handoff

`he-plan` should produce a two-track plan:

1. Implementation track:
   - responsibility map;
   - baseline command capture;
   - plugin cache service extraction;
   - focused validation;
   - eval artifact.

2. ADR track:
   - proof taxonomy terms;
   - lifecycle states;
   - explicit statement that enforcement is out of scope for this slice.

Do not let `he-plan` add catalog/projection extraction or proof enforcement to the first implementation track.

## Validation Run During Review

Commands already run during spec deepening:

- `./bin/ask skills sync --scope workspace --dry-run --json` -> pass.
- `./bin/ask repo doctor --json --robot` -> fail with existing catalog parity `count_mismatch`.

The doctor failure is not a spec defect. It is baseline evidence that the implementation eval must classify separately.

## Review Conclusion

The spec is deep enough to support safe planning. Its most important property is that it prevents the first refactor from pretending to solve the whole `skills.py` problem. It narrows execution to one service seam, requires baseline output proof, preserves command contracts, and records the current validation blocker so future agents cannot confuse ambient drift with their own regression.
