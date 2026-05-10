---
schema_version: 1
artifact_id: agent-skills-ask-control-plane-decomposition-plan
artifact_type: he-plan
type: he-plan
canonical_slug: agent-skills-ask-control-plane-decomposition
title: Agent Skills Ask Control Plane Decomposition Plan
harness_stage: he-plan
status: plan_ask_005_complete_linear_resolved
date: 2026-05-08
origin: .harness/specs/agent-skills-ask-control-plane-decomposition-spec.md
risk: migration-risk
depth: bounded-execution-slice
traceability_required: true
linear_status: linear_resolved_done
linear_refresh_status: resolved_live_fetch_done
linear_issue: JSC-284
linear_issue_url: https://linear.app/jscraik/issue/JSC-284/agent-skills-decompose-skills-command-module-into-bounded-services
linear_team: JSC
linear_workspace: Jscraik
linear_project: agent-skills
linear_project_id: 791c2f12-5ffb-4644-8421-f4216ac6d805
linear_project_identity_status: resolved_canonical_project
linear_parent_initiative: Dev Portfolio
linear_milestone: Command surface and ask reliability
he_slice: Ask Control Plane Decomposition
linear_parent_issue_title: "[agent-skills] Decompose skills command module into bounded services"
linear_child_issues: JSC-285, JSC-286, JSC-287
linear_labels: architecture, Refactor, Agent
linear_label_status: resolved_mapped_to_existing_labels
selected_refactor: .harness/refactors/ask-control-plane-decomposition.md
parallel_refactor: .harness/refactors/proof-driven-skill-promotion.md
eval_artifact: .harness/evals/agent-skills-jsc-284-eval.md
---

# Agent Skills Ask Control Plane Decomposition Plan

## Mode Decision

This is the durable `he-plan` artifact for the approved current slice only.

Selected slice:

- Linear project: `agent-skills`
- Canonical project ID: `791c2f12-5ffb-4644-8421-f4216ac6d805`
- Linear milestone: `Command surface and ask reliability`
- HE slice: `Ask Control Plane Decomposition`
- Parent issue: `JSC-284`
- Child issues: `JSC-285`, `JSC-286`, `JSC-287`
- Selected refactor: `.harness/refactors/ask-control-plane-decomposition.md`
- Parallel decision slice: proof taxonomy ADR from `.harness/refactors/proof-driven-skill-promotion.md`

This plan does not activate later refactor phases. Catalog/projection extraction, proof enforcement, routing/improvement extraction, and tool-resolution extraction remain out of scope.

## Linear Work Item Contract

| Field | Value |
|---|---|
| Linear issue | `JSC-284` |
| URL | https://linear.app/jscraik/issue/JSC-284/agent-skills-decompose-skills-command-module-into-bounded-services |
| Team | `JSC` |
| Workspace | `Jscraik` |
| Project | `agent-skills` |
| Project ID | `791c2f12-5ffb-4644-8421-f4216ac6d805` |
| Project identity status | Resolved to canonical existing repo project; duplicate project canceled |
| Milestone | `Command surface and ask reliability` |
| HE slice | `Ask Control Plane Decomposition` |
| Parent initiative | `Dev Portfolio` |
| Priority | `1` |
| Parent issue | `JSC-284` |
| Child issues | `JSC-285`, `JSC-286`, `JSC-287` |
| Labels | `JSC-284`, `JSC-285`, `JSC-286`: `architecture`, `Agent`, `Refactor`; `JSC-287`: `CE: Spec`, `architecture`, `Agent`, `Policy` |
| Execution route | Agent-assisted; human-review required for public command contract changes |
| Blocked by | None |
| Blocks | Proof-driven promotion enforcement; later agent-first routing changes |

## Linear Delta Capture

Captured: `2026-05-08`

Live Linear state checked:

- `agent-skills` project query under team `JSC`
- issue query for canonical project `791c2f12-5ffb-4644-8421-f4216ac6d805`
- issue query for duplicate project `e6ad5ea3-28b0-4b07-b2e0-594ec1b9242f`
- issue-label query for team `JSC`

