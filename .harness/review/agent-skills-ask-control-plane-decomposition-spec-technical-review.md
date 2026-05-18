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
- `.harness/core/moat-invariants.md`
- `Infrastructure/scripts/lib/ask/commands/skills.py`
- live Linear project, issue, and label queries on `2026-05-08`

Review question:

Does the deepened spec give a future agent enough precise, evidence-backed requirements to implement the first extraction safely without widening scope, preserving command-module coupling under a new name, or inheriting ambiguous Linear routing?

## Verdict

Status: approved for `he-plan` after Linear routing hygiene reconciliation.

The spec is implementation-useful. It identifies a bounded first extraction, cites live code seams, names the current plugin-cache call sites, records baseline command behavior, and adds acceptance criteria that prevent both output drift and shallow-service theater.

The tracker correction has now been applied. Current slice issues `JSC-284` through `JSC-287` are attached to canonical project `791c2f12-5ffb-4644-8421-f4216ac6d805`. Duplicate project `e6ad5ea3-28b0-4b07-b2e0-594ec1b9242f` is canceled and has no active issues.

Labels have also been reconciled by mapping to existing reusable labels rather than creating specialty labels for this slice.

## Findings

### Resolved: Duplicate Linear project identity

Evidence:

- Live Linear project query returned two `agent-skills` projects under team `JSC`.
- Older project `791c2f12-5ffb-4644-8421-f4216ac6d805` already existed with the repo-control description, `Dev Portfolio` initiative link, and labels `Developer Experience`, `Reliability`, `Governance`, and `Automation`.
- `.harness/linear/agent-skills-linear-plan.md` explicitly says not to create a new project if `agent-skills` exists.
- Follow-up Linear verification shows `JSC-284`, `JSC-285`, `JSC-286`, and `JSC-287` now attached to canonical project `791c2f12-5ffb-4644-8421-f4216ac6d805`.
- Duplicate project `e6ad5ea3-28b0-4b07-b2e0-594ec1b9242f` is canceled and has no active issues.

Impact:

- Future agents could route follow-up work into the wrong project.
- Portfolio reporting could split the repo state across two control surfaces.
- The `he-plan` stage could produce a correct implementation plan attached to the wrong durable Linear project.

Resolution:

- Canonical project is `791c2f12-5ffb-4644-8421-f4216ac6d805`.
- Duplicate project is canceled and documented as superseded.
- `JSC-284` traceability is preserved.

### Resolved: Linear label contract

Evidence:

- `JSC-284`, `JSC-285`, and `JSC-286` now have `architecture`, `Refactor`, and `Agent`.
- `JSC-287` now has `CE: Spec`, `architecture`, `Agent`, and `Policy`.
- Missing specialty labels were not created; the slice maps to existing reusable labels.

Impact:

- The tracker exists, but filtering and execution routing are weaker than the spec claims.
- The proof taxonomy ADR is under-classified, making it easier for future agents to lose the parallel decision slice.

Resolution:

- Treat `architecture`, `Refactor`, and `Agent` as the current implementation-slice labels.
- Treat `CE: Spec`, `architecture`, `Agent`, and `Policy` as the proof taxonomy ADR label set.
- Do not create `Drift-Risk`, `Agent-Native`, or `Eval` labels for this slice unless the reusable label policy changes.

### Resolved: Plugin cache extraction could preserve command-module coupling

Severity before correction: High.

Evidence:

- `Infrastructure/scripts/lib/ask/commands/skills.py:20` imports `_copy_directory_contents`, `_load_local_marketplace`, and `_materialize_first_level_skill_aliases` from `ask.commands.plugins`.
- The selected extraction moves plugin-cache behavior out of `commands/skills.py`.
- If the new service imported those helpers directly from `ask.commands.plugins` without constraint, the architecture would still couple one command module's service path to another command module.

Impact:

