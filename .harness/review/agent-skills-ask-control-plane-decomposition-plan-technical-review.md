# Agent Skills Ask Control Plane Decomposition Plan Technical Review

## Findings

No unresolved plan-structure loopholes remain against `.harness/plan/agent-skills-ask-control-plane-decomposition-plan.md` after the hardening loop on `2026-05-08`.

The plan is now safe as a bounded execution contract, but not ready for code movement. Focused tests surfaced live validation blockers that must be resolved or explicitly classified before `PLAN-ASK-003` starts.

### Resolved During Hardening: Spec/plan drift guard

Severity before fix: high.

Evidence before fix:

- The plan's `Source Drift Handling` section treated the spec as stale even though the spec now contains the canonical project ID, milestone, labels, and `SA-ASK-014`/`SA-ASK-015`.
- The spec blackboard still used `Ask Control Plane Decomposition` as a milestone name instead of preserving it as the HE slice name.

Fix applied:

- `.harness/plan/agent-skills-ask-control-plane-decomposition-plan.md` now states that the spec and plan are reconciled as of `2026-05-08` and uses `SA-ASK-001` through `SA-ASK-015`.
- `.harness/specs/agent-skills-ask-control-plane-decomposition-spec.md` now keeps `Command surface and ask reliability` as the Linear milestone and `Ask Control Plane Decomposition` as the HE slice.

### Resolved During Hardening: Non-deterministic sync baseline

Severity before fix: high.

Evidence before fix:

- Required baseline and parity commands used `./bin/ask skills sync --scope workspace --dry-run --json`.
- `sync_skills` honors `SYNC_SKILLS_PROJECTION_MODE` when `--projection` is omitted, so before/after comparison could drift with the caller environment.

Fix applied:

- Required baseline, parity, and final validation now pin `./bin/ask skills sync --scope workspace --projection rooted --dry-run --json`.

### Resolved During Hardening: Temporary command coupling escape hatch

Severity before fix: medium.

Evidence before fix:

- The plan allowed `services/plugin_cache.py` to import from `ask.commands.plugins` temporarily if documented in the eval artifact.

Fix applied:

- The final `JSC-286` diff must not leave `ask.services.plugin_cache` importing from `ask.commands.*`.
- If neutral helper extraction cannot stay bounded to shared marketplace/copy/materialization helpers, `JSC-286` must be marked blocked rather than shipping hidden command coupling.

### Resolved During Hardening: Conceptual rollback and ADR vocabulary widening

Severity before fix: medium.

Fix applied:

- `PLAN-ASK-003` now requires pre-extraction `git status`/`git diff` evidence, bounded file scope, targeted rollback, and post-rollback baseline validation.
- `JSC-287` now keeps proof vocabulary changes ADR-local; global `UBIQUITOUS_LANGUAGE.md` changes require a separate artifact-hygiene issue.

## Review Scope

Reviewed artifact:

- `.harness/plan/agent-skills-ask-control-plane-decomposition-plan.md`

Primary evidence:

- `.harness/specs/agent-skills-ask-control-plane-decomposition-spec.md`
- `.harness/linear/agent-skills-linear-plan.md`
- `.harness/refactors/ask-control-plane-decomposition.md`
- `.harness/refactors/proof-driven-skill-promotion.md`
- `.harness/core/architecture-invariants.md`
- `.harness/core/execution-invariants.md`
- `.harness/core/routing-invariants.md`
- `.harness/core/moat-invariants.md`
- `Infrastructure/scripts/lib/ask/commands/skills.py`
- live Linear project, issue, and label queries on `2026-05-08`

Review question:

Does the deepened plan give a future `he-work` agent enough precise, bounded, reversible sequencing to implement the first Ask Control Plane extraction without widening scope or corrupting Linear traceability?

## Verdict

Status: approved for `PLAN-ASK-001` and `PLAN-ASK-002`; blocked before `PLAN-ASK-003` code movement.

The plan is stronger than the previous planning state in five important ways:

- It uses live Linear as the tracker authority and explicitly preserves canonical project identity.
- It keeps spec, plan, and live Linear tracker identity reconciled instead of relying on stale override rules.
- It turns the implementation into five ordered units with clear rollback gates, not a general refactor essay.
- It pins projection mode for sync baseline/parity commands.
- It removes the temporary command-coupling loophole from the service extraction.

## Technical Adequacy Checks