| Object | Live state | Classification | Plan handling |
|---|---|---|---|
| Canonical project | `791c2f12-5ffb-4644-8421-f4216ac6d805`, `agent-skills`, `In Progress`, under `Dev Portfolio` | `already_covered` | Use as the only repo-specific Linear destination. |
| Duplicate project | `e6ad5ea3-28b0-4b07-b2e0-594ec1b9242f`, `Canceled`, no active issues | `duplicate_or_superseded` | Do not revive or attach work. |
| Milestone | `Command surface and ask reliability` | `already_covered` | Use as Linear milestone; keep `Ask Control Plane Decomposition` as HE slice name, not a new milestone. |
| JSC-284 | Parent issue in canonical project, Done, completed `2026-05-08T01:29:39.211Z`, priority 1, labels `architecture`, `Agent`, `Refactor` | `resolved_done` | Parent tracker for this plan; closure proof comment `a54b9452-af8c-4498-bbba-ed61f92bd773` posted before status mutation. |
| JSC-285 | Child issue in canonical project, Done, completed `2026-05-08T01:29:28.358Z`, priority 1, labels `architecture`, `Agent`, `Refactor` | `resolved_done` | Phase 1 execution issue. |
| JSC-286 | Child issue in canonical project, Done, completed `2026-05-08T01:29:34.009Z`, priority 2, labels `architecture`, `Agent`, `Refactor` | `resolved_done` | Phase 2 execution issue; completed after Phase 1 evidence. |
| JSC-287 | Child issue in canonical project, Done, completed `2026-05-08T01:29:38.858Z`, priority 1, labels `CE: Spec`, `architecture`, `Agent`, `Policy` | `resolved_done` | Parallel ADR-only issue. |
| Label contract | Existing reusable labels are available; no specialty labels required for this slice | `resolved_mapped_to_existing_labels` | Preserve mapped labels; do not create `Drift-Risk`, `Agent-Native`, or `Eval` labels here. |

Structured status:

```yaml
schema_version: 1
linear_delta_status: resolved_live_fetch_done
current_slice_status: plan_ask_005_complete_linear_resolved
label_status: resolved_mapped_to_existing_labels
next_slice:
  type: closure_review
  linear_issue: JSC-284
  reason: Local Ask Control Plane Decomposition evidence is complete through PLAN-ASK-005; live Linear refresh was reverified with issue fetches and JSC-284 through JSC-287 are Done.
updated_artifacts:
  - .harness/plan/agent-skills-ask-control-plane-decomposition-plan.md
```

## Source Drift Handling

The checked-in spec and this plan are reconciled as of `2026-05-08`.

Current reconciled fields:

- canonical Linear project ID: `791c2f12-5ffb-4644-8421-f4216ac6d805`
- Linear milestone: `Command surface and ask reliability`
- HE slice name: `Ask Control Plane Decomposition`
- label mapping: `architecture`, `Agent`, `Refactor` for implementation work; `CE: Spec`, `architecture`, `Agent`, `Policy` for the proof ADR
- acceptance matrix: `SA-ASK-001` through `SA-ASK-015`

Plan authority rule:

- For requirements, consume the spec's `SA-ASK-001` through `SA-ASK-015`.
- For tracker identity, labels, and milestone, verify this plan's Linear Delta Capture against live Linear before code movement.
- If the spec and live Linear diverge again, stop before code movement, record the delta, and reconcile the harness artifacts or explicitly mark the work blocked. Do not execute from stale tracker metadata.

## Live Validation Gate

Captured: `2026-05-08`

Earlier focused blockers were discovered while hardening the plan. They are now resolved in live validation evidence and no longer block code movement.

| Check | Current outcome | Why it matters | Gate decision |
|---|---|---|---|
| `python3 -m pytest Infrastructure/tests/test_local_plugin_picker_surface.py -q` | Pass: `9 passed`. The expected local plugin surface now includes intentional `he-phase-heartbeat` and `he-eval-report`; `he-eval-report` also has `agents/openai.yaml`. | The extraction must not hide plugin picker drift under a cache refactor. | Resolved. Keep this focused test green through `PLAN-ASK-003`. |
| `python3 -m pytest Infrastructure/tests/test_ask_skills_sync_security.py -q` | Pass: `25 passed`. User-scope plugin mirror behavior preserves source plugin skills. | This directly exercises local plugin mirror copy behavior adjacent to the helper functions this refactor would move. | Resolved. Keep this focused test green through `PLAN-ASK-003`. |
| `./bin/ask repo doctor --json --robot` | Pass: `blocking: false`; catalog parity, runtime budget, command handles, and projection sync pass; latest closure trace `5954fd8e-642d-4fc6-8d9b-b723cff7269e`. Repo surface remains non-blocking diagnostic debt. | Code movement must not begin from a red repo doctor caused by projection/catalog drift. | Resolved. Treat repo surface warning as diagnostic debt, not a blocker for this slice. |
| `./bin/ask skills sync --scope workspace --projection rooted --dry-run --json` | Pass after extraction and review fixes: validation status `pass`; mutation counts `219` writes, `6` deletes, `1` symlink; command surface has `95` handles; latest closure trace `ae7aa5a8-0578-4f32-9fb9-6de30ea455a7`. | This is the public dry-run contract that `PLAN-ASK-003` must preserve. | Preserved. |

