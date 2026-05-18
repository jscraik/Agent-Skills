---
schema_version: 1
artifact_id: agent-skills-ask-control-plane-decomposition-spec
artifact_type: he-spec
type: he-spec
canonical_slug: agent-skills-ask-control-plane-decomposition
title: Agent Skills Ask Control Plane Decomposition Spec
harness_stage: he-spec
status: draft
date: 2026-05-08
origin: .harness/linear/agent-skills-linear-plan.md
risk: migration-risk
depth: bounded-execution-slice
ui: false
traceability_required: true
linear_status: created
linear_issue: JSC-284
linear_issue_url: https://linear.app/jscraik/issue/JSC-284/agent-skills-decompose-skills-command-module-into-bounded-services
linear_team: JSC
linear_workspace: Jscraik
linear_project: agent-skills
linear_project_id: 791c2f12-5ffb-4644-8421-f4216ac6d805
linear_project_identity_status: resolved_canonical_project
linear_parent_initiative: Dev Portfolio
linear_milestone: Command surface and ask reliability
linear_parent_issue_title: "[agent-skills] Decompose skills command module into bounded services"
linear_labels: architecture, Refactor, Agent
linear_label_status: resolved_mapped_to_existing_labels
linear_priority: 1
selected_refactor: .harness/refactors/ask-control-plane-decomposition.md
parallel_spec_slice: proof-taxonomy-adr
---

# Agent Skills Ask Control Plane Decomposition Spec

## Mode Decision

This is a bounded HE spec for the first approved execution slice from `.harness/linear/agent-skills-linear-plan.md`.

Selected slice:

- Linear milestone: `Command surface and ask reliability`
- HE slice name: `Ask Control Plane Decomposition`
- Parent issue: `[agent-skills] Decompose skills command module into bounded services`
- Active sub-issues:
  - `[agent-skills] Map skills command responsibilities and output contracts`
  - `[agent-skills] Extract plugin cache service behind existing behavior`
  - `[agent-skills] Write proof taxonomy and lifecycle ADR`

This spec does not cover the whole refactor programme. Later extraction phases remain in `.harness/refactors/ask-control-plane-decomposition.md` until activated by Linear.

## Linear Tracker Status

`linear_status: created`

Linear objects were created after the initial `Plan only` decision was corrected for the HE Spec flow.

Created Linear objects:

```yaml
linear_status: created
team: JSC
workspace: Jscraik
project: agent-skills
project_id: 791c2f12-5ffb-4644-8421-f4216ac6d805
parent_initiative: Dev Portfolio
milestone: Command surface and ask reliability
slice_name: Ask Control Plane Decomposition
project_identity_status: resolved_canonical_project
duplicate_project_status: canceled
superseded_project_id: e6ad5ea3-28b0-4b07-b2e0-594ec1b9242f
label_status: resolved_mapped_to_existing_labels
parent_issue:
  key: JSC-284
  title: "[agent-skills] Decompose skills command module into bounded services"
  url: "https://linear.app/jscraik/issue/JSC-284/agent-skills-decompose-skills-command-module-into-bounded-services"
  priority: 1
  labels:
    - architecture
    - Refactor
    - Agent
  execution_route: Agent-assisted; human-review required for public command contract changes
  blocks:
    - Proof-driven skill promotion implementation
    - Agent-first routing changes
  blocked_by: []
sub_issues:
  - key: JSC-285
    title: "[agent-skills] Map skills command responsibilities and output contracts"
    priority: 1
    execution_route: Agent-safe
    labels:
      - architecture
      - Refactor
      - Agent
  - key: JSC-286
    title: "[agent-skills] Extract plugin cache service behind existing behavior"
    priority: 2
    execution_route: Agent-assisted
    labels:
      - architecture
      - Refactor
      - Agent
    blocked_by:
      - JSC-285
  - key: JSC-287
    title: "[agent-skills] Write proof taxonomy and lifecycle ADR"
    priority: 1
    execution_route: Agent-assisted; human-review required
    labels:
      - CE: Spec
      - architecture
      - Agent
      - Policy
```

### Live Linear Delta Capture

Captured: `2026-05-08`

Source checked:

- Linear project query for `agent-skills` under team `JSC`;
- Linear issue query for project `agent-skills`;
- Linear issue-label query for team `JSC`.

