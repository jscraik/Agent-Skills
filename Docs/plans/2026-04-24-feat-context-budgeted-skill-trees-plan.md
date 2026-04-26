---
schema_version: 1
title: "feat: Context-Budgeted Skill Trees Implementation Plan"
type: feat
status: implementation-in-review
date: 2026-04-24
origin: Docs/specs/2026-04-24-feat-context-budgeted-skill-trees-spec.md
spec: Docs/specs/2026-04-24-feat-context-budgeted-skill-trees-spec.md
plan_route: fresh
plan_depth: deep
current_phase: pre-implementation-review
---

# feat: Context-Budgeted Skill Trees Implementation Plan

## Table of Contents

- [Overview](#overview)
- [Planning Source](#planning-source)
- [Current Baseline](#current-baseline)
- [Scope](#scope)
- [Key Decisions](#key-decisions)
- [Review Corrections](#review-corrections)
- [Implementation Strategy](#implementation-strategy)
- [Task Graph](#task-graph)
- [Phase A: Reporting and Mode Contract](#phase-a-reporting-and-mode-contract)
- [Phase B: Rooted Projection Infrastructure](#phase-b-rooted-projection-infrastructure)
- [Phase C: Workouts and Default Flip](#phase-c-workouts-and-default-flip)
- [Validation Ladder](#validation-ladder)
- [Rollback Strategy](#rollback-strategy)
- [Risks and Controls](#risks-and-controls)
- [Open Decisions Before Execution](#open-decisions-before-execution)
- [Acceptance Checklist](#acceptance-checklist)
- [Next Stage Handoff](#next-stage-handoff)

## Overview

Implement the context-budgeted skill-tree runtime model from the governing spec.
The work is a refactor of runtime projection and discovery surfaces, not a
catalog rewrite. The default mode remains `flat` until rooted projection has
reporting, parity, validation, router, workout, and rollback evidence.
`rooted` is the canonical projection-mode name; `skill-tree` is a compatibility
alias for users and docs that started with that terminology.

Plan route: `fresh`.

Plan depth: `deep`.

Execution posture:

- contract-first;
- reporting-first;
- no behavior flip until fallback is proven;
- generated-surface ownership preserved;
- local plugin skills remain separately browsable;
- project-level skills are overlays, not mutations to global skill sources.

## Planning Source

Primary source:

- `Docs/specs/2026-04-24-feat-context-budgeted-skill-trees-spec.md`

Related planning context:

- `Docs/plans/2026-04-12-feat-product-factory-runtime-separation-plan.md`
- `Docs/plans/2026-04-09-feat-skill-plugin-selection-gold-standard-upgrade-plan.md`

The runtime-separation plan is especially relevant because it already treats
runtime/projection surfaces as derived outputs and warns against direct edits to
`.agents/**`, `.agents/skills/**`, `skills-codex/**`, `Plugins/cache/**`, and
runtime projection lanes.

## Current Baseline

Current live baseline from `./bin/ask skills budget --json`:

```text
status: pass
default_visible_count: 18
catalog_default_count: 18
advanced_visible_count: 105
policy_identity: ccc42d9df4a2db2e
```

Interpretation:

- The current default runtime surface is bounded, not emergency-unbounded.
- The advanced-visible catalog is large enough to justify rooted projection.
- The first implementation slice should make current surface reporting richer
  before changing sync behavior.

## Scope

In scope:

- `./bin/ask skills budget --json` runtime surface reporting.
- Projection-mode parsing for `flat`, `rooted`, and optional alias
  `skill-tree -> rooted`.
- Explicit rejection or deferred handling for `hybrid`.
- Scope reporting for `global`, `project`, `local-plugin`, `system`, and
  `primary-runtime`.
- Project-level skill overlay support.
- Local plugin skill browseability preservation.
- Canonical projection engine or explicit command-surface delegation.
- Root skill-set generation behind dry-run first.
- Latent manifests.
- Generated command-surface projection for `$` skill handles and `@` reviewer
  handles.
- Generated command handles for command-visible latent modules.
- Durable `./bin/ask reviewers resolve` command surface for `@<handle>`
  references.
- Public `./bin/ask` wrappers for generator, manifest, router, handle, and
  reviewer operations before those operations become normative validation gates.
- Bounded router MVP.
- Context-budget validation fixtures and gate wiring.
- Workout MVP and amendment evidence.
- Rooted default flip only after cutover gates pass.

Out of scope:

- Rewriting individual skill bodies before projection mechanics are proven.
- Changing plugin marketplace protocol.
- Replacing the existing flat mode before rooted rollout evidence exists.
- Implementing `hybrid` in wave 1.
- Changing Codex desktop picker internals. This plan may generate and sync the
  runtime surfaces Codex consumes, but must prove picker/invocation behavior from
  outside the app.
- Moving canonical skill/plugin roots as part of this plan unless a slice
  explicitly coordinates with the runtime-separation plan.

## Key Decisions

### D1: Implement `flat` and `rooted` First

`hybrid` remains deferred. Mode parsing may know about `hybrid` as a deferred
value, but mutating sync must not accept it until a named first consumer and
acceptance test exist.

### D2: Choose Projection Engine Boundary in Phase A

Before behavior changes, choose one:

- Add `Infrastructure/scripts/lifecycle-and-sync/projection_engine.py` and make
  `./bin/ask skills sync` plus `sync_skills.sh` call it.
- Make `sync_skills.sh` delegate projection inventory and mutation behavior to
  `./bin/ask skills sync`.

The recommended path is the first option: a Python projection engine with shell
wrapper delegation. It keeps business logic out of shell while preserving the
existing shell entrypoint.

### D3: Keep Plugin Browseability Separate from Runtime Visibility

Local plugin skill folders remain separately browsable for humans and operators,
matching the curated plugin shape. This does not make every local plugin skill a
first-level rooted runtime skill.

### D4: Project Skills Are Overlays

Project-level skills are canonical within a repo and should not mutate global
skill source files. Use this source path:

```text
Skills/project/<skill>/SKILL.md
```

Projection reports must show project/global shadowing explicitly.

### D5: Rooted Manifests Own Skill Handle Inputs

`.skillsets/<skill-set>/manifest.jsonl` remains the canonical rooted module
inventory for skill handles. A future `.skillsets/command-surface.json` is a
generated projection, not a hand-edited source of truth, until a separate ADR
promotes it.

Rationale: handle metadata must not drift from rooted routing metadata. Keeping
the manifests canonical lets command-surface validation catch duplicate handles,
missing `source_path`, missing `invoke_via`, stale generated command handles, and
skill/reviewer namespace collisions from one input set.

### D6: Command Handles Require Runtime and Invocation Gates

Resolver success is not enough to claim `$<handle>` works. A command-visible
latent module must pass these gates in order:

1. resolver gate: `./bin/ask skills resolve <handle> --json` returns one latent
   module;
2. generated command-surface gate: command metadata is present in the generated
   command-surface projection;
3. command-handle gate: `.agents/skills/<handle>/SKILL.md` is generated as a pointer
   with no full workflow body;
4. sync gate: workspace and user runtime projections are refreshed from
   canonical sources;
5. black-box proof gate: a public `./bin/ask` proof command records
   handle-to-module-to-invocation evidence;
6. live invocation gate: a fresh Codex session can use the explicit `$<handle>`
   token without loading unrelated latent workflows.

### D7: Reviewer Handles Use a Separate CLI Namespace

Reviewer and inspector handles are not skills. They resolve through:

```bash
./bin/ask reviewers resolve skillinspector --json
```

The command normalizes optional `@` prefixes, returns the canonical reviewer
role, writes schema-compatible evidence when requested, and fails on ambiguous
aliases. Skill resolution must keep reviewers out of the skill namespace.

### D8: Public `ask` Owns Operator and Agent Interfaces

Internal scripts may exist as implementation details, but plan validation and
agent workflows must use stable `./bin/ask` surfaces. A direct script invocation
may appear only in script-level unit tests or while creating the wrapper itself.

Required public wrappers before Phase B completion:

- `./bin/ask skills roots generate --dry-run --json`
- `./bin/ask skills manifests generate --dry-run --json`
- `./bin/ask skills route --skill-set <name> --task-stdin --json`
- `./bin/ask skills handles --check --json`
- `./bin/ask skills resolve <handle> --json`
- `./bin/ask reviewers resolve <handle> --json`
- `./bin/ask skills proof <handle> --json`

`./bin/ask skills proof` is the deterministic runtime-surface proof command. It
must not claim active Codex picker proof; it records the live picker check as a
manual session gate after resolver, command-handle, workspace-runtime, and
user-runtime gates pass. Reviewer handles stay separate and are proven with
`./bin/ask reviewers resolve <handle> --json`.

### D9: Review Before Work

This plan requires a review gate before implementation resumes. Any slice that
changes command handles, generated runtime command handles, projection mutation, router
fallback, or reviewer resolution must complete plan review and reviewer
synthesis before `he-work` starts.

## Review Corrections

This plan incorporates the commandable skill trees review findings and the
follow-up reviewer swarm findings:

| Finding | Correction |
| --- | --- |
| Resolver proof was mistaken for runtime/picker proof | D6 splits resolver, generated command surface, command-handle projection, sync, black-box proof, and live invocation into separate gates. |
| Rooted projection requires a generated runtime command-handle phase | B2a adds generated command handles before any claim that `$he-heartbeat` is command-visible. |
| Reviewer resolver lacks durable CLI ownership | D7 and B2a assign reviewers to `./bin/ask reviewers resolve`, separate from `./bin/ask skills resolve`. |
| Command surface needs explicit ownership | D5 keeps rooted manifests canonical and treats `.skillsets/command-surface.json` as a generated projection. |
| Internal script commands risk public contract drift | D8 requires public `./bin/ask` wrappers before generator, manifest, router, and proof commands become validation gates. |
| Router fallback is not executable enough | B3 defines deterministic low-confidence/no-match fallback commands and acceptance tests. |
| Invocation proof lacks an artifact schema | B2a requires a versioned handle proof artifact for handle, module, projection mode, budget checks, and outcome. |
| Default rooted state is not re-asserted after rollback | C4 and the cutover validation set add a final default-mode integrity assertion. |
| A0 boundary decision is not gate-enforced | A0 now requires a decision artifact ID and downstream phases must reference it. |

## Implementation Strategy

Deliver the feature in independently reversible phases:

- Phase A: reporting, mode parsing, parity, and ownership contracts.
- Phase B: rooted projection, manifests, command handles, routing, and budget
  gates while keeping `flat` default.
- Phase C: workouts, amendment records, soak evidence, and default flip.

Each phase should be shippable without requiring the next phase.

## Task Graph

```yaml
tasks:
  - id: A0
    title: "Baseline and projection-engine decision"
    depends_on: []
  - id: A1
    title: "Runtime surface report expansion"
    depends_on: [A0]
  - id: A2
    title: "Projection mode parser and flat parity"
    depends_on: [A1]
  - id: A3
    title: "Skill scope reporting"
    depends_on: [A1]
  - id: B1
    title: "Root skill-set model and generator dry-run"
    depends_on: [A2, A3]
  - id: B2
    title: "Manifest generator and validator"
    depends_on: [B1]
  - id: B2a
    title: "Command surface projection and command handles"
    depends_on: [B2]
  - id: B3
    title: "Bounded router MVP"
    depends_on: [B2a]
  - id: B4
    title: "Rooted mutation mode and budget fixtures"
    depends_on: [B1, B2, B2a, B3]
  - id: B5
    title: "Documentation and project/local-plugin scope UX"
    depends_on: [B4]
  - id: C0
    title: "Workout CLI command surface"
    depends_on: [B4]
  - id: C1
    title: "Workout MVP and scorecards"
    depends_on: [C0]
  - id: C2
    title: "Amendment proposal records"
    depends_on: [C1]
  - id: C3
    title: "Rooted soak records"
    depends_on: [C1, C2]
  - id: C4
    title: "Default flip"
    depends_on: [C3]
```

## Phase A: Reporting and Mode Contract

### A0: Baseline and Projection-Engine Decision

Goal:

- Freeze the starting point and choose the implementation boundary before
  behavior changes.

Implementation tasks:

- Record current `./bin/ask skills budget --json` output in a baseline doc or
  artifact.
- Inspect `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh` and
  `Infrastructure/scripts/lib/ask/commands/skills.py`.
- Choose the projection-engine boundary.
- Add a projection-boundary decision artifact under `Docs/architecture/` or
  `Docs/decisions/` before downstream implementation starts.
- Record the decision artifact ID/path in this plan or the execution report.
- Require A1, A2, and Phase B gates to reference the chosen boundary.
- Add an ADR or plan note if choosing anything other than `projection_engine.py`.

Files likely touched:

- `Docs/plans/` or `Docs/architecture/`
- `Infrastructure/scripts/lifecycle-and-sync/`
- `Infrastructure/scripts/lib/ask/commands/skills.py`

Validation:

```bash
./bin/ask skills budget --json
git diff --check
```

Exit criteria:

- Baseline is recorded.
- Projection engine boundary is explicit.
- Projection-boundary decision artifact exists and has a durable ID/path.
- A1, A2, and Phase B gate definitions reference that boundary.
- No sync behavior changes yet.

### A1: Runtime Surface Report Expansion

Goal:

- Extend `./bin/ask skills budget --json` to distinguish runtime surfaces and
  scopes.

Implementation tasks:

- Extend report fields for:
  - `projection_mode`;
  - `first_level_default_entries`;
  - `hidden_system_entries`;
  - `primary_runtime_entries`;
  - `plugin_runtime_entries`;
  - `system_bridge_skills`;
  - `duplicate_default_names`;
  - `largest_descriptions`;
  - `root_skill_set_count`;
  - `unmapped_skill_names`;
  - `estimated_description_words`;
  - `estimated_description_tokens`;
  - `budget_status`;
  - scope counts for `global`, `project`, `local-plugin`, `system`, and
    `primary-runtime`;
  - shadowed/suppressed entries.
- Keep existing field names stable for existing consumers.
- Preserve the existing `status` key for compatibility while adding
  `budget_status`; do not rename or remove `status` in Phase A.
- Add required JSON field parity tests against the governing spec's Runtime
  Surface Report field set.
- Add tests for current flat-mode output.

Files likely touched:

- `Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py`
- `Infrastructure/scripts/lifecycle-and-sync/skill_discovery.py`
- `Infrastructure/scripts/lifecycle-and-sync/selection_policy.py`
- `Infrastructure/tests/**`

Validation:

```bash
./bin/ask skills budget --json
python3 -m pytest Infrastructure/tests -q
```

Exit criteria:

- Current flat baseline still passes.
- Report includes scope and lane counts.
- Report includes every required Runtime Surface Report field from the spec.
- No rooted behavior yet.

### A2: Projection Mode Parser and Flat Parity

Goal:

- Add projection-mode contract without changing default behavior.

Implementation tasks:

- Add canonical mode enum:
  - `flat`
  - `rooted`
- Add alias:
  - `skill-tree -> rooted`
- Reject or report `hybrid` as deferred.
- Add env parsing for `SYNC_SKILLS_PROJECTION_MODE`.
- Add CLI parsing for `./bin/ask skills sync --projection`.
- Define precedence when CLI and env both specify projection mode; CLI argument
  wins and env is the default only when CLI is omitted.
- Thread the parsed mode through the sync command function and projection engine
  boundary so it cannot be parsed and then ignored.
- Normalize legacy shell scopes before parity is claimed:
  - `sync_skills.sh --workspace` maps to
    `./bin/ask skills sync --scope workspace`;
  - `sync_skills.sh --project-local` maps to a documented `./bin/ask` scope or is
    retired behind the canonical projection engine.
- Add dry-run inventory output for `flat`.
- Add JSON schema assertions for dry-run output fields, including planned
  writes, deletes, preserved bridge-lane entries, preserved system-lane entries,
  validation status, ambiguous or unmapped entries, mutation counts, report path,
  and warnings.
- Add parity tests proving flat output matches current behavior.
- Add a test assertion that `--projection rooted` and `--projection flat` reach
  the sync engine or projection engine as distinct values.
- Add env-mode tests proving `SYNC_SKILLS_PROJECTION_MODE` dispatches to the
  same projection engine and loses to explicit `--projection`.

Files likely touched:

- `Infrastructure/scripts/lifecycle-and-sync/selection_policy.py`
- `Infrastructure/scripts/lib/ask/commands/skills.py`
- `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh`
- selected tests under `Infrastructure/tests/**`

Validation:

```bash
./bin/ask skills budget --json
./bin/ask skills sync --scope workspace --projection flat --dry-run
python3 -m pytest Infrastructure/tests -q
```

Exit criteria:

- Default remains `flat`.
- `flat` parity passes.
- `rooted` can parse but does not mutate runtime surfaces yet.
- Unknown, deferred, or unsupported projection modes fail before any mutation.

### A3: Skill Scope Reporting

Goal:

- Make global/project/local-plugin/system/primary-runtime distinctions
  observable before manifests depend on them.

Implementation tasks:

- Add scope classification helpers.
- Treat current first-party skills as `global`.
- Add discovery support for project skill overlays from
  `Skills/project/<skill>/SKILL.md`.
- Enforce user-authored scope precedence as `project > local-plugin > global`,
  with `system` and `primary-runtime` bridge lanes handled separately.
- Define a resolved collision as one selected by that precedence rule with
  explicit shadow metadata for every suppressed source.
- Report local plugin skill browseability without counting all plugin skills as
  rooted first-level entries.
- Report scope collisions and shadowing candidates.
- Fail projection when unresolved project/local-plugin/global collisions remain.

Files likely touched:

- `Infrastructure/scripts/lifecycle-and-sync/skill_discovery.py`
- `Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py`
- `Infrastructure/tests/**`
- documentation for project skill overlays

Validation:

```bash
./bin/ask skills budget --json
python3 -m pytest Infrastructure/tests -q
```

Exit criteria:

- Runtime report shows skill counts by scope.
- Project overlays can be discovered without mutating global sources.
- Scope precedence is deterministic and reported.
- Positive and negative fixtures prove winner selection, shadow-report fields,
  and unresolved-collision failure.
- Scope collisions are reportable, and unresolved collisions fail projection.

## Phase B: Rooted Projection Infrastructure

### B1: Root Skill-Set Model and Generator Dry-Run

Goal:

- Generate the rooted skill-set inventory without writing runtime surfaces.

Implementation tasks:

- Define root skill-set inventory for wave 1.
- Add root skill template.
- Implement root skill-set generator dry-run.
- Enforce root body and description budgets in generated output.
- Ensure root body routes rather than listing child inventories.

Files likely touched:

- `Infrastructure/templates/root-skill-set/SKILL.md.j2`
- `Infrastructure/scripts/lifecycle-and-sync/generate_root_skill_sets.py`
- `Infrastructure/tests/**`

Validation:

```bash
./bin/ask skills roots generate --dry-run --json
python3 -m pytest Infrastructure/tests -q
```

Exit criteria:

- Root count is at or below budget.
- Root descriptions and bodies are within limits.
- Generated roots do not enumerate all child skills.

### B2: Manifest Generator and Validator

Goal:

- Generate deterministic latent manifests for rooted routing.

Implementation tasks:

- Implement `.skillsets/<skill-set>/manifest.jsonl` generation.
- Include wave-1 manifest input set:
  - non-system advanced/catalog-visible skills;
  - project-level skills;
  - local-plugin skills only when discovery classifies them as
    advanced/catalog-visible.
- Exclude system and primary-runtime bridge lanes from ordinary root manifests.
- Add metadata status reporting:
  - `untagged`;
  - `inferred`;
  - `declared`;
  - `validated`;
  - `enforced`.
- Define the metadata enforcement transition:
  - Phase B starts with missing metadata reported as advisory;
  - rooted mutation may proceed only when every in-scope module is declared,
    inferred with an explicit warning, or intentionally unmapped;
  - default flip requires metadata status to be `validated` or `enforced` for
    every in-scope module.
- Add collision reporting:
  - duplicate ids;
  - duplicate source paths;
  - project/local-plugin/global shadowing.
- Fail manifest/projection validation when unresolved scope collisions remain.

Files likely touched:

- `Infrastructure/scripts/lifecycle-and-sync/generate_skillset_manifests.py`
- `Infrastructure/scripts/lifecycle-and-sync/skill_discovery.py`
- path ownership documentation and generated-file policy surfaces
- `Infrastructure/tests/**`

Validation:

```bash
./bin/ask skills manifests generate --dry-run --json
python3 -m pytest Infrastructure/tests -q
```

Exit criteria:

- Every in-scope module maps exactly once or is reported as unmapped.
- Generated rows are deterministic.
- Generated manifests include provenance for generator name, projection mode,
  policy identity, and source revision when practical.
- Path ownership docs classify `.skillsets/**` as generated-but-committed and
  forbid hand edits.
- Metadata transition rules distinguish advisory, warning, validation failure,
  and enforced failure states.
- Scope collisions are explicit, and unresolved collisions fail validation.

### B2a: Command Surface Projection and Handle Stubs

Goal:

- Make selected latent modules and reviewers mentionable as command handles
  without treating resolver success as proof of Codex-visible invocation.

Implementation tasks:

- Generate `.skillsets/command-surface.json` from rooted manifests as a
  generated projection. Do not hand-edit it.
- Add or preserve the public skill-handle command surface:
  - `./bin/ask skills handles --json`;
  - `./bin/ask skills handles --check --json`;
  - `./bin/ask skills resolve <handle> --json`.
- Add the public reviewer-handle command surface:
  - `./bin/ask reviewers resolve <handle> --json`.
- Keep skill and reviewer namespaces separate. A `$` handle and an `@` handle
  may share spelling only when the resolver reports an explicit namespace and no
  command path is ambiguous.
- Generate `.agents/skills/<handle>/SKILL.md` command handles only for rooted
  manifest rows with `command_visibility != none`.
- Generate `agents/openai.yaml` beside each generated command handle where the runtime surface
  supports it.
- Enforce command-handle budgets:
  - maximum command handle count;
  - maximum description words;
  - maximum body words;
  - no full workflow instructions;
  - no examples;
  - no alias-only command handles.
- Require every target handle to declare `invoke_via`.
- Require every command-visible handle to resolve to exactly one `source_path`
  and, when applicable, exactly one `command_handle_path`.
- Define a versioned handle-proof artifact schema with at least:
  - `schema_version`;
  - `handle`;
  - `reviewer_handle`;
  - `canonical_handle`;
  - `kind`;
  - `command_visibility`;
  - `source_path`;
  - `command_handle_path`;
  - `projection_mode`;
  - `policy_identity`;
  - `budget_checks`;
  - `loaded_modules`;
  - `outcome`;
  - `artifact_path`.
- Add a black-box proof command that records handle-to-module-to-runtime-surface
  evidence without exposing full latent workflows:
  `./bin/ask skills proof <handle> --json`.
- Keep live Codex picker invocation separate from resolver and runtime-surface
  proof. The proof command must expose a `live_codex_invocation` field with
  `status: manual_session_gate` and an operator action to open or reload Codex
  and verify that `$<handle>` is selectable/invokable in the active session.

Files likely touched:

- `Infrastructure/scripts/lifecycle-and-sync/command_surface.py`
- `Infrastructure/scripts/lifecycle-and-sync/generate_skillset_manifests.py`
- command-handle template code under `Infrastructure/scripts/lifecycle-and-sync/**`
- `Infrastructure/scripts/lib/ask/commands/skills.py`
- reviewer command routing under `Infrastructure/scripts/lib/ask/**`
- `.skillsets/command-surface.json` as generated output
- `.agents/skills/<handle>/SKILL.md` as generated output
- `Infrastructure/tests/**`

Validation:

```bash
./bin/ask skills handles --check --json
./bin/ask skills resolve he-heartbeat --json
./bin/ask skills resolve skill-builder --json
./bin/ask reviewers resolve skillinspector --json
./bin/ask skills sync --scope workspace --projection rooted --dry-run
./bin/ask skills sync --scope user --projection rooted --dry-run
./bin/ask skills proof he-heartbeat --json
python3 -m pytest Infrastructure/tests -q
```

Exit criteria:

- `.skillsets/command-surface.json` is generated from rooted manifests and
  carries provenance proving that source.
- `he-heartbeat` resolves as a target skill handle with one source path and a
  generated command-handle path.
- `skill-builder` resolves as an orchestrator skill handle.
- `skillinspector` resolves only through the reviewer namespace.
- Generated command handles stay within budget and contain pointer instructions rather
  than full workflows.
- Workspace and user rooted dry-runs show the command-visible command handles that would
  be projected.
- Handle proof artifact exists, validates against schema, and distinguishes
  resolver, command-handle, sync, and invocation evidence.
- Live Codex invocation proof has a deterministic artifact path, validates
  against schema, and is not inferred from CLI resolution alone.

### B3: Bounded Router MVP

Goal:

- Add a router that selects latent modules without dumping manifests into
  context.

Implementation tasks:

- Add shared router script.
- Add public wrapper:
  `./bin/ask skills route --skill-set <name> --task-stdin --json`.
- Support `--task-stdin` and `--task-file`.
- Keep `--task` limited to non-sensitive examples/tests if implemented.
- Persist only redacted task summaries in router logs or decision artifacts by
  default.
- Return schema-versioned JSON with statuses:
  - `selected`;
  - `low_confidence`;
  - `no_match`;
  - `invalid_skill_set`;
  - `manifest_missing`.
- For `low_confidence`, `no_match`, `invalid_skill_set`, and
  `manifest_missing`, stop without loading a module and return an executable
  fallback contract.
- For recoverable low-confidence/no-match cases, return:
  - `clarification_required: true`;
  - `operator_action`;
  - `safe_fallback_command`;
  - `candidate_handles`;
  - `reason`.
- The only default fallback command is:
  `./bin/ask skills route --skill-set <name> --fallback flat --task-stdin --json`.
- If flat fallback cannot safely handle the request, return no fallback command
  and require clarification instead of guessing.
- Cap candidates at 3.
- Return source paths, not skill bodies.
- Add selected-module loading fixture that proves the chosen canonical
  `source_path` exists and can be read without projecting, symlinking, or copying
  the latent module into first-level `.agents/skills/**`.
- Enforce module-loading budget rules:
  - maximum loaded modules per task;
  - no unrelated skill-set loads;
  - selected module count cannot exceed the configured budget even when router
    returns three candidates.

Files likely touched:

- `Infrastructure/scripts/lifecycle-and-sync/route_skillset.py`
- router telemetry/decision artifact writer if separate
- `Infrastructure/tests/**`

Validation:

```bash
printf '%s\n' 'verify this implementation is complete' | \
  ./bin/ask skills route \
  --skill-set agent-ops \
  --task-stdin \
  --top-k 3 \
  --json
python3 -m pytest Infrastructure/tests -q
```

Exit criteria:

- Router never prints full manifest or skill body.
- Router handles low-confidence/no-match safely.
- Low-confidence/no-match fallback output is executable or explicitly requires
  clarification.
- Negative-path tests cover low confidence, no match, invalid skill set, missing
  manifest, and disabled fallback.
- Sensitive task text can avoid argv.
- Router and telemetry persistence prove raw task text is redacted by default.
- Router failure statuses stop module loading and require clarification or a
  documented fallback.
- Selected canonical `source_path` loads without first-level latent projection.
- Module loading respects max-loaded-module and unrelated-skillset constraints.

### B4: Rooted Mutation Mode and Budget Fixtures

Goal:

- Enable rooted projection mutation while keeping `flat` as default.

Implementation tasks:

- Add rooted projection writer.
- Preserve system and primary-runtime lanes.
- Ensure local plugin skills remain separately browsable but not automatically
  first-level rooted entries.
- Ensure user-scope rooted sync replaces copied plugin runtime mirrors from
  canonical `Plugins/` sources after any local plugin or marketplace update.
- Ensure project skill overlays participate in manifests and reports.
- Add budget fixtures for:
  - too many roots;
  - overlong root description;
  - overlong root body;
  - child inventory leakage;
  - latent first-level exposure;
  - router over-output;
  - manifest-shaped router output;
  - more than the configured max loaded modules per task;
  - unrelated skill-set load attempts;
  - raw task text persisted in router or telemetry artifacts;
  - missing or stale manifest provenance;
  - hand-edited generated manifest rows;
  - scope collision;
  - full workflow body in a generated command handle;
  - over-budget command handle description or body;
  - alias-only command handle;
  - target command handle missing `invoke_via`;
  - skill/reviewer namespace collision;
  - stale command-surface projection;
  - invalid handle-proof artifact.
- Wire budget validation into existing validation entrypoints.

Files likely touched:

- projection engine or `./bin/ask skills sync` implementation;
- `Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py`;
- `Infrastructure/scripts/validate_all.sh`;
- sync dry-run/mutation JSON schema fixtures;
- `Infrastructure/tests/fixtures/**`;
- `Infrastructure/tests/**`.

Validation:

```bash
./bin/ask skills budget --json
./bin/ask skills handles --check --json
./bin/ask skills sync --scope workspace --dry-run
./bin/ask skills sync --scope workspace --projection rooted --dry-run
./bin/ask skills sync --scope user --projection rooted --dry-run
./bin/ask skills sync --scope workspace --projection rooted
./bin/ask skills sync --scope user --projection rooted
./bin/ask plugins sync-local-runtime --dry-run
bash Infrastructure/scripts/validate_all.sh --ephemeral
./bin/ask skills sync --scope user --projection flat
./bin/ask skills sync --scope workspace --projection flat
./bin/ask skills sync --scope workspace --projection flat --dry-run
./bin/ask skills sync --scope user --projection flat --dry-run
python3 Infrastructure/scripts/validation-and-linting/check_context_budget.py --json
```

Exit criteria:

- Rooted dry-run and mutation mode work in controlled scope.
- Rooted dry-run contract coverage includes both `workspace` and `user` scopes.
- Controlled non-dry-run rooted workspace sync writes projection provenance and
  passes the rooted validation gate before rollback.
- Controlled non-dry-run user sync exercises forward rooted and rollback flat
  commands, then leaves the user surface in flat mode.
- User-scope rooted sync reports copied plugin runtime mirrors as replaced from
  canonical `Plugins/` sources; plugin updates must not rely on stale runtime
  copies or symlinked `~/plugins`.
- Flat and rooted dry-run/mutation outputs satisfy the sync JSON contract.
- User mutation outputs satisfy the sync JSON contract, including
  created/updated/removed/preserved counts, report path, and changed-surface
  warnings.
- Sync JSON schema distinguishes preserved bridge-lane entries from preserved
  system-lane entries.
- Budget validator catches seeded failures.
- Manifest ownership/provenance validator catches missing provenance and
  hand-edited `.skillsets/**` fixtures.
- Command-surface validator catches stale projections, duplicate handles,
  over-budget command handles, alias-only command handles, namespace collisions, target handles
  missing `invoke_via`, and invalid handle-proof artifacts.
- Redaction fixtures catch raw task text in router and telemetry persistence.
- Default remains `flat`.

### B5: Documentation and Scope UX

Goal:

- Make global/project/local-plugin/rooted semantics legible to future agents and
  humans.

Implementation tasks:

- Add architecture docs for projection modes.
- Add runbook for flat-to-rooted migration.
- Document project-level skill overlays.
- Document local plugin browseability and its distinction from rooted runtime
  visibility.
- Update README/root index language that currently assumes flat projection only.

Files likely touched:

- `README.md`
- root `SKILL.md`
- `Docs/architecture/**`
- `Docs/runbooks/**`

Validation:

```bash
git diff --check
./bin/ask skills budget --json
```

Exit criteria:

- Docs explain `flat`, `rooted`, `skill-tree` alias, and deferred `hybrid`.
- Docs explain project skill overlays and local plugin browseability.
- Docs explain that plugin runtime mirrors are copied directories and must be
  replaced after plugin source or marketplace updates.

## Phase C: Workouts and Default Flip

### C0: Workout CLI Command Surface

Goal:

- Add the `ask workouts` command contract before workout validation depends on
  it.

Implementation tasks:

- Add `ask workouts list`.
- Add `ask workouts run <skill-set>/<module> --attempts <n>`.
- Add `ask workouts score <skill-set>/<module>`.
- Add `ask workouts promote <skill-set>/<module> --if-better --dry-run`.
- Route commands to the workout runner and amendment workflow without requiring
  users or agents to call internal scripts directly.
- Define failure-path behavior for:
  - no workouts configured;
  - empty workout list;
  - unknown workout id;
  - missing scorecard;
  - runner failure;
  - invalid promotion target.
- Add parser tests for required arguments, unknown workout IDs, and dry-run
  promotion.

Files likely touched:

- `Infrastructure/scripts/lib/ask/**`
- `Infrastructure/bin/ask`
- workout runner entrypoints under `Infrastructure/scripts/**` or
  `Infrastructure/EVALUATION/**`
- `Docs/cli-specs/**`
- `Infrastructure/tests/**`

Validation:

```bash
./bin/ask workouts list --help
./bin/ask workouts run --help
./bin/ask workouts score --help
./bin/ask workouts promote --help
python3 -m pytest Infrastructure/tests -q
```

Exit criteria:

- `ask workouts` commands parse and dispatch to the intended implementation
  boundary.
- Unknown workout IDs fail before mutation.
- Empty, missing, and runner-error paths return structured errors and nonzero
  exits where appropriate.
- Promotion dry-run cannot write accepted amendment records.

### C1: Workout MVP and Scorecards

Goal:

- Add a minimal eval loop that can measure routing and instruction quality.

Implementation tasks:

- Add workout definitions for:
  - `agent-ops/verification-before-completion`;
  - `harness-engineering/he-router` or `harness-engineering/he-spec`;
  - one factory workflow.
- Add scorecard schema and writer under the canonical artifact path.
- Track pass rate, flake rate, wall-clock, tool steps, retries, and context
  estimate.
- Prevent shortcuts such as editing verifier files or hardcoding flags.

Files likely touched:

- workout runner under `Infrastructure/scripts/**` or `Infrastructure/EVALUATION/**`;
- `Infrastructure/artifacts/skill-workouts/**` as generated output;
- tests and fixtures.

Validation:

```bash
./bin/ask workouts list
./bin/ask workouts run agent-ops/verification-before-completion --attempts 3
./bin/ask workouts score agent-ops/verification-before-completion
```

Exit criteria:

- At least one workout runs end-to-end.
- Scorecard is generated.
- Context estimate is captured.
- Full cutover evidence is deferred to C3, which requires all three diagnostic
  workouts to pass with scorecards.

### C2: Amendment Proposal Records

Goal:

- Turn workout failures into controlled, auditable improvement proposals.

Implementation tasks:

- Add amendment proposal schema.
- Write accepted/rejected amendment records.
- Include previous hash, new hash, score before, score after, rationale,
  evidence, and rollback command.
- Reject patches that improve pass rate by exceeding context budget.

Files likely touched:

- amendment workflow scripts;
- `.skill-telemetry/amendments/**` as generated local artifact path;
- tests and docs.

Validation:

```bash
./bin/ask workouts promote agent-ops/verification-before-completion --if-better --dry-run
python3 -m pytest Infrastructure/tests -q
```

Exit criteria:

- Dry-run promotion works.
- Budget regression rejects amendment.

### C3: Rooted Soak Records

Goal:

- Produce deterministic rollout evidence before default flip.

Implementation tasks:

- Run at least three representative non-default sync/report cycles.
- Run the three diagnostic workouts named in C1 and require scorecards for each.
- Record timestamp, git SHA, projection mode, exact command, validation result,
  runtime surface artifact path, and report hash.
- Run five consecutive executions of the same validation command set on the same
  branch after rooted mutation support, using an isolated Codex profile or
  sandboxed home directory for any non-dry-run `--scope user` mutation.
- Before any non-dry-run user-scope cutover run, require:
  - no active Codex session is using the same user runtime surface;
  - pre-mutation snapshot and hash of user-facing projection files;
  - post-rollback snapshot parity check;
  - documented recovery commands for interrupted workspace/user sequences.
- Confirm no P0/P1 routing regressions remain open.

Validation:

- Run the canonical cutover validation set defined in the Validation Ladder.
- Execute it five consecutive times on the same branch.

Exit criteria:

- Three soak records exist.
- Each soak record contains timestamp, git SHA, projection mode, exact command,
  validation result, runtime surface artifact path, and report hash.
- Three diagnostic workouts pass with scorecards.
- Five consecutive executions of the same validation command set pass on the
  same branch.
- All A0, Phase B, and router-threshold decisions have artifact IDs and
  revision stamps before C3 soak records are accepted.
- No P0/P1 routing regressions remain open.
- Rollback command is documented and tested.

### C4: Default Flip

Goal:

- Make rooted projection the default only after cutover gates pass.

Implementation tasks:

- Change default projection from `flat` to `rooted`.
- Preserve explicit rollback:

```bash
./bin/ask skills sync --scope workspace --projection flat
./bin/ask skills sync --scope user --projection flat
```

- Update docs and any environment variable guidance.
- Verify system and primary-runtime bridge lanes remain intact.

Validation:

```bash
./bin/ask skills budget --json
./bin/ask runtime surface --json
./bin/ask skills sync --scope workspace --dry-run
./bin/ask skills sync --scope workspace --projection rooted
./bin/ask skills sync --scope workspace --projection flat
./bin/ask skills sync --scope user --projection rooted --dry-run
./bin/ask skills sync --scope user --projection rooted
./bin/ask skills sync --scope user --projection flat
./bin/ask skills sync --scope user --projection flat --dry-run
./bin/ask runtime surface --json
bash Infrastructure/scripts/validate_all.sh --ephemeral
```

Exit criteria:

- Default rooted projection passes.
- Three diagnostic workouts have passing scorecards.
- Non-dry-run workspace forward and rollback commands pass and leave the
  workspace surface in flat mode when rollback is requested.
- Non-dry-run user forward and rollback commands pass and leave the user surface
  in flat mode when rollback is requested.
- Flat rollback still works.
- Final default-mode integrity assertion proves configured default remains
  `rooted` after explicit rollback commands, unless the rollback command is
  intentionally persisted as a documented operator action.
- No bridge lane regression.

## Validation Ladder

Use the smallest relevant validation first, then widen.

Per small Python/script slice:

```bash
python3 -m pytest Infrastructure/tests -q
```

Per reporting/projection slice:

```bash
./bin/ask skills budget --json
./bin/ask skills sync --scope workspace --projection flat --dry-run
```

Per rooted slice:

```bash
./bin/ask skills sync --scope workspace --projection rooted --dry-run
./bin/ask skills handles --check --json
./bin/ask skills resolve he-heartbeat --json
./bin/ask reviewers resolve skillinspector --json
```

Per validation-gate slice:

```bash
bash Infrastructure/scripts/validate_all.sh --ephemeral
```

Canonical cutover validation set:

```bash
./bin/ask skills budget --json
./bin/ask skills handles --check --json
./bin/ask skills resolve he-heartbeat --json
./bin/ask skills resolve skill-builder --json
./bin/ask reviewers resolve skillinspector --json
./bin/ask skills sync --scope workspace --projection rooted --dry-run
./bin/ask skills sync --scope workspace --projection rooted
./bin/ask skills sync --scope user --projection rooted --dry-run
./bin/ask skills sync --scope user --projection rooted
./bin/ask skills proof he-heartbeat --json
bash Infrastructure/scripts/validate_all.sh --ephemeral
./bin/ask skills sync --scope user --projection flat
./bin/ask skills sync --scope workspace --projection flat
./bin/ask skills sync --scope workspace --projection flat --dry-run
./bin/ask skills sync --scope user --projection flat --dry-run
./bin/ask runtime surface --json
python3 Infrastructure/scripts/validation-and-linting/check_context_budget.py --json
```

C3 requires five consecutive executions of this exact command set on the same
branch in an isolated profile for user-scope mutations. The full validation gate
intentionally runs before flat rollback because it verifies the rooted
first-level workspace surface. The final flat dry-runs, runtime-surface
assertion, and flat context-budget check prove rollback remains available without
mixing the two runtime surfaces in one validator invocation. C4 reuses the same
set immediately before flipping the default.

## Rollback Strategy

Primary rollback regenerates the workspace projection first, then relinks the
user-facing surface:

```bash
./bin/ask skills sync --scope workspace --projection flat
./bin/ask skills sync --scope user --projection flat
```

If environment variables participate in runtime mode:

```bash
SYNC_SKILLS_PROJECTION_MODE=flat ./bin/ask skills sync --scope workspace
SYNC_SKILLS_PROJECTION_MODE=flat ./bin/ask skills sync --scope user
```

Scope naming must be normalized before implementation:

- `./bin/ask skills sync --scope workspace` is the canonical projection mutation scope.
- `./bin/ask skills sync --scope user` is the user-facing relink/sync scope and must
  not be the only command used for rollback.
- `sync_skills.sh --workspace` maps to
  `./bin/ask skills sync --scope workspace`.
- `sync_skills.sh --project-local` must either map to a documented `./bin/ask`
  scope or be retired behind the canonical projection engine before parity is
  claimed.

Rollback triggers:

- rooted projection exposes latent modules first-level;
- system or primary-runtime bridge lanes disappear;
- `ask skills` core commands fail only in rooted mode;
- router no-match/low-confidence blocks a workflow that flat mode handles and no
  fallback exists;
- validation fails in rooted mode and passes after flat rollback.

## Risks and Controls

| Risk                                                 | Impact                                                      | Control                                                                                |
| ---------------------------------------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Sync path divergence                                 | Shell and Python sync produce different surfaces            | Choose one projection engine boundary in A0; add parity tests                          |
| Scope collision ambiguity                            | Project/local/global skills shadow silently                 | Require collision report and fail unresolved collisions                                |
| Plugin browseability mistaken for runtime visibility | Rooted surface grows accidentally                           | Separate `LocalPluginSkillView` from runtime projection and validate first-level count |
| Router leaks task text                               | Sensitive prompt text appears in argv/logs                  | Support stdin/file input and redacted persistence                                      |
| Manifest overreach                                   | System/primary-runtime lanes pulled into ordinary manifests | Exclude bridge lanes and report separately                                             |
| Resolver proof mistaken for invocation proof         | `$` handles appear resolved but are not Codex-visible        | Require resolver, command-handle, sync, proof artifact, and live invocation gates      |
| Command-surface drift                                | Generated command handles diverge from rooted manifests     | Treat `.skillsets/command-surface.json` as generated projection with provenance checks |
| Reviewer namespace ambiguity                         | `@` reviewers collide with `$` skills                       | Use `./bin/ask reviewers resolve` and fail ambiguous aliases                           |
| Router fallback ambiguity                            | Low-confidence routes leave agents without executable path   | Require executable fallback command or explicit clarification-required response        |
| Default state not re-asserted                        | Rollback tests accidentally persist the wrong default        | End cutover/default-flip validation with `./bin/ask runtime surface --json`            |
| User-scope cutover is not isolated                   | Validation can rewrite a live operator runtime               | Run user mutation checks in an isolated profile with snapshot parity                   |
| Default flip too early                               | Normal workflows regress                                    | Keep flat default until Phase C gates pass                                             |
| Runtime-separation conflict                          | This plan conflicts with canonical path migration           | Treat runtime-separation plan as dependency; do not move roots in this plan            |

## Open Decisions Before Execution

Resolve in A0 before A1/A2 behavior changes:

- Projection engine boundary:
  - `projection_engine.py` shared by shell/Python; or
  - shell delegates to `./bin/ask skills sync`.
- Boundary decision artifact:
  - must exist under `Docs/architecture/` or `Docs/decisions/`;
  - must be referenced by A1, A2, and Phase B gates.

Resolve before the relevant Phase B slice starts:

- Root skill-set inventory for wave 1.
- Any ADR that would promote `.skillsets/command-surface.json` from generated
  projection to source of truth. Without that ADR, rooted manifests own command
  handle inputs.

Resolve before the relevant B3 router slice starts:

- Low-confidence router threshold.

Recommended defaults:

- Use `projection_engine.py`.
- Use canonical `rooted` with `skill-tree` alias.
- Use `Skills/project/<skill>/SKILL.md` for project overlays.
- Keep `.skillsets/<skill-set>/manifest.jsonl` as the command-handle source.
- Resolve reviewers through `./bin/ask reviewers resolve`.
- Keep root set count at or below 10.

## Acceptance Checklist

Phase A:

- [ ] Projection-boundary decision artifact exists and downstream gates
      reference it.
- [ ] Runtime surface report includes lanes and scopes.
- [ ] Projection mode parser supports `flat`, `rooted`, and `skill-tree` alias.
- [ ] `SYNC_SKILLS_PROJECTION_MODE` is tested, and explicit `--projection`
      overrides the environment default.
- [ ] `--projection` reaches the sync/projection engine and cannot be silently
      ignored.
- [ ] Shell/Python sync scopes have a documented canonical mapping.
- [ ] Legacy shell scope mapping or retirement is covered by parity tests.
- [ ] Sync dry-run/mutation JSON contract has schema assertions.
- [ ] `hybrid` is rejected or marked deferred.
- [ ] Flat parity passes.
- [ ] Default remains `flat`.

Phase B:

- [ ] Root generation dry-run passes budgets.
- [ ] Manifest generation maps every in-scope module or reports it as unmapped.
- [ ] Manifest provenance and `.skillsets/**` ownership validation pass.
- [ ] `.skillsets/command-surface.json` is generated from rooted manifests and
      carries provenance.
- [ ] `./bin/ask skills handles --check --json` passes.
- [ ] `./bin/ask skills resolve he-heartbeat --json` resolves one target
      module and generated command handle.
- [ ] `./bin/ask skills resolve skill-builder --json` resolves one orchestrator
      module and generated command handle.
- [ ] `./bin/ask reviewers resolve skillinspector --json` resolves a reviewer
      outside the skill namespace.
- [ ] Generated command handles are thin and include supported
      `agents/openai.yaml` metadata.
- [ ] Workspace and user rooted dry-runs show command-visible command handles.
- [ ] Handle-proof artifact validates and distinguishes resolver, command-handle, sync,
      and invocation evidence.
- [ ] `./bin/ask skills proof he-heartbeat --json` passes resolver,
      command-handle, workspace-runtime, and user-runtime gates, and reports
      live Codex picker invocation as a separate manual session gate.
- [ ] Router returns at most three candidates and no full body/manifest content.
- [ ] Router supports stdin/file task input.
- [ ] Router low-confidence/no-match output is executable or explicitly asks for
      clarification.
- [ ] Selected canonical `source_path` loads without latent first-level
      projection.
- [ ] Module-loading budget fixtures enforce max loaded modules and unrelated
      skill-set bans.
- [ ] Router and telemetry redaction fixtures pass.
- [ ] Rooted dry-run passes.
- [ ] Rooted mutation works in controlled scope.
- [ ] Local plugin skills remain separately browsable.
- [ ] Project-level skills can overlay global skills with explicit reporting.
- [ ] Scope precedence is `project > local-plugin > global`, with bridge lanes
      separate.
- [ ] Context-budget validator catches seeded failures.

Phase C:

- [ ] Workout MVP runs.
- [ ] `ask workouts` command surface parses and dispatches before workout MVP
      validation depends on it.
- [ ] `ask workouts` empty/missing/error paths return structured failures.
- [ ] Scorecards include pass rate, flake rate, wall-clock, and context estimate.
- [ ] Amendment dry-run rejects context-budget regression.
- [ ] Three rooted soak records exist.
- [ ] User-scope non-dry-run cutover validation runs in an isolated Codex
      profile or sandboxed home directory with snapshot parity checks.
- [ ] Soak records include required metadata fields and report hash.
- [ ] Three diagnostic workouts pass with scorecards.
- [ ] Five consecutive executions of the same validation command set pass on the
      same branch.
- [ ] Decision artifact IDs and revision stamps are closed before C3 soak
      records are accepted.
- [ ] No P0/P1 routing regressions remain open.
- [ ] Default flips to rooted.
- [ ] Both-scope forward rooted and rollback flat mutation paths pass.
- [ ] Final default-mode integrity assertion passes after rollback commands.
- [ ] Flat rollback remains documented and tested.

## Next Stage Handoff

Recommended next Harness Engineering stage:

```text
he-technical-review
```

Review this plan before `he-work`, with emphasis on:

- whether Phase A is small enough;
- whether project/global/local-plugin scope semantics are implementable;
- whether the projection-engine boundary should be decided before coding;
- whether B2a correctly separates resolver, command-handle, sync, proof artifact, and
  live invocation gates;
- whether rooted manifests are clearly the command-handle source of truth;
- whether reviewer handles belong in the separate `./bin/ask reviewers`
  namespace;
- whether router fallback is executable enough for agents;
- whether user-scope cutover validation is isolated and rollback-safe;
- whether any step conflicts with the runtime-separation plan.

If the review is clean, execute the smallest reviewed slice, not the whole plan:

```text
he-work Docs/plans/2026-04-24-feat-context-budgeted-skill-trees-plan.md --phase reviewed-slice
```