Execution rule:

- `PLAN-ASK-001` and `PLAN-ASK-002` have gathered evidence and produced the responsibility map.
- `PLAN-ASK-003` implementation is complete and the end-of-phase simplify, he-fix-bugs, and he-code-review loop has completed.
- `PLAN-ASK-004` ADR exists and its end-of-phase simplify, he-fix-bugs, and he-code-review loop has completed. Do not mutate Linear or close tracker issues until live Linear can be refreshed.

## Scope

In scope:

- Produce a responsibility map for `Infrastructure/scripts/lib/ask/commands/skills.py`.
- Capture baseline command behavior before code movement.
- Extract plugin cache refresh/report/error behavior into `Infrastructure/scripts/lib/ask/services/plugin_cache.py` or an equivalent internal service path that matches repo conventions.
- Preserve public `./bin/ask skills ...` command behavior.
- Preserve observed plugin cache dry-run fields and log strings.
- Record implementation evidence in `.harness/evals/agent-skills-jsc-284-eval.md`.
- Write the proof taxonomy ADR in parallel as a decision-only artifact.
- Preserve the resolved validation gate before starting and closing `PLAN-ASK-003`.

Out of scope:

- Catalog/projection service extraction.
- Proof command behavior changes.
- Proof enforcement or trusted/default-visible gates.
- Routing/improvement service extraction.
- Tool-resolution service extraction.
- Marketplace schema changes.
- Cache root layout changes.
- New Linear objects.
- Spec metadata cleanup unless drift reappears during execution.

## Source Evidence

| Evidence | Path or source | Why it matters |
|---|---|---|
| Approved spec | `.harness/specs/agent-skills-ask-control-plane-decomposition-spec.md` | Defines original SA-ASK acceptance IDs and plugin-cache seam requirements. |
| Linear execution snapshot | `.harness/linear/agent-skills-linear-plan.md` | Defines current slice queue and records the prior Linear object creation flow. |
| Live Linear query | Linear project/issue/label query on `2026-05-08` | Confirms canonical project, duplicate cancellation, current issue set, and label mapping. |
| Main refactor program | `.harness/refactors/ask-control-plane-decomposition.md` | Defines staged service extraction path and rollback posture. |
| Parallel proof refactor | `.harness/refactors/proof-driven-skill-promotion.md` | Allows only the proof taxonomy ADR in this slice. |
| Technical review | `.harness/review/agent-skills-ask-control-plane-decomposition-spec-technical-review.md` | Approves planning after Linear hygiene and flags helper-coupling risk. |
| Architecture invariants | `.harness/core/architecture-invariants.md` | Makes `./bin/ask`, source/projection separation, and shallow handles non-negotiable. |
| Execution invariants | `.harness/core/execution-invariants.md` | Requires reversible migration, machine-readable output stability, and eval-backed closure. |
| Routing invariants | `.harness/core/routing-invariants.md` | Requires deterministic, explainable routing and proof-backed promotion. |
| Moat invariants | `.harness/core/moat-invariants.md` | Protects trust in `./bin/ask`, proof taxonomy, and outcome evidence over catalog size. |
| Code seam | `Infrastructure/scripts/lib/ask/commands/skills.py` | Current 3001-line command module containing plugin cache behavior. |

## Current Code Seams

Known seams to verify before implementation:

| Current symbol or region | Current path | Planned owner | Notes |
|---|---|---|---|
| `PluginCacheRefreshReport` | `Infrastructure/scripts/lib/ask/commands/skills.py` | `Infrastructure/scripts/lib/ask/services/plugin_cache.py` | Data/report type for plugin-cache mutation, not final CLI formatting. |
| `PluginCacheRefreshError` | `Infrastructure/scripts/lib/ask/commands/skills.py` | `Infrastructure/scripts/lib/ask/services/plugin_cache.py` | Internal cache/pruning error. |
| `_prune_command_handle_skill_entries` | `Infrastructure/scripts/lib/ask/commands/skills.py` | plugin cache service | Must keep generated command-handle duplicate pruning behavior. |
| `_plugin_version` | `Infrastructure/scripts/lib/ask/commands/skills.py` | plugin cache service | Must preserve fallback and path-safety behavior. |
| `_replace_plugin_cache_copy` | `Infrastructure/scripts/lib/ask/commands/skills.py` | plugin cache service | Must preserve write/delete/log behavior. |
| `_refresh_workspace_plugin_caches` | `Infrastructure/scripts/lib/ask/commands/skills.py` | plugin cache service | Main service entrypoint candidate. |
| `sync_skills` calls | `Infrastructure/scripts/lib/ask/commands/skills.py` | command adapter remains caller | `sync_skills` may decide when cache refresh runs; service decides how cache refresh works. |
| plugin helper imports | `Infrastructure/scripts/lib/ask/commands/skills.py` imports from `ask.commands.plugins` | neutral shared helper/service | Must not launder command-to-command coupling through a shallow service. Final `JSC-286` diff must not leave `ask.services.plugin_cache` importing from `ask.commands.*`. |

Current structural observation:

- `Infrastructure/scripts/lib/ask` currently has a `commands/` directory and no `services/` directory. Implementation should create the smallest service package required for this slice.

## Implementation Units

### PLAN-ASK-001 - Verify Tracker And Baseline Preconditions

Linear mapping:

- Parent: `JSC-284`
- Supports: `JSC-285`, `JSC-286`, `JSC-287`
- Acceptance: `SA-ASK-014`, `SA-ASK-015`

Objective:

- Reconfirm the selected Linear slice and capture the current command-state baseline before any code movement.

Steps:

1. Verify `JSC-284` through `JSC-287` remain on canonical project `791c2f12-5ffb-4644-8421-f4216ac6d805`.
2. Verify duplicate project `e6ad5ea3-28b0-4b07-b2e0-594ec1b9242f` remains canceled and has no active issues.
3. Verify implementation issues keep `architecture`, `Agent`, `Refactor`; proof ADR keeps `CE: Spec`, `architecture`, `Agent`, `Policy`.
4. Run baseline command samples and record exact outcomes in `.harness/evals/agent-skills-jsc-284-eval.md`.

Baseline commands:

```bash
./bin/ask skills resolve he-spec --json
./bin/ask skills list --json
./bin/ask skills sync --scope workspace --projection rooted --dry-run --json
./bin/ask repo doctor --json --robot
```

Expected behavior:

- The first three commands should pass unless a pre-existing environment blocker is recorded.
- `repo doctor` may fail with existing `catalog_parity` `count_mismatch`; this must be classified as pre-existing and must not worsen after extraction.
- `skills sync --scope workspace --projection rooted --dry-run --json` must expose plugin-cache plan/log fields before implementation.

Validation requirements:

- Eval artifact records command, outcome, key output fields, and blocker classification.
- No source files are changed in this unit except the eval artifact if the implementer chooses to start it immediately.

Rollback conditions:

- None for Linear verification.
- If baseline commands cannot run, stop before code movement and classify the blocker.

Can run in parallel: no.

Agent-safe: yes.

Human review required: no.

### PLAN-ASK-002 - Map Responsibilities Before Moving Code

Linear mapping:

- Primary issue: `JSC-285`
- Acceptance: `SA-ASK-001`, `SA-ASK-002`, `SA-ASK-010`

Objective:

- Produce the responsibility map required to prevent a shallow or over-broad extraction.

Steps:

1. Inspect `Infrastructure/scripts/lib/ask/commands/skills.py`.
2. Assign current regions to these boundaries:
   - command adapter
   - plugin cache
   - catalog/projection
   - proof/eval
   - tool resolution
   - routing/improvement
3. Record the responsibility map in `.harness/evals/agent-skills-jsc-284-eval.md`.
4. Select plugin-cache-specific baseline assertions from the current `skills sync --scope workspace --projection rooted --dry-run --json` output.
5. Record the current `repo doctor` failure class separately from migration risk.