| Delta | Live evidence | Classification | Required handling |
|---|---|---|---|
| Two `agent-skills` Linear projects existed. | Current slice issues `JSC-284` through `JSC-287` were moved to canonical project `791c2f12-5ffb-4644-8421-f4216ac6d805`; duplicate project `e6ad5ea3-28b0-4b07-b2e0-594ec1b9242f` is canceled and has no active issues. | `resolved` | Keep all future repo-specific work on canonical project `791c2f12-5ffb-4644-8421-f4216ac6d805`. Do not create another `agent-skills` project. |
| Planned labels were only partially applied. | Current implementation issues now use `architecture`, `Refactor`, and `Agent`; proof taxonomy ADR uses `CE: Spec`, `architecture`, `Agent`, and `Policy`. | `resolved_mapped_to_existing_labels` | Use existing reusable labels instead of creating `Drift-Risk`, `Agent-Native`, or `Eval` for this slice. |
| Current slice remains bounded. | `JSC-284`, `JSC-285`, `JSC-286`, and `JSC-287` remain in `Triage`; priorities and parent-child links still match the intended slice. | `already_covered` | No scope expansion. Keep the spec bounded to Ask Control Plane Decomposition plus the parallel proof taxonomy ADR. |

Current-slice status:

```yaml
linear_delta_status: updated
current_slice_status: ready_for_he_plan
label_status: resolved_mapped_to_existing_labels
next_slice:
  type: parent_issue
  linear_issue: JSC-284
  reason: Current implementation scope remains the selected bounded slice and tracker hygiene has been reconciled.
```

## Linear Work Item Contract

| Field | Value |
|---|---|
| Linear issue | JSC-284 |
| URL | https://linear.app/jscraik/issue/JSC-284/agent-skills-decompose-skills-command-module-into-bounded-services |
| Team | JSC |
| Project | agent-skills |
| Project ID | 791c2f12-5ffb-4644-8421-f4216ac6d805 |
| Project identity status | Resolved to canonical existing `agent-skills` project; duplicate project canceled |
| Milestone | Command surface and ask reliability |
| HE slice | Ask Control Plane Decomposition |
| Parent initiative | Dev Portfolio |
| Priority | 1 |
| Labels | `JSC-284`, `JSC-285`, `JSC-286`: `architecture`, `Refactor`, `Agent`; `JSC-287`: `CE: Spec`, `architecture`, `Agent`, `Policy` |
| Label status | Resolved by mapping to existing reusable labels |
| Execution route | Agent-assisted; human-review required for public command contract changes |
| Child issues | JSC-285, JSC-286, JSC-287 |
| Blocks | Proof-driven skill promotion implementation; agent-first routing changes |
| Blocked by | None |

## Problem

`Infrastructure/scripts/lib/ask/commands/skills.py` is the main structural choke point for the repository's public skill control plane.

The problem is not only size. The problem is mixed responsibility behind a public command surface that future agents must preserve. The selected refactor identifies skill discovery, plugin cache behavior, catalog parity, projection coordination, command-surface behavior, proof/eval entrypoints, dynamic tool resolution, analytics, and CLI response shaping as colocated concerns.

If the first extraction is not disciplined, the repo will either:

- create more indirection without reducing reasoning cost; or
- break the `./bin/ask` command contract while trying to improve internals.

## Goals

- Preserve the public `./bin/ask` skills command contract while identifying internal service boundaries.
- Produce a responsibility map that future agents can use before moving code.
- Extract plugin cache behavior behind a coherent service without changing user-facing or robot-facing behavior.
- Write the proof taxonomy ADR in parallel without adding proof enforcement into the command module yet.
- Establish validation evidence that the command plane remains deterministic after the first extraction.

## Non-Goals

- Do not redesign the full CLI.
- Do not add new skill features.
- Do not change generated command-handle semantics.
- Do not change source/projection/catalog ownership.
- Do not implement promotion gates in this slice.
- Do not split every service boundary in one pass.
- Do not create or mutate Linear objects from this spec.

## Boundary

### In Scope

- Read-only responsibility mapping for `Infrastructure/scripts/lib/ask/commands/skills.py`.
- Baseline capture for representative `./bin/ask skills ... --json` and human-readable commands.
- Extraction of plugin cache refresh/report/error behavior behind an internal service module.
- Import/call-site rewiring needed only for that extraction.
- Tests or smoke fixtures required to preserve behavior.
- Proof taxonomy ADR as a separate, parallel documentation/decision slice.