- A superficial extraction would reduce line count while preserving hidden command-to-command dependency.
- Future agents could mistake the service for a deep module even though key behavior remains owned by `ask.commands.plugins`.

Correction now present:

- The spec requires either moving shared helpers to a neutral module or recording a temporary `ask.commands.plugins` dependency with explicit follow-up and no import cycle.
- `SA-ASK-013` verifies the service does not preserve command-module coupling through a wrapper.

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
| Linear issue traceability exists | Pass | `JSC-284`, `JSC-285`, `JSC-286`, and `JSC-287` exist and are linked in the spec. |
| Linear project identity is unambiguous | Pass | Current issues are on canonical project `791c2f12-5ffb-4644-8421-f4216ac6d805`; duplicate project is canceled. |
| Linear labels are complete | Pass | Current issues use mapped existing labels; `JSC-287` now has ADR-appropriate labels. |

## Implementation Risks

| Risk | Severity | Why it matters | Required mitigation |
|---|---|---|---|
| Duplicate Linear project splits tracker of record | Resolved | The implementation could have been tracked under a non-canonical repo project. | Keep future work on canonical project `791c2f12-5ffb-4644-8421-f4216ac6d805`; do not revive the duplicate. |
| Partial labels weaken routing and filtering | Resolved | Proof ADR and drift-risk work could disappear from intended filters. | Preserve mapped labels unless label policy is intentionally changed. |
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
| SA-ASK-013 | Required; prevents command-module coupling laundering. |
| SA-ASK-014 | Resolved; canonical project identity is now explicit and must be preserved. |
| SA-ASK-015 | Resolved; labels are mapped to existing reusable labels and must be preserved. |

## Recommended Plan Handoff

`he-plan` should verify tracker hygiene before code sequencing:

1. Linear hygiene track:
   - confirm `JSC-284` through `JSC-287` remain on canonical project `791c2f12-5ffb-4644-8421-f4216ac6d805`;
   - confirm duplicate project `e6ad5ea3-28b0-4b07-b2e0-594ec1b9242f` remains canceled;
   - confirm mapped labels remain applied.

2. Implementation track:
   - responsibility map;
   - baseline command capture;
   - plugin cache service extraction;
   - focused validation;
   - eval artifact.

3. ADR track:
   - proof taxonomy terms;
   - lifecycle states;
   - explicit statement that enforcement is out of scope for this slice.

Do not let `he-plan` add catalog/projection extraction or proof enforcement to the first implementation track.

## Validation Run During Review

Commands run during this review pass:

- `./bin/ask skills resolve he-spec --json` -> pass; resolved canonical source `Plugins/harness-engineering/skills/he-spec/SKILL.md`.
- `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/specs/agent-skills-ask-control-plane-decomposition-spec.md` -> pass.
- `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json` -> pass with `errors=0 warnings=0`.

Live checks run during this review pass:

- Linear project query for `agent-skills` -> pass; returned two projects, which is a planning blocker.
- Linear issue query for project `agent-skills` -> pass; found `JSC-284` through `JSC-287` in the current slice.
- Linear issue-label query for team `JSC` -> pass; found partial reusable label coverage but not the full intended label contract.
- Linear project update -> pass; duplicate project `e6ad5ea3-28b0-4b07-b2e0-594ec1b9242f` canceled.
- Linear issue updates -> pass; `JSC-284`, `JSC-285`, `JSC-286`, and `JSC-287` moved to canonical project `791c2f12-5ffb-4644-8421-f4216ac6d805`.
- Linear label updates -> pass; current slice issues mapped to existing reusable labels.

## Review Conclusion

The spec is now deep enough technically and operationally reconciled. Its most important technical property is still that it prevents the first refactor from pretending to solve the whole `skills.py` problem. Its most important process correction is that Linear traceability now points to the canonical repo control surface instead of a duplicate project.

`he-plan` may proceed after verifying `SA-ASK-014` and `SA-ASK-015` still hold.