Minimum responsibility-map rows:

| Boundary | Required treatment |
|---|---|
| Command adapter | Remains in `commands/skills.py`; owns args, final output, exit mapping. |
| Plugin cache | Moves in this slice. |
| Catalog/projection | Does not move in this slice. |
| Proof/eval | Does not move in this slice, except ADR language in `JSC-287`. |
| Tool resolution | Does not move in this slice. |
| Routing/improvement | Does not move in this slice. |

Validation requirements:

- Eval artifact contains the map before `JSC-286` starts.
- Map names the plugin cache symbols listed in the spec.
- Map explicitly marks later phases as out of scope.

Rollback conditions:

- If the responsibility map shows plugin cache cannot be extracted without catalog/projection behavior changes, stop and update `JSC-286` as blocked rather than widening scope.

Can run in parallel: no.

Agent-safe: yes.

Human review required: no, unless the boundary map contradicts the approved spec.

### PLAN-ASK-003 - Extract Plugin Cache Service

Linear mapping:

- Primary issue: `JSC-286`
- Blocked by: `JSC-285`
- Acceptance: `SA-ASK-003`, `SA-ASK-004`, `SA-ASK-005`, `SA-ASK-006`, `SA-ASK-009`, `SA-ASK-010`, `SA-ASK-011`, `SA-ASK-012`, `SA-ASK-013`

Objective:

- Move plugin cache refresh/report/error behavior behind a real internal service without public command drift.

Preferred implementation shape:

- Create `Infrastructure/scripts/lib/ask/services/`.
- Create `Infrastructure/scripts/lib/ask/services/plugin_cache.py`.
- Move or expose these service-owned symbols:
  - `PluginCacheRefreshReport`
  - `PluginCacheRefreshError`
  - `prune_command_handle_skill_entries`
  - `plugin_version`
  - `replace_plugin_cache_copy`
  - `refresh_workspace_plugin_caches`
- Update `Infrastructure/scripts/lib/ask/commands/skills.py` to import and call the service.
- Keep `sync_skills` as workflow adapter; it may call `refresh_workspace_plugin_caches(...)` but must not know plugin cache internals.

Helper-coupling rule:

- Required: move shared plugin copy/materialization/marketplace helpers out of `ask.commands.plugins` into a neutral helper or service module when `services/plugin_cache.py` needs them.
- Final `JSC-286` diff must not leave `Infrastructure/scripts/lib/ask/services/plugin_cache.py` importing from `ask.commands.plugins` or any other `ask.commands.*` module.
- If neutral helper extraction cannot be completed without widening beyond the shared marketplace/copy/materialization helpers, stop and mark `JSC-286` blocked. Do not merge a service extraction that preserves command-to-command coupling.
- Forbidden: `services/plugin_cache.py` becomes a thin pass-through wrapper over `ask.commands.plugins`.

Implementation order:

1. Create the service package and copy the plugin-cache behavior with private names removed only where call sites are updated.
2. Rewire `commands/skills.py` to import only the new service entrypoint and types required by the adapter.
3. Keep mutable `plan`/`logs` protocol unchanged for this first slice.
4. Move only the shared helper functions required to remove command-to-command coupling.
5. Run focused parity after the service and neutral helper boundaries are both in place.

Behavior to preserve:

- `data.plan.plugin_cache_writes`
- `data.plan.writes`
- `data.plan.deletes`
- `data.logs`
- `data.plan.validation_status`
- `data.plan.mutation_counts`
- `data.plan.warnings`
- `errors`

Log strings to preserve:

- `Would replace local plugin cache: <runtime-target> <- <source>`
- `Would replace local plugin cache: <versioned-target> <- <source>`
- `Would remove stale versioned local plugin cache variant: <path>`
- `Would remove stale local plugin cache: <path>`
- `Skipped workspace plugin cache refresh: <reason>`
- `Skipped unsafe plugin cache name: <name>`
- `Skipped missing plugin cache source: <path>`

Validation requirements:

```bash
./bin/ask skills sync --scope workspace --projection rooted --dry-run --json
./bin/ask skills resolve he-spec --json
./bin/ask skills list --json
./bin/ask repo doctor --json --robot
python3 -m pytest Infrastructure/tests/test_local_plugin_picker_surface.py -q
python3 -m pytest Infrastructure/tests/test_ask_skills_sync_security.py -q
python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json
```