### Out of Scope

- Catalog/projection service extraction.
- Proof command implementation changes.
- Tool-resolution service extraction.
- Runtime-visible selection policy changes.
- New default-visible or trusted skill promotion rules.
- Repo-wide governance compression.
- Repository cognition burn-down or deletion/quarantine work.

## Baseline

Known source evidence:

- `.harness/linear/agent-skills-linear-plan.md` selects `Ask Control Plane Decomposition` as the first active milestone.
- `.harness/refactors/ask-control-plane-decomposition.md` defines the staged migration path.
- `.harness/refactors/proof-driven-skill-promotion.md` allows the proof taxonomy ADR to run in parallel.
- `.harness/core/architecture-invariants.md` makes `./bin/ask` the public control-plane contract.
- `.harness/core/routing-invariants.md` requires deterministic, explainable skill routing.
- `.harness/core/execution-invariants.md` requires machine-readable output stability and reversible migrations.
- `.harness/core/moat-invariants.md` says trust in `./bin/ask`, source/projection separation, and proof taxonomy are moat-critical.
- `.harness/decisions/*.md` is absent in this repository snapshot; no decision artifact constrains this slice.
- Live Linear on `2026-05-08` initially showed a project identity conflict. The current slice is now reconciled onto canonical project id `791c2f12-5ffb-4644-8421-f4216ac6d805`; duplicate project id `e6ad5ea3-28b0-4b07-b2e0-594ec1b9242f` is canceled.
- Live Linear on `2026-05-08` initially showed label mismatch. The current slice now maps to existing reusable labels: `architecture`, `Refactor`, `Agent`, `Policy`, and `CE: Spec`.
- `Infrastructure/scripts/lib/ask/commands/skills.py` is 3001 lines in this snapshot.
- Plugin cache DTO/error types currently live in `Infrastructure/scripts/lib/ask/commands/skills.py:57` and `Infrastructure/scripts/lib/ask/commands/skills.py:65`.
- Plugin cache pruning, version detection, copy replacement, and workspace cache refresh currently live in `Infrastructure/scripts/lib/ask/commands/skills.py:2349`, `Infrastructure/scripts/lib/ask/commands/skills.py:2400`, `Infrastructure/scripts/lib/ask/commands/skills.py:2413`, and `Infrastructure/scripts/lib/ask/commands/skills.py:2435`.
- `sync_skills` calls `_refresh_workspace_plugin_caches` from both rooted and flat workspace sync paths at `Infrastructure/scripts/lib/ask/commands/skills.py:2928` and `Infrastructure/scripts/lib/ask/commands/skills.py:2978`.

Baseline commands to capture before implementation:

```bash
./bin/ask skills resolve he-spec --json
./bin/ask skills list --json
./bin/ask skills sync --scope workspace --projection rooted --dry-run --json
./bin/ask repo doctor --json --robot
```

Additional command samples should be chosen from the exact plugin cache behavior discovered in the responsibility map.

Observed live baseline from this spec pass:

- `./bin/ask skills sync --scope workspace --dry-run --json` passed in the original spec pass. The execution plan now pins `--projection rooted` for deterministic before/after comparison.
- The dry-run plan reported plugin cache writes for `harness-engineering`, `plugin-factory`, and `skill-factory`.
- Each plugin cache write has two target roots:
  - `.agents/plugins-runtime/cache/agent-skills-local/<plugin>`
  - `Plugins/cache/agent-skills-local/<plugin>/0.1.0`
- The dry-run reported `validation_status: pass`, `mutation_counts.writes: 8`, `mutation_counts.deletes: 16`, `mutation_counts.symlinks: 22`, and no warnings.
- `./bin/ask repo doctor --json --robot` currently fails with existing `catalog_parity` drift: `count_mismatch`.
- The doctor failure also reports runtime budget pass with `default_visible_count: 10`, `estimated_description_tokens: 3172`, and command handle validation pass with `handle_count: 93`.
- The doctor blocker is pre-existing execution context for this spec. It should not be attributed to the spec change unless the implementation worsens it.

## Live Code Seam Map

The first extraction seam is not the full sync workflow. It is the plugin cache concern embedded inside sync.