| Check | Result | Evidence |
|---|---|---|
| Linear tracker identity is explicit | Pass | Plan frontmatter and `Linear Work Item Contract` name canonical project `791c2f12-5ffb-4644-8421-f4216ac6d805`. |
| Duplicate project handling is explicit | Pass | `Linear Delta Capture` marks `e6ad5ea3-28b0-4b07-b2e0-594ec1b9242f` as `duplicate_or_superseded`. |
| Scope is bounded | Pass | Plan excludes catalog/projection extraction, proof enforcement, routing/improvement extraction, tool-resolution extraction, marketplace schema changes, and new Linear objects. |
| Execution order is safe | Pass | `PLAN-ASK-001` baseline precedes `PLAN-ASK-002` mapping, which gates `PLAN-ASK-003` extraction. |
| JSC-286 is properly blocked | Pass | Plan states `JSC-286` must not start until `JSC-285` evidence exists. |
| Plugin cache service risk is named | Pass | Plan includes a helper-coupling rule for `ask.commands.plugins` imports and forbids thin wrapper extraction. |
| Public command contract is protected | Pass | Plan preserves `./bin/ask`, `skills sync --scope workspace --projection rooted --dry-run --json`, JSON/robot output, plugin cache fields, and log strings. |
| Known `repo doctor` failure is classified | Pass | Plan treats `catalog_parity` `count_mismatch` as a known blocker class that must not worsen. |
| Eval closure is mandatory | Pass | Plan requires `.harness/evals/agent-skills-ask-control-plane-decomposition-eval.md` before `JSC-284` closure. |
| Proof ADR is bounded | Pass | Plan allows ADR terms only and forbids proof enforcement in this slice. |

## Migration Risk Review

| Risk | Severity | Review assessment | Required mitigation in plan |
|---|---|---|---|
| Service extraction becomes line-count theater | High | Addressed. | `PLAN-ASK-003` forbids thin pass-through wrapper behavior and requires service-owned cache logic. |
| Command-to-command coupling moves into service | High | Addressed. | Helper-coupling rule requires neutral helper movement or blocks `JSC-286`; final service diff must not import `ask.commands.*`. |
| Public JSON output drifts | High | Addressed. | Baseline and focused parity commands preserve dry-run fields and log strings. |
| `repo doctor` failure obscures regression | Medium | Addressed. | Plan requires failure-class comparison and prevents misattributing existing `catalog_parity` drift. |
| Proof ADR expands into enforcement | Medium | Addressed. | `PLAN-ASK-004` explicitly forbids selection-policy, command behavior, and promotion-gate changes. |
| Stale spec metadata confuses future agents | Low | Addressed. | Spec and plan metadata are reconciled; future drift becomes a blocker before code movement. |
| Implicit projection mode corrupts parity comparison | High | Addressed. | Baseline, focused parity, and final validation commands pin `--projection rooted`. |

## He-Work Readiness

Approved next execution path:

1. Run `PLAN-ASK-001`.
2. Complete `PLAN-ASK-002` and update the eval artifact with the responsibility map.
3. Resolve or explicitly classify the live focused-test blockers.
4. Only then start `PLAN-ASK-003`.
5. Run `PLAN-ASK-004` in parallel after tracker/baseline verification.
6. Close through `PLAN-ASK-005` only when the eval artifact exists and validation evidence is recorded.

Do not start:

- catalog/projection extraction;
- proof enforcement;
- runtime visibility changes;
- command-handle semantics changes;
- new Linear tracker creation.
- plugin-cache service extraction while the two focused tests are red.

## Validation Run During Review

Commands run:

- `./bin/ask skills resolve he-plan --json` -> pass; resolved `Plugins/harness-engineering/skills/he-plan/SKILL.md`.
- `./bin/ask skills resolve verification-before-completion --json` -> pass; resolved `Skills/agent-ops/verification-before-completion/SKILL.md`.
- `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/plan/agent-skills-ask-control-plane-decomposition-plan.md` -> pass after hardening.
- `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/specs/agent-skills-ask-control-plane-decomposition-spec.md` -> pass after hardening.
- `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json` -> pass after hardening; `errors=0 warnings=0`.
- `python3 -m pytest Infrastructure/tests/test_local_plugin_picker_surface.py -q` -> fail after hardening; `harness-engineering first-level plugin picker surface drifted` because `he-phase-heartbeat` is present but not in the expected first-level set.
- `python3 -m pytest Infrastructure/tests/test_ask_skills_sync_security.py -q` -> fail after hardening; `TestAskSkillsSyncSecurity.test_sync_skills_user_scope_replaces_local_plugin_mirror_copies` cannot find the expected mirrored `he-heartbeat/SKILL.md` after user-scope sync.

Live checks run:

- Linear project query for `agent-skills` -> pass; canonical project active, duplicate project canceled.
- Linear issue query for canonical project `791c2f12-5ffb-4644-8421-f4216ac6d805` -> pass; `JSC-284`, `JSC-285`, `JSC-286`, and `JSC-287` present in current slice.
- Linear issue query for duplicate project `e6ad5ea3-28b0-4b07-b2e0-594ec1b9242f` -> pass; no active issues.
- Linear issue-label query for team `JSC` -> pass; reusable labels available and current mapping remains valid.

## Review Conclusion

The plan is structurally ready after the hardening loop. It is concrete enough for implementation planning, conservative enough for a migration-risk command-plane refactor, deterministic about projection mode, and explicit that spec/plan/live Linear drift blocks code movement.

Code movement is not currently approved because focused validation is red. The next agent should first resolve or explicitly classify the two live validation blockers recorded in the plan.

The next agent should proceed with `PLAN-ASK-001` and `PLAN-ASK-002` against `.harness/plan/agent-skills-ask-control-plane-decomposition-plan.md`, not against the spec alone.