Additional focused test discovery:

```bash
rg -n "sync_skills|plugin_cache|skills sync|PluginCacheRefresh" Infrastructure/scripts Infrastructure/tests .harness -g "*.py" -g "*.md"
```

Known direct tests already exist and should be used before relying on smoke evidence:

- `Infrastructure/tests/test_local_plugin_picker_surface.py`
- `Infrastructure/tests/test_ask_skills_sync_security.py`

If those tests move before implementation, rediscover their replacements and record the replacement paths in the eval artifact.

Expected outcomes:

- `skills sync --scope workspace --projection rooted --dry-run --json` preserves plugin-cache fields, cache roots, and log strings.
- `repo doctor` does not introduce a new or worse failure class beyond the known `catalog_parity` `count_mismatch`.
- `commands/skills.py` becomes smaller for the touched concern and does not gain unrelated behavior.
- No catalog/projection, proof/eval, routing/improvement, or tool-resolution semantics are moved.

Rollback conditions:

- Any unexpected robot JSON drift.
- Any plugin cache root layout drift.
- Any import cycle or broader command import churn.
- Any catalog/projection behavior change caused by this slice.
- Any service that only hides command-module coupling without owning behavior.

Can run in parallel: no.

Agent-safe: assisted.

Human review required: yes for final diff, because the touched path is a public control-plane command.

### PLAN-ASK-004 - Write Proof Taxonomy ADR

Linear mapping:

- Primary issue: `JSC-287`
- Acceptance: `SA-ASK-007`

Objective:

- Define proof levels and lifecycle states without implementing enforcement.

Steps:

1. Check whether `.harness/decisions/` exists at execution time.
2. If absent, create `.harness/decisions/`.
3. Write a concise ADR for proof taxonomy and skill lifecycle states.
4. Define at least these proof levels:
   - reachability
   - structural
   - quality
   - outcome
5. Define at least these lifecycle states:
   - experimental
   - latent
   - structurally valid
   - reachable
   - outcome-proven
   - trusted
   - default-visible
   - deprecated
6. Explicitly state that enforcement is outside this slice.
7. Check terms against `UBIQUITOUS_LANGUAGE.md`.
8. Keep vocabulary changes ADR-local in this slice. If `UBIQUITOUS_LANGUAGE.md` must change, stop and open or select a separate artifact-hygiene issue; do not mutate the global language contract inside `JSC-287`.

Validation requirements:

- ADR exists and is linked from the eval artifact.
- ADR says structural audit is not outcome proof.
- ADR does not change selection policy, command behavior, or default-visible promotion gates.

Rollback conditions:

- ADR terms create more ambiguity than they remove.
- ADR starts specifying enforcement implementation.

Can run in parallel: yes, after PLAN-ASK-001.

Agent-safe: assisted.

Human review required: yes, because this is governance/domain vocabulary.

### PLAN-ASK-005 - Closure Eval And Traceability

Linear mapping:

- Parent: `JSC-284`
- Depends on: `JSC-285`, `JSC-286`, `JSC-287`
- Acceptance: `SA-ASK-008`, `SA-ASK-009`, plus all parent acceptance IDs

Objective:

- Prove that the slice is complete, reversible, and still inside the approved boundary.

Required eval artifact:

```text
.harness/evals/agent-skills-jsc-284-eval.md
```

Eval artifact must include:

- responsibility map;
- before/after command evidence;
- changed files list;
- plugin cache field/log comparison;
- `repo doctor` blocker classification;
- rollback conditions and whether any were hit;
- Linear traceability table for `JSC-284` through `JSC-287`;
- statement that later extraction phases were not started;
- validation command outcomes.

Final validation commands:

```bash
./bin/ask skills resolve he-spec --json
./bin/ask skills list --json
./bin/ask skills sync --scope workspace --projection rooted --dry-run --json
./bin/ask repo doctor --json --robot
python3 -m pytest Infrastructure/tests/test_local_plugin_picker_surface.py -q
python3 -m pytest Infrastructure/tests/test_ask_skills_sync_security.py -q
python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/specs/agent-skills-ask-control-plane-decomposition-spec.md
python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/plan/agent-skills-ask-control-plane-decomposition-plan.md
python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json
```