| Current symbol | Current file/line | Proposed owner | Keep in command module? | Reason |
|---|---:|---|---|---|
| `PluginCacheRefreshReport` | `Infrastructure/scripts/lib/ask/commands/skills.py:57` | `ask/services/plugin_cache.py` | No | It describes plugin-cache mutation output, not CLI behavior. |
| `PluginCacheRefreshError` | `Infrastructure/scripts/lib/ask/commands/skills.py:65` | `ask/services/plugin_cache.py` | No | Error type is internal to plugin-cache refresh/pruning. |
| `_prune_command_handle_skill_entries` | `Infrastructure/scripts/lib/ask/commands/skills.py:2349` | `ask/services/plugin_cache.py` | No | It couples plugin cache pruning to command-handle ownership. |
| `_plugin_version` | `Infrastructure/scripts/lib/ask/commands/skills.py:2400` | `ask/services/plugin_cache.py` | No | Version normalization is plugin-cache path policy. |
| `_replace_plugin_cache_copy` | `Infrastructure/scripts/lib/ask/commands/skills.py:2413` | `ask/services/plugin_cache.py` | No | Copy/materialize/prune is plugin-cache mutation behavior. |
| `_refresh_workspace_plugin_caches` | `Infrastructure/scripts/lib/ask/commands/skills.py:2435` | `ask/services/plugin_cache.py` | No | This is the main service entrypoint candidate. |
| `sync_skills` calls to `_refresh_workspace_plugin_caches` | `Infrastructure/scripts/lib/ask/commands/skills.py:2928`, `Infrastructure/scripts/lib/ask/commands/skills.py:2978` | Command adapter remains caller | Yes, as delegation only | Sync controls workflow sequencing; plugin cache service owns refresh behavior. |

Boundary rule:

- `sync_skills` may still decide when plugin cache refresh runs.
- The plugin cache service must decide how marketplace entries become runtime/versioned cache writes, deletes, logs, and errors.
- The plugin cache service must not own projection sync, catalog projection refresh, root skill set generation, or final `CallResult` formatting.

## Proposed Service Contract

Target module:

```text
Infrastructure/scripts/lib/ask/services/plugin_cache.py
```

Allowed imports from the command layer:

- `PluginCacheRefreshReport`
- `PluginCacheRefreshError`
- `refresh_workspace_plugin_caches`

Suggested public service entrypoint:

```python
def refresh_workspace_plugin_caches(
    plan: dict[str, object],
    logs: list[str],
    repo_root: Path,
    *,
    dry_run: bool,
) -> ErrorObject | None:
    ...
```

The signature may remain compatible with the current `_refresh_workspace_plugin_caches` call site to keep the first extraction small. A later pass may replace the mutable `plan`/`logs` coupling with a richer return object, but that is not required for this slice.

Minimum extracted helpers:

- `prune_command_handle_skill_entries`
- `plugin_version`
- `replace_plugin_cache_copy`
- `refresh_workspace_plugin_caches`

Service dependencies that must be made explicit:

- local marketplace loading from plugin command helpers;
- directory copy/materialization helpers;
- command-handle report lookup for duplicate pruning;
- `ErrorObject` construction;
- filesystem mutation and dry-run behavior.

Current coupling to handle deliberately:

- `skills.py` currently imports `_copy_directory_contents`, `_load_local_marketplace`, and `_materialize_first_level_skill_aliases` from `ask.commands.plugins` at `Infrastructure/scripts/lib/ask/commands/skills.py:20`.
- If `services/plugin_cache.py` imports those helpers directly from `ask.commands.plugins`, the extraction reduces `skills.py` size but preserves command-module coupling.
- Acceptable first-pass options:
  - move those helper functions to a neutral service/helper module and have both command modules import from it; or
  - keep a temporary dependency on `ask.commands.plugins` only if the eval artifact records an explicit follow-up and the dependency does not introduce an import cycle.
- Forbidden outcome: `ask.commands.skills` stops owning plugin cache behavior but `ask.services.plugin_cache` becomes a thin wrapper over `ask.commands.plugins`.

Forbidden first-pass redesign:

- Do not alter marketplace schema.
- Do not change cache root layout.
- Do not change stale cache deletion semantics.
- Do not change command-handle duplicate pruning behavior.
- Do not replace mutable `plan`/`logs` with a new protocol unless tests prove exact parity.

## Responsibility Map Artifact

The implementation must create or update one durable responsibility map before code movement.

Recommended location:

```text
.harness/evals/agent-skills-ask-control-plane-decomposition-eval.md
```

The responsibility map must include at least:

| Boundary | Current symbols or regions | Future owner | Move in first slice? |
|---|---|---|---|
| Command adapter | argument parsing, result formatting, exit-code behavior | `commands/skills.py` | No |
| Plugin cache | `PluginCacheRefreshReport`, `PluginCacheRefreshError`, `_prune_command_handle_skill_entries`, `_plugin_version`, `_replace_plugin_cache_copy`, `_refresh_workspace_plugin_caches` | `services/plugin_cache.py` | Yes |
| Catalog/projection | `_refresh_catalog_projections`, rooted projection sync, projection metadata | later catalog/projection services | No |
| Proof/eval | `skills_proof`, `skills_prove`, proof payload assembly | later proof service | No |
| Tool resolution | skill installer/builder module lookup | later tool-resolution service | No |
| Routing/improvement | `route_skills`, `goal_skills`, `improve_skills` | later routing/improvement service | No |

## Domain Model

| Concept | Meaning in this spec |
|---|---|
| Command adapter | Public CLI layer that parses arguments, calls services, formats human/robot output, and maps exit codes. |
| Service boundary | Internal module that owns one coherent responsibility and reduces what the command adapter must know. |
| Plugin cache service | Internal owner for plugin cache refresh/report/error behavior. |
| Robot contract | Machine-facing `--json` / `--robot` output that must not drift accidentally. |
| Responsibility map | Evidence artifact that maps current functions/blocks to future service boundaries before code moves. |
| Proof taxonomy ADR | Parallel decision slice defining proof levels and lifecycle states before enforcement. |
| Source/projection boundary | Trust boundary between canonical source files and generated/runtime surfaces. |

## Lifecycle

1. Boundary map is produced from current code without behavior change.
2. Representative command outputs are captured.
3. Plugin cache behavior is extracted behind a service.
4. Existing command adapter delegates to the service.
5. Focused tests and command smoke checks compare behavior before and after extraction.
6. Proof taxonomy ADR is written and reviewed in parallel.
7. The eval artifact records evidence before the parent issue can close.

No later extraction phase may start until the plugin cache extraction is validated or explicitly rolled back.

## Interfaces

### Public Interfaces To Preserve

- `./bin/ask`
- `./bin/ask skills ...`
- `./bin/ask skills resolve <handle> --json`
- `./bin/ask skills list --json`
- `./bin/ask repo doctor --json --robot`
- Exit-code behavior for representative skill commands.
- Human-readable output unless a change is explicitly approved.
- JSON/robot output shape.

### Internal Interfaces To Introduce

The exact module path may be adjusted to match repo conventions, but the intended boundary is:

```text
Infrastructure/scripts/lib/ask/services/plugin_cache.py
```

The first service should expose behavior-level functions, not pass-through wrappers. Names must come from the responsibility map, but the boundary must satisfy:

- the command adapter does not know cache internals;
- the service does not format final CLI output;
- errors are structured enough for the adapter to map them into existing output and exit behavior;
- service functions are directly testable where practical.

### Baseline Output Contract For Plugin Cache

The extraction must preserve these observed dry-run fields:

- `data.plan.plugin_cache_writes`
- `data.plan.writes`
- `data.plan.deletes`
- `data.logs`
- `data.plan.validation_status`
- `data.plan.mutation_counts`
- `data.plan.warnings`
- `errors`

The extraction must preserve these observed log patterns:

- `Would replace local plugin cache: <runtime-target> <- <source>`
- `Would replace local plugin cache: <versioned-target> <- <source>`
- `Would remove stale versioned local plugin cache variant: <path>`
- `Would remove stale local plugin cache: <path>`
- `Skipped workspace plugin cache refresh: <reason>`
- `Skipped unsafe plugin cache name: <name>`
- `Skipped missing plugin cache source: <path>`

Do not normalize or reword these strings in the first extraction unless the implementation records an explicit contract change.

## Invariants

- `./bin/ask` remains the public control-plane contract.
- Generated/runtime projections are not source.
- Generated command handles remain shallow pointers.
- `--json --robot` is the machine consumer contract.
- Source/projection/catalog parity remains a trust boundary.
- New feature logic must not accumulate in an over-threshold command module.
- Structural audit is not outcome proof.
- Migration steps must be reversible.
- Hidden orchestration is a defect.

## Failure And Recovery

| Failure | Recovery |
|---|---|
| Robot JSON changes unexpectedly | Stop the phase, compare baseline output, revert extraction or make an explicit contract decision. |
| Human output changes unexpectedly | Stop unless the change is intentional and documented. |
| Plugin cache refresh/report behavior regresses | Revert the plugin cache service extraction only; keep responsibility map if accurate. |
| Service becomes pass-through wrapper | Collapse it or deepen the boundary before merging. |
| Import path churn spreads outside the selected concern | Stop and narrow the extraction. |
| Proof ADR starts defining enforcement implementation | Split enforcement back to the later proof-driven promotion phase. |
| Catalog/projection behavior changes | Stop; that is a later phase and outside this spec. |

Rollback condition:

- Any behavior drift in representative commands without explicit approval should block completion of this slice.

## Observability

This slice needs operational evidence, not new telemetry.

Required evidence:

- responsibility map path or section;
- before/after command outputs or summarized snapshots;
- changed files list;
- focused test outcomes;
- docs lint outcome if docs/specs are touched;
- repo doctor output outcome;
- eval artifact path.

Expected eval artifact:

```text
.harness/evals/agent-skills-ask-control-plane-decomposition-eval.md
```

## Acceptance Matrix

| Acceptance ID | Requirement | Validation |
|---|---|---|
| SA-ASK-001 | A responsibility map exists for `Infrastructure/scripts/lib/ask/commands/skills.py` and assigns plugin cache behavior to a future service boundary. | Inspect committed responsibility map or spec section; verify it distinguishes command adapter, plugin cache, catalog/projection, proof, and tool-resolution concerns. |
| SA-ASK-002 | Representative baseline outputs are captured before code movement. | Evidence includes exact commands and before-state output summaries for `skills resolve`, `skills list`, `repo doctor`, plus plugin-cache-specific samples discovered by SA-ASK-001. |
| SA-ASK-003 | Plugin cache behavior is moved behind an internal service without public command drift. | Before/after command evidence shows preserved human and JSON/robot behavior for representative plugin cache paths, especially `./bin/ask skills sync --scope workspace --projection rooted --dry-run --json`. |
| SA-ASK-004 | `commands/skills.py` remains the CLI adapter for the touched path and no new unrelated feature behavior is added there. | Diff review confirms only delegation/adapter responsibilities remain for extracted plugin cache behavior. |
| SA-ASK-005 | The plugin cache service is not a pass-through wrapper. | Service owns cache refresh/report/error behavior and has testable behavior-level functions. |
| SA-ASK-006 | Source/projection/catalog semantics do not change in this slice. | No changes to projection ownership, selection policy, or catalog parity semantics unless explicitly documented as untouched. |
| SA-ASK-007 | The proof taxonomy ADR is written as a parallel decision slice without implementing promotion gates. | ADR exists or ready draft exists; it defines proof levels/lifecycle states and keeps enforcement out of this slice. |
| SA-ASK-008 | Completion is backed by an eval artifact. | `.harness/evals/agent-skills-ask-control-plane-decomposition-eval.md` exists before the parent issue is considered closable. |
| SA-ASK-009 | Rollback conditions are recorded with actual command evidence. | Eval artifact records whether rollback conditions were hit and what command/test evidence supports continuation. |
| SA-ASK-010 | Existing `repo doctor` catalog parity drift is classified separately from plugin cache extraction regressions. | Eval artifact records the current `catalog_parity` `count_mismatch` blocker and proves the implementation did not introduce a worse or different doctor failure. |
| SA-ASK-011 | Plugin cache root layout is preserved. | Dry-run plan still writes both `.agents/plugins-runtime/cache/agent-skills-local/<plugin>` and `Plugins/cache/agent-skills-local/<plugin>/0.1.0` for applicable plugins. |
| SA-ASK-012 | No later extraction phase is accidentally started. | Diff review confirms catalog/projection, proof/eval, routing/improvement, and tool-resolution behavior are not moved or semantically changed in this slice. |
| SA-ASK-013 | The extraction does not preserve command-module coupling through a new service wrapper. | Review imports and service implementation; any temporary dependency on `ask.commands.plugins` is documented with a follow-up, and no import cycle exists. |
| SA-ASK-014 | Linear project identity remains reconciled before implementation planning starts. | `JSC-284` through `JSC-287` remain in canonical project `791c2f12-5ffb-4644-8421-f4216ac6d805`; duplicate project `e6ad5ea3-28b0-4b07-b2e0-594ec1b9242f` remains canceled and receives no new work. |
| SA-ASK-015 | Linear labels remain reconciled before implementation planning starts. | Parent and child issues retain the existing reusable labels mapped in this spec, or `he-plan` records a deliberate replacement mapping. |