Do not close `JSC-284` while traceability lint fails or while spec/plan/live Linear tracker identity diverges.

Rollback conditions:

- Eval artifact is missing.
- Traceability to `JSC-284` through `JSC-287` is missing.
- Command output comparison is absent.
- Known `repo doctor` blocker changes class or worsens without explanation.

Can run in parallel: no.

Agent-safe: yes for evidence assembly; assisted for closure judgment.

Human review required: yes before closing `JSC-284`.

## Sequencing

```text
PLAN-ASK-001
  -> PLAN-ASK-002
      -> PLAN-ASK-003
          -> PLAN-ASK-005

PLAN-ASK-004 may run after PLAN-ASK-001 and in parallel with PLAN-ASK-002/003.
JSC-286 must not start until JSC-285 evidence exists.
JSC-284 must not close until JSC-285, JSC-286, JSC-287, and PLAN-ASK-005 evidence are complete.
```

## Linear / Spec / Plan / PR Traceability

| Linear issue | Source acceptance IDs | Plan units | Acceptance IDs | PR evidence |
|---|---|---|---|---|
| JSC-284 | SA-ASK-001 through SA-ASK-015 | PLAN-ASK-001, PLAN-ASK-005 | SA-ASK-001 through SA-ASK-015 | Pending he-work |
| JSC-285 | SA-ASK-001, SA-ASK-002, SA-ASK-010 | PLAN-ASK-002 | SA-ASK-001, SA-ASK-002, SA-ASK-010 | Pending he-work |
| JSC-286 | SA-ASK-003, SA-ASK-004, SA-ASK-005, SA-ASK-006, SA-ASK-009, SA-ASK-010, SA-ASK-011, SA-ASK-012, SA-ASK-013 | PLAN-ASK-003 | SA-ASK-003, SA-ASK-004, SA-ASK-005, SA-ASK-006, SA-ASK-009, SA-ASK-010, SA-ASK-011, SA-ASK-012, SA-ASK-013 | Pending he-work |
| JSC-287 | SA-ASK-007 | PLAN-ASK-004 | SA-ASK-007 | Pending he-work |

## Validation Strategy

Focused validation comes first because the first extraction is behavior-preserving. Broad validation is useful only after plugin-cache behavior is proven stable.

Required validation tiers:

| Tier | Commands | Required for |
|---|---|---|
| Baseline | `./bin/ask skills resolve he-spec --json`; `./bin/ask skills list --json`; `./bin/ask skills sync --scope workspace --projection rooted --dry-run --json`; `./bin/ask repo doctor --json --robot` | PLAN-ASK-001, PLAN-ASK-002 |
| Focused parity | `./bin/ask skills sync --scope workspace --projection rooted --dry-run --json` before/after field-level comparison | PLAN-ASK-003 |
| Focused tests | `python3 -m pytest Infrastructure/tests/test_local_plugin_picker_surface.py -q`; `python3 -m pytest Infrastructure/tests/test_ask_skills_sync_security.py -q` | PLAN-ASK-003, PLAN-ASK-005 |
| Traceability | `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/specs/agent-skills-ask-control-plane-decomposition-spec.md`; same command against this plan | PLAN-ASK-005 |
| Docs policy | `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json` | Any docs/harness artifact change |

Known blocker classification:

- Earlier `catalog_parity` and runtime-budget blockers are resolved as of the current baseline.
- `repo doctor` still reports repo surface diagnostic debt, but it is non-blocking and not a plugin-cache extraction failure unless the failure class worsens or becomes caused by touched files.

## Rollback Strategy

Rollback the smallest unit that introduced drift:

- If baseline capture is incomplete, stop before implementation.
- If the responsibility map reveals incompatible boundaries, keep the map and mark `JSC-286` blocked.
- If plugin cache extraction changes public behavior, revert `PLAN-ASK-003` only.
- If proof ADR terms are wrong, revise or revert the ADR without touching command code.
- If eval evidence is incomplete, keep implementation open and do not close `JSC-284`.

Operational rollback mechanics for `PLAN-ASK-003`:

1. Before moving code, record `git status --short` and `git diff -- Infrastructure/scripts/lib/ask/commands/skills.py Infrastructure/scripts/lib/ask/commands/plugins.py Infrastructure/scripts/lib/ask/services Infrastructure/tests` in the eval artifact.
2. Keep the extraction diff limited to plugin-cache service files, the neutral helper files required to remove command-to-command coupling, `commands/skills.py`, `commands/plugins.py`, focused tests, and the eval artifact.
3. If rollback is needed, revert only the files changed by `PLAN-ASK-003`, preserving unrelated user changes in the worktree.
4. After rollback, rerun the baseline tier and record pass/fail/blocker outcomes.

Do not rollback the Linear hygiene correction: canonical project identity remains `791c2f12-5ffb-4644-8421-f4216ac6d805`; duplicate project remains canceled.

## Human And Agent Routing

| Work | Route | Human review |
|---|---|---|
| Tracker verification | Agent-safe | No |
| Responsibility map | Agent-safe | Only if boundaries are disputed |
| Baseline command capture | Agent-safe | No |
| Plugin cache service extraction | Agent-assisted | Yes |
| Proof taxonomy ADR | Agent-assisted | Yes |
| Eval artifact assembly | Agent-safe | Human review before parent closure |

## Anti-Regression Constraints

- Do not change public command names.
- Do not change generated command-handle semantics.
- Do not treat runtime projections as source.
- Do not change plugin cache root layout.
- Do not reword plugin cache dry-run log strings in this slice.
- Do not move catalog/projection behavior.
- Do not move proof/eval behavior except ADR language.
- Do not implement proof enforcement.
- Do not add unrelated feature behavior to `commands/skills.py`.
- Do not leave new service modules importing from `ask.commands.*`.
- Do not create new Linear projects, milestones, labels, or issues for this slice.
- Do not close `JSC-284` without `.harness/evals/agent-skills-jsc-284-eval.md`.

## Open Execution Unknowns

| Unknown | Handling |
|---|---|
| Whether a direct `skills sync` Python test already exists | Known direct tests exist in `Infrastructure/tests/test_local_plugin_picker_surface.py` and `Infrastructure/tests/test_ask_skills_sync_security.py`; rediscover replacements only if these files move. |
| Whether plugin helpers can be moved out of `ask.commands.plugins` without widening scope | Required for final `JSC-286` diff. If this cannot be done within the shared helper boundary, block `JSC-286` rather than shipping hidden command coupling. |
| Whether `.harness/decisions/` exists at implementation time | Create only when writing the proof taxonomy ADR. |
| Whether spec metadata drifts again at closure | Reconcile the spec/plan/live Linear mismatch or block closure; do not close parent work while traceability lint fails. |

## Completion Criteria

The plan is complete when:

- PLAN-ASK-001 through PLAN-ASK-005 are complete or explicitly blocked with evidence.
- `JSC-285` has responsibility-map and baseline evidence.
- `JSC-286` has plugin-cache service extraction evidence with preserved command behavior.
- `JSC-287` has an ADR or ready draft that defines proof taxonomy without enforcement.
- `.harness/evals/agent-skills-jsc-284-eval.md` exists and links evidence to SA-ASK IDs.
- No later refactor phase started accidentally.
- Linear tracker identity remains canonical.

## slack_policy

```yaml
notify: false
reason: Local repository planning artifact only; no Slack or external broadcast requested.
```

## blackboard_delta

```yaml
schema_version: 1
artifact_status: created
artifacts:
  - .harness/plan/agent-skills-ask-control-plane-decomposition-plan.md
selected_slice:
  linear_project: agent-skills
  linear_project_id: 791c2f12-5ffb-4644-8421-f4216ac6d805
  linear_milestone: Command surface and ask reliability
  he_slice: Ask Control Plane Decomposition
  parent_issue: JSC-284
  child_issues:
    - JSC-285
    - JSC-286
    - JSC-287
  selected_refactor: .harness/refactors/ask-control-plane-decomposition.md
linear_delta_status: resolved_live_fetch_done
current_slice_status: plan_ask_005_complete_linear_resolved
label_status: resolved_mapped_to_existing_labels
next_stage: selected_file_commit_review_if_requested
acceptance_ids:
  - SA-ASK-001
  - SA-ASK-002
  - SA-ASK-003
  - SA-ASK-004
  - SA-ASK-005
  - SA-ASK-006
  - SA-ASK-007
  - SA-ASK-008
  - SA-ASK-009
  - SA-ASK-010
  - SA-ASK-011
  - SA-ASK-012
  - SA-ASK-013
  - SA-ASK-014
  - SA-ASK-015
```