## Linear Acceptance Traceability

| Linear issue | Acceptance IDs | Source artifact |
|---|---|---|
| JSC-284 | SA-ASK-001, SA-ASK-002, SA-ASK-003, SA-ASK-004, SA-ASK-005, SA-ASK-006, SA-ASK-008, SA-ASK-009, SA-ASK-010, SA-ASK-011, SA-ASK-012, SA-ASK-013, SA-ASK-014, SA-ASK-015 | `.harness/linear/agent-skills-linear-plan.md` |
| JSC-285 | SA-ASK-001, SA-ASK-002, SA-ASK-010 | `.harness/refactors/ask-control-plane-decomposition.md` |
| JSC-286 | SA-ASK-003, SA-ASK-004, SA-ASK-005, SA-ASK-006, SA-ASK-009, SA-ASK-010, SA-ASK-011, SA-ASK-012, SA-ASK-013 | `.harness/refactors/ask-control-plane-decomposition.md` |
| JSC-287 | SA-ASK-007 | `.harness/refactors/proof-driven-skill-promotion.md` |

## First Slice

The first implementation pass should do only this:

1. Produce or update a responsibility map for `Infrastructure/scripts/lib/ask/commands/skills.py`.
2. Capture baseline outputs for representative skill commands.
3. Extract plugin cache behavior into an internal service.
4. Run focused validation.
5. Record evidence in the eval artifact.

The proof taxonomy ADR may run in parallel because it is a decision/specification artifact, not command enforcement.

## Questions

- What exact plugin cache command paths should be treated as the baseline samples after the responsibility map is complete?
- Should the responsibility map live inside the eval artifact, a source comment-free markdown artifact, or both?
- No open milestone-identity question remains for this slice: use Linear milestone `Command surface and ask reliability` and keep `Ask Control Plane Decomposition` as the HE slice name.

## Done

This spec is complete enough for `he-plan` when:

- the selected Linear/refactor slice is unchanged;
- Linear issue JSC-284 remains the parent tracker;
- duplicate `agent-skills` project identity remains resolved to canonical project `791c2f12-5ffb-4644-8421-f4216ac6d805`;
- Linear labels remain resolved through existing reusable labels;
- SA-ASK acceptance IDs are preserved;
- implementation scope remains limited to boundary mapping, plugin cache extraction, and the parallel proof taxonomy ADR.

This spec is not complete enough to close the Linear parent issue. Closure requires implementation evidence and the eval artifact.

## he-plan Handoff

Use this artifact as the requirements source for the first execution plan:

```text
.harness/specs/agent-skills-ask-control-plane-decomposition-spec.md
```

Primary sources:

- `.harness/linear/agent-skills-linear-plan.md`
- `.harness/refactors/ask-control-plane-decomposition.md`
- `.harness/refactors/proof-driven-skill-promotion.md`
- `.harness/core/architecture-invariants.md`
- `.harness/core/routing-invariants.md`
- `.harness/core/execution-invariants.md`
- `.harness/core/cognition-principles.md`
- `.harness/core/moat-invariants.md`

Validation expectations for planning:

- preserve SA-ASK IDs;
- verify SA-ASK-014 and SA-ASK-015 still hold before sequencing code movement;
- keep active implementation to one extraction concern at a time;
- require eval artifact before closure;
- preserve JSC-284 traceability unless the parent tracker is explicitly replaced.

## blackboard_delta

```yaml
schema_version: 1
artifact_status: created
artifacts:
  - .harness/specs/agent-skills-ask-control-plane-decomposition-spec.md
selected_slice:
  milestone: Command surface and ask reliability
  he_slice: Ask Control Plane Decomposition
  parent_issue_title: "[agent-skills] Decompose skills command module into bounded services"
  selected_refactor: .harness/refactors/ask-control-plane-decomposition.md
linear_status: created
linear_delta_status: updated
current_slice_status: ready_for_he_plan
label_status: resolved_mapped_to_existing_labels
linear_project_identity_status: resolved_canonical_project
linear_issue: JSC-284
linear_child_issues:
  - JSC-285
  - JSC-286
  - JSC-287
next_stage: he-plan
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
