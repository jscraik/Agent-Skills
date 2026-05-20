---
schema_version: 1
title: Context-Budgeted Skill Trees
type: feat
status: draft
date: 2026-04-24
origin: harness-engineering he-spec
risk: medium-high
spec_depth: deepened
ui_required: false
---

# Context-Budgeted Skill Trees

## Table of Contents

- [Enhancement Summary](#enhancement-summary)
- [Current-State Baseline](#current-state-baseline)
- [Problem Statement](#problem-statement)
- [Goals](#goals)
- [Required Invariants](#required-invariants)
- [Non-Goals](#non-goals)
- [System Boundary](#system-boundary)
- [Architecture Decisions](#architecture-decisions)
- [Core Domain Model](#core-domain-model)
- [Lifecycle State Machine](#lifecycle-state-machine)
- [Functional Contracts](#functional-contracts)
- [Data Ownership and Generated Surfaces](#data-ownership-and-generated-surfaces)
- [Migration and Cutover Rules](#migration-and-cutover-rules)
- [Security and Safety Requirements](#security-and-safety-requirements)
- [Failure Model](#failure-model)
- [Observability](#observability)
- [Acceptance Criteria](#acceptance-criteria)
- [Verification Matrix](#verification-matrix)
- [Open Questions](#open-questions)
- [Definition of Done](#definition-of-done)
- [Handoff to `he-plan`](#handoff-to-he-plan)

## Enhancement Summary

Introduce context-budgeted runtime projection modes for the Agent-Skills catalog.
The current default runtime surface is already bounded by selection policy, so this
is a refactor of the projection model rather than a restart. The new model keeps
the existing flat projection as a fallback, adds a root-skill-set projection for
large catalogs, and enforces context budgets through existing validation lanes.

The target runtime posture is:

```text
Canonical catalog:       all source skills under Skills/** and Plugins/**
Default flat surface:    current bounded allowlist behavior
Rooted surface:          small set of visible root skill sets
Local plugin view:       individual plugin skills stay separately browsable
Skill scopes:            global baseline + project overlays + local plugins
Latent modules:          selected by bounded routers, not projected directly
Validation:              budget gates prevent hidden context bloat
Improvement loop:        workouts and amendments improve modules after routing exists
Wave 1 modes:            flat + rooted only
```

## Current-State Baseline

The spec is anchored to the live repository state as of 2026-04-24.

`python3 bin/ask skills budget --json` currently reports:

```json
{
  "default_visible_count": 18,
  "catalog_default_count": 18,
  "advanced_visible_count": 105,
  "advanced_visible_warn": 60,
  "default_visible_max": 30,
  "policy_identity": "ccc42d9df4a2db2e",
  "first_level_bridge_skills": [],
  "status": "pass"
}
```

The default-visible skills are the bounded flat allowlist from selection policy,
not the full advanced-visible catalog. The advanced-visible count is already
above the informational warning threshold, so the refactor should reduce future
runtime selection pressure without treating the current default projection as an
emergency failure.

The system bridge lane is distinct from normal first-level skill visibility. It
currently includes:

```text
imagegen
openai-docs
plugin-creator
plugin-installer
skill-creator
skill-installer
```

The baseline report is a required migration artifact. If these counts drift
before implementation starts, the first implementation PR must regenerate the
baseline rather than copying the numbers above as constants.

## Problem Statement

The repository already has the core ingredients for a scalable skill catalog:
canonical source folders, a bounded selection policy, runtime projection, CLI
wrappers, budget checks, validation gates, and eval planning. The current problem
is not that every catalog skill is loaded by default. Live repo checks show a
bounded flat default surface: `ask skills budget --json` reports 18 default-visible
skills, while the advanced/catalog-facing surface is much larger.

The remaining scaling issue is that the runtime model is still expressed as a
flat skill surface. Flat projection works for small curated sets, but it becomes
harder to operate when the catalog contains many related atoms, molecules,
routers, references, and plugin-backed workflows. Without a projection model that
separates visible roots from latent modules, agents can drift toward duplicative
skill descriptions, accidental first-level exposure, and context-heavy routing.

The v2 projection should preserve the existing context-pressure controls while
adding a tree-shaped runtime option that exposes only short root skill sets and
loads child modules selectively.

## Goals

- Add explicit runtime projection modes without changing the initial default.
- Preserve current flat projection behavior as a compatibility and rollback path.
- Add a rooted projection where Codex-visible entries are root skill sets, not
  every latent module.
- Keep hidden/system and primary-runtime bridge lanes governed separately from
  first-level skill visibility.
- Preserve separately browsable local plugin skills for human/operator use, with
  a shape that matches OpenAI-curated plugins.
- Support global skills and project-level skills with explicit precedence,
  ownership, and budget reporting.
- Generate or validate latent skill-set manifests without hand-editing derived
  runtime surfaces.
- Add bounded routers that return shortlists and selected source paths, not full
  catalogs or skill bodies.
- Extend existing budget and validation infrastructure instead of creating a
  disconnected governance path.
- Stage workouts and amendment loops after projection and routing are measurable.
- Defer `hybrid` mode until rooted mode has real evidence that a small direct
  emergency allowlist is needed.

## Required Invariants

- Canonical skill sources stay under `Skills/**` and `Plugins/**`.
- Runtime projection surfaces remain generated, disposable, and reproducible.
- The default mode remains `flat` until rooted mode passes explicit cutover
  gates.
- `flat` mode parity is a release blocker for all projection-mode PRs before the
  default flip.
- System bridge skills are not counted as ordinary root skill sets unless a
  later migration explicitly changes their ownership.
- Primary-runtime bridge folders are reported separately from user-authored root
  skill sets.
- Human-facing local plugin skill layout is distinct from Codex-visible runtime
  projection; keeping plugin skills separately browsable must not imply that all
  plugin skills are first-level runtime skills in rooted mode.
- Global skills provide the reusable baseline; project-level skills provide
  repo-specific overlays; projection reports must show which scope contributed
  each visible or latent skill.
- Project-level skills may override or shadow global skills only through an
  explicit conflict policy that is reported and validated.
- Manifest generation never silently drops a skill; unmapped skills are reported
  and eventually fail validation.
- Routers output references to modules, not module bodies.
- Workouts and telemetry are never projected into normal runtime context.
- Context budget improvements cannot be achieved by hiding runtime exposure from
  reporting.

## Non-Goals

- Do not rewrite individual skill bodies in the first implementation wave.
- Do not remove the current flat projection until rooted projection is validated.
- Do not hand-edit `.agents/skills/**`, `skills-codex/**`, plugin cache output,
  or other derived runtime surfaces.
- Do not introduce a standalone eval universe disconnected from existing eval
  plans, validation, or `ask` command contracts.
- Do not change plugin marketplace or plugin package protocols unless a later
  spec explicitly scopes that work.
- Do not collapse hidden/system bridge skills into ordinary root skill sets
  without a separate compatibility decision.
- Do not implement `hybrid` mode in wave 1 unless a named first consumer and
  failing rooted-only acceptance case are documented.

## System Boundary

### Owned Surfaces

- `Infrastructure/scripts/lifecycle-and-sync/selection_policy.py`
- `Infrastructure/scripts/lifecycle-and-sync/skill_discovery.py`
- `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh`
- `Infrastructure/scripts/lib/ask/commands/skills.py`
- `Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py`
- `Infrastructure/scripts/validate_all.sh`
- New manifest, router, and root-skill generation scripts under
  `Infrastructure/scripts/lifecycle-and-sync/`
- New budget fixtures and tests under the existing infrastructure test layout
- Documentation under `Docs/specs/`, `Docs/architecture/`, and `Docs/runbooks/`

### Out of Scope

- Runtime behavior inside the Codex desktop app.
- Provider-specific plugin package protocols.
- Broad skill-content hardening outside metadata needed for manifests.
- Unrelated branch, release, or provider cleanup.

## Architecture Decisions

### AD-001: Keep `flat` as the Initial Default

Decision: projection mode defaults to `flat` until rooted projection passes all
acceptance gates.

Rationale: current default projection is already bounded and passing budget
validation. Changing the default before parity, rollback, and workout evidence
would increase operational risk without immediate user benefit.

### AD-002: Use One Canonical Projection Engine

Decision: the desired end state is one projection implementation used by both
`sync_skills.sh` and `ask skills sync`.

Rationale: the repo currently has shell and Python projection paths. Projection
modes introduce enough state that duplicate implementations would create a high
drift risk. If unification is not possible in the first PR, parity tests are
mandatory until unification lands.

Wave-1 boundary: implementation must choose one of these two options before
changing projection behavior:

- Add `Infrastructure/scripts/lifecycle-and-sync/projection_engine.py` and have
  both command surfaces call it.
- Make `sync_skills.sh` delegate projection inventory and mutation behavior to
  `bin/ask skills sync`.

Any other boundary requires updating this spec or the implementation plan before
code changes start.

### AD-003: Treat Root Skills as Routing Entrypoints

Decision: root skills classify and route; they do not summarize all child
modules.

Rationale: listing child modules recreates flat-surface context pressure inside a
single larger prompt. The root body must stay small and point to bounded routing.

### AD-004: Make Metadata Enforcement Progressive

Decision: missing skill-set metadata is advisory during the first migration wave
and becomes a validation failure only after baseline mapping coverage exists.

Rationale: immediate hard failure across a large catalog would force noisy
metadata churn before projection mechanics are proven.

### AD-005: Keep Workouts Post-Projection

Decision: workouts are not first-wave projection infrastructure. They begin after
surface reports, projection modes, manifests, routers, and budget gates are
measurable.

Rationale: workouts need stable routing and budget signals to produce useful
amendment evidence.

### AD-006: Keep Wave 1 to `flat` and `rooted`

Decision: wave 1 implements only `flat` and `rooted`. `hybrid` is a deferred
mode, not an initial implementation requirement.

Rationale: `hybrid` adds policy surface, allowlist semantics, fixtures, and
failure modes before rooted projection has proven a real emergency-lane gap. The
current rollback path is `flat`, so rooted does not need hybrid to ship safely.

Deferred trigger: implement `hybrid` only if rooted mode cannot support a
documented production workflow and the workflow cannot safely use hidden/system
or primary-runtime bridge lanes.

## Core Domain Model

### `ProjectionMode`

The projection strategy used when generating `.agents/skills/**`.

Allowed canonical values:

```text
flat
rooted
```

Compatibility aliases may be accepted at the CLI boundary:

```text
skill-tree -> rooted
```

Deferred values:

```text
hybrid
```

`hybrid` is intentionally outside wave 1. Any plan that includes it must name the
first consumer and prove why `flat` rollback plus `rooted` projection is
insufficient.

### `RuntimeSurfaceReport`

Machine-readable snapshot of what the runtime exposes. It must distinguish:

- Default-visible canonical skills.
- Advanced/catalog-visible skills.
- Hidden/system bridge skills.
- Primary runtime bridge folders.
- Plugin runtime cache exposure.
- First-level `.agents/skills` entries.
- Generated root skill sets.
- Estimated metadata and description budget cost.
- Policy identity.

### `SkillSetRoot`

A short Codex-visible root skill that classifies a user task and delegates to a
bounded router. It is not a manifest dump and must not list every child skill.

### `LatentSkillModule`

A canonical skill source that remains available to routers and humans, but is not
projected as a first-level runtime skill in rooted mode.

### `LocalPluginSkillView`

A human/operator-facing view where local plugin skills remain separately
browsable, matching the OpenAI-curated plugin convention of one visible skill
folder per plugin skill. This view is for inspection, authoring, and local
operator navigation; it is not the same as the rooted Codex-visible runtime
projection.

### `SkillScope`

The ownership level of a skill before projection:

```text
global
project
local-plugin
system
primary-runtime
```

`global` skills are reusable defaults available across projects. `project`
skills are repository-specific additions or overrides. `local-plugin` skills are
plugin-packaged skills that remain separately browsable. `system` and
`primary-runtime` are governed bridge lanes and are not ordinary user-authored
skill scopes.

### `ProjectSkillOverlay`

A repo-local skill layer that can add project-specific skills, customize routing
metadata, or intentionally shadow a global skill. Shadowing must be declared in
projection output so agents can see why a project-specific skill won over a
global baseline skill.

### `SkillsetManifest`

A generated JSONL index for one root skill set. Each entry maps exactly one
canonical module to exactly one root skill set.

### `SkillsetRouterDecision`

Small JSON output from the router. It identifies a selected module and at most
three candidates. It must never print the full manifest or full skill body.

### `ContextBudgetPolicy`

Budget configuration and validation logic for root count, root description size,
root body size, first-level exposure, router output size, and loaded-module count.

### `Workout`

An eval harness for measuring routing and skill-instruction behavior. Workouts
are not runtime skills and must not be loaded into normal runtime context.

### `AmendmentProposal`

A controlled patch proposal created from workout evidence. Promotion requires
metric improvement without context-budget regression.

## Lifecycle State Machine

### Projection Mode Lifecycle

```text
unsupported
  -> parsed
  -> dry_run_available
  -> mutation_available
  -> validation_gated
  -> rollout_candidate
  -> default
  -> deprecated_or_retained_fallback
```

State requirements:

- `parsed`: CLI and environment values normalize to canonical mode names.
- `dry_run_available`: mode can produce an inventory without writing runtime
  surfaces.
- `mutation_available`: mode can generate derived runtime surfaces.
- `validation_gated`: budget and ownership validators can pass and fail fixtures
  for the mode.
- `rollout_candidate`: docs, rollback, and at least three diagnostic workouts
  pass.
- `default`: mode is the default for sync commands.
- `deprecated_or_retained_fallback`: old mode is either retained with support
  commitments or deprecated with a removal plan.

### Skill Module Metadata Lifecycle

```text
untagged
  -> inferred
  -> declared
  -> validated
  -> enforced
```

State requirements:

- `untagged`: no skill-set metadata exists.
- `inferred`: generator can infer mapping and reports that it did so.
- `declared`: canonical skill frontmatter declares the mapping.
- `validated`: declared mapping agrees with generated manifest rules.
- `enforced`: missing or invalid mapping fails validation.

### Amendment Lifecycle

```text
observed_failure
  -> classified_failure
  -> proposed_patch
  -> workout_rerun
  -> scorecard_compared
  -> accepted
  -> promoted
  -> rolled_back
```

Rollback must be possible from every accepted or promoted amendment.

## Functional Contracts

### Runtime Surface Report

The existing `ask skills budget --json` command is the first-class reporting
surface for wave 1. Extend this command first. Do not add a sibling
`ask skills surface --json` command unless the implementation proves that a
backward-compatible extension would make the budget schema too large or
confusing.

New reporting commands are deferred until both are true:

- `ask skills budget --json` cannot carry the runtime surface fields without
  breaking existing consumers.
- The new command has a schema, tests, and docs in the same PR that introduces
  it.

Required fields:

```json
{
  "projection_mode": "flat",
  "policy_identity": "string",
  "default_visible_count": 18,
  "advanced_visible_count": 105,
  "catalog_default_count": 18,
  "root_skill_set_count": 0,
  "first_level_default_entries": [],
  "hidden_system_entries": [],
  "primary_runtime_entries": [],
  "plugin_runtime_entries": [],
  "system_bridge_skills": [],
  "duplicate_default_names": [],
  "largest_descriptions": [],
  "unmapped_skill_names": [],
  "estimated_description_words": 0,
  "estimated_description_tokens": 0,
  "status": "pass",
  "budget_status": "pass"
}
```

Existing consumers may continue reading `status`; `budget_status` is added as
the explicit runtime-budget field and must not remove or rename `status` during
the compatibility phase.

The report must not assume that all catalog skills are first-level runtime
entries. It must report observed runtime state and selection-policy state
separately.

### Projection Modes

`flat` mode:

- Preserves current behavior.
- Projects the existing default-visible allowlist.
- Keeps current hidden/system and primary runtime lanes.
- Remains the default until rooted projection passes all preconditions.

`rooted` mode:

- Projects only root skill-set entries as normal first-level runtime skills.
- Keeps hidden/system bridge skills under their existing governed lane.
- Keeps primary-runtime bridge folders governed separately from root skill sets.
- Does not project individual latent canonical skills as first-level entries.
- Fails validation if latent modules appear directly in the rooted first-level
  surface.

`hybrid` mode:

- Is deferred in wave 1.
- Would project root skill sets plus a small emergency direct-skill allowlist.
- Must not be implemented without a named first consumer and acceptance test.
- Would use the same hidden/system and primary-runtime lane rules as rooted mode.
- Would fail validation if the emergency allowlist exceeds the configured budget.

### Sync Contract

Projection mode must be accepted through both environment and CLI plumbing:

```bash
SYNC_SKILLS_PROJECTION_MODE=rooted
ask skills sync --scope workspace --projection rooted
ask skills sync --scope workspace --projection flat
ask skills sync --scope user --projection rooted
ask skills sync --scope user --projection flat
ask skills sync --scope user --projection skill-tree
```

`rooted` is the canonical projection-mode name. `skill-tree` is accepted as a
compatibility alias for `rooted`.
`hybrid` must not be accepted as a mutating projection mode until the deferred
mode is explicitly promoted into scope.

Both `sync_skills.sh` and the Python `ask skills sync` implementation must be
kept consistent. The preferred implementation is one canonical projection engine
with both command surfaces delegating to it. If that is too large for the first
change, the first PR must at least add tests that prove the two paths agree.

Scope naming must be normalized before parity can be claimed:

- `ask skills sync --scope workspace` is the canonical runtime projection
  mutation scope.
- `ask skills sync --scope user` is the user-facing relink/sync scope.
- `sync_skills.sh --workspace` maps to `ask skills sync --scope workspace`.
- `sync_skills.sh --project-local` must either map to a documented `ask` scope
  or be retired behind the canonical projection engine.

Mutation commands must support a dry-run mode before changing derived runtime
surfaces.

Dry-run output must include:

- Projection mode after alias normalization.
- Would-create entries.
- Would-delete entries.
- Would-preserve bridge entries.
- Would-preserve system entries.
- Validation status.
- Any unmapped or ambiguous skills.

Mutation output must include:

- Projection mode after alias normalization.
- Counts for created, updated, removed, and preserved entries.
- Path to any generated report artifact.
- Clear warning if the command changed derived surfaces.

### Module Loading Contract

Rooted mode does not dynamically add latent modules to first-level
`.agents/skills/**`. The router returns repo-relative canonical `source_path`
values, and the agent loads only those canonical files for the current task.

Wave-1 loading rules:

- A selected module is loaded by reading its `source_path`.
- The selected module may load only directly referenced files needed to execute
  its own contract.
- Loading a selected module must not project, symlink, or copy the module into
  first-level `.agents/skills/**`.
- A root skill may load at most `modules.max_loaded_modules_per_task` selected
  modules.
- If router status is `low_confidence`, `no_match`, `invalid_skill_set`, or
  `manifest_missing`, the root skill must stop and ask for clarification or use
  the documented fallback path instead of loading a module authoritatively.
- Module loading must preserve the existing hidden/system and primary-runtime
  bridge lanes; those lanes are not latent-module loading mechanisms.
- Local plugin skills may remain individually browsable in their plugin package
  layout, but rooted runtime loading still goes through the selected canonical
  `source_path` returned by the router.

### Skill Scope and Precedence Contract

Projection must resolve skills from multiple scopes deterministically.

Scope order for user-authored skills:

```text
project > local-plugin > global
```

Bridge lanes are resolved separately:

```text
system
primary-runtime
```

Rules:

- Project-level skills may add new skills without modifying global skill sources.
- Project-level skills may shadow global skills only when the projection report
  records `shadowed_global_skill`, the project source path, and the global source
  path.
- Local plugin skills remain separately browsable in plugin layout and may
  contribute latent modules or root candidates, but browseability alone does not
  make them first-level rooted runtime entries.
- Name collisions across project, local-plugin, and global scopes must be
  reported. Unresolved collisions fail projection.
- Global skills should remain generic and reusable; project skills should carry
  repository-specific workflows, commands, constraints, and local vocabulary.
- A project overlay must not mutate global skill source files.
- Runtime budget reports must show visible counts by scope and must identify
  shadowed or suppressed entries.

Recommended project skill source path:

```text
Skills/project/<skill>/SKILL.md
```

This path is a canonical project-local source, not a generated runtime
projection. It intentionally lives outside `.agents/**` so project skills remain
trackable repo source and do not collide with generated runtime projection
ownership.

### Root Skill Contract

Each root `SKILL.md` must satisfy:

- Frontmatter `name` matches the root skill set id.
- `description` is 35 words or fewer.
- Body is 250 words or fewer.
- Body includes explicit "use for" and "do not use for" boundaries.
- Body instructs the agent to run the router and load only selected modules.
- Body does not enumerate every child module.
- Body does not embed the full manifest.

Required root body structure:

```md
---
name: <root-id>
description: <35 words or fewer>
---

Use for: <bounded scope>

Do not use for: <explicit exclusions>

Process:
1. Classify the task.
2. Run the bounded router for this root.
3. Load only selected module paths.
4. Stop if routing confidence is too low.
```

Root files may mention representative task shapes, but must not include a full
child inventory.

### Manifest Contract

Generated manifests live outside normal runtime context. Canonical location:

```text
.skillsets/<skill-set>/manifest.jsonl
```

Manifest input set for wave 1:

- Include all non-system canonical skills returned by existing discovery as
  advanced/catalog-visible skills.
- Include project-level skills from the chosen project-skill source path.
- Exclude hidden/system bridge skills from ordinary root manifests; report them
  in the runtime surface report instead.
- Exclude primary-runtime bridge folders from ordinary root manifests; report
  them in the runtime surface report instead.
- Include plugin-backed canonical skills only when discovery classifies them as
  advanced/catalog-visible skill entries, not merely because they exist in
  `Plugins/cache/**`.
- Preserve local plugin package skill layout for human browsing even when those
  plugin skills are represented as latent modules in rooted mode.
- Treat any discovered skill that cannot be classified into one of these buckets
  as `unmapped` and report it before generation succeeds.

Each JSONL entry must include:

```json
{
  "id": "verification-before-completion",
  "skill_set": "agent-ops",
  "scope": "global",
  "level": "atom",
  "source_path": "Skills/agent-ops/verification-before-completion/SKILL.md",
  "triggers": ["verify work", "completion check"],
  "exclusions": ["general planning"],
  "risk": "low",
  "owner": "Skills",
  "source_kind": "canonical-skill",
  "metadata_status": "declared",
  "shadowed_by": null,
  "runtime_visibility": "latent"
}
```

Rules:

- Every default/catalog module maps to exactly one skill set.
- `level` is one of `atom`, `molecule`, `compound`, `router`, or `reference`.
- Missing metadata is reported in the first migration wave.
- Missing metadata becomes a validation failure after the migration cutoff.
- `metadata.skill-type` remains a separate concept and must not be overloaded.
- Manifest rows are generated, sorted deterministically, and reproducible.
- Manifest generation reports inferred mappings separately from declared
  mappings.
- Duplicate `id` values within a skill set fail validation.
- A single `source_path` mapped to more than one skill set fails validation unless
  an explicit exception file exists.
- Scope collisions are reported with project, local-plugin, and global source
  paths.

### Router Contract

Routers may be generated per skill set or implemented as one shared script:

```bash
printf '%s\n' "verify this implementation is complete" | \
  python3 <agent-skills-root>/Infrastructure/scripts/lifecycle-and-sync/route_skillset.py \
  --skill-set agent-ops \
  --skillsets-dir <agent-skills-root>/.skillsets \
  --task-stdin \
  --top-k 3 \
  --json
```

`--task "..."` may exist for non-sensitive examples and tests only. Real routing
must support `--task-stdin` or `--task-file` so raw task text does not leak via
shell history, process listings, or terminal telemetry.

Required behavior:

- `top_k` is capped at 3.
- Output includes one selected module when confidence is sufficient.
- Output includes at most three candidates.
- Output includes `source_path` only for selected and candidate modules.
- Output does not include full manifests.
- Output does not include full skill bodies.
- Selected `source_path` must exist.
- Low-confidence output must be explicit rather than inventing certainty.

Required output schema:

```json
{
  "schema_version": 1,
  "status": "selected",
  "skill_set": "agent-ops",
  "query": {
    "redacted_task_summary": "verify implementation completeness",
    "top_k": 3
  },
  "selected": {
    "id": "verification-before-completion",
    "level": "atom",
    "source_path": "Skills/agent-ops/verification-before-completion/SKILL.md",
    "confidence": 0.82,
    "reason": "Task asks for completion verification."
  },
  "candidates": [
    {
      "id": "verification-before-completion",
      "source_path": "Skills/agent-ops/verification-before-completion/SKILL.md",
      "confidence": 0.82,
      "reason": "Task asks for completion verification."
    }
  ],
  "warnings": []
}
```

Allowed `status` values:

```text
selected
low_confidence
no_match
invalid_skill_set
manifest_missing
```

For `low_confidence` and `no_match`, the router may return candidates but must
not instruct the agent to load a module as authoritative.

### Context Budget Contract

Add or extend budget configuration with these policy controls:

```yaml
runtime_projection:
  max_root_skill_sets: 10
  max_root_description_words_total: 350
  max_root_body_words_each: 250
  count_system_bridge_as_roots: false
  count_primary_runtime_as_roots: false

routing:
  max_candidates_returned: 3
  forbid_full_manifest_output: true
  forbid_unrelated_skillset_load: true

modules:
  max_loaded_modules_per_task: 3
  max_module_body_words: 900

workouts:
  max_skill_context_tokens: 1500
```

Validation must fail when:

- Root skill-set count exceeds the configured limit.
- Combined root descriptions exceed the configured word budget.
- A root body exceeds the configured word budget.
- A root body lists all child modules.
- Latent skills appear directly in rooted first-level projection.
- Router output can emit a full manifest or more than three candidates.
- Generated runtime files are edited as canonical sources.

Budget tests must include positive and negative fixtures for:

- Too many root skills.
- Overlong root description.
- Overlong root body.
- Root body with a child inventory.
- Latent module exposed as first-level rooted projection.
- Router output with too many candidates.
- Router output containing manifest-shaped bulk data.

### Workout and Amendment Contract

Workouts start only after the projection, manifest, router, and budget gates are
measurable.

The first workout targets should be small and diagnostic:

- `agent-ops/verification-before-completion`
- `harness-engineering/he-router` or `harness-engineering/he-spec`
- One factory workflow, such as `skill-factory/skill-refactor`

Promotion rules:

- Pass rate improves.
- Flake rate does not regress.
- Wall-clock time does not materially regress.
- Context budget remains within limits.
- Patch is minimal and targeted.
- Validation passes.

Any accepted amendment must record previous hash, new hash, score before, score
after, rationale, evidence, and rollback command.

## Data Ownership and Generated Surfaces

Canonical inputs:

- `Skills/**`
- `Plugins/**`
- `Infrastructure/scripts/lifecycle-and-sync/**`
- `Infrastructure/scripts/lib/ask/**`
- `Infrastructure/GOVERNANCE/**`
- `Docs/**`

Generated or derived outputs:

- `.agents/skills/**`
- `skills-codex/**`
- `.skillsets/**`
- `.skill-telemetry/**`
- `Infrastructure/artifacts/runtime-surface/**`
- `Infrastructure/artifacts/skill-workouts/**`

Canonical artifact ownership:

| Artifact Class | Canonical Path | Committed | Generator | Validator | Edit Rule |
| --- | --- | --- | --- | --- | --- |
| Runtime projection | `.agents/skills/**` | No, except explicitly tracked workflow files already allowed by repo policy | `ask skills sync` or canonical projection engine | Runtime budget and path ownership validators | Never hand-edit |
| Generated command handles | `.agents/skills/<handle>/SKILL.md` for command-visible non-root handles | No, except when explicitly committed as generated projection output by repo policy | Command-surface generator under `Infrastructure/scripts/lifecycle-and-sync/` | `ask skills handles --check --json` and handle proof gates | Never hand-edit; regenerate from rooted manifests |
| Project skill source | `Skills/project/<skill>/SKILL.md` | Yes when used by a repo | Project skill authoring workflow | Skill audit and projection validators | Edit as project-local canonical source |
| Local plugin skill view | `Plugins/<plugin>/skills/<skill>/SKILL.md` or installed plugin-equivalent skill folders | Yes when part of a canonical local plugin package | Plugin authoring/sync workflow | Plugin audit and skill audit validators | Edit canonical plugin source, not generated cache |
| Plugin runtime mirror | `~/plugins/<plugin>`, `<codex-profile>/Plugins/<plugin>` | No | `ask plugins sync-local-runtime` and `ask skills sync --scope user --projection rooted` | Runtime sync reports and plugin diagnostics | Replace copied mirrors after any canonical plugin or marketplace update |
| Skill-set manifests | `.skillsets/<skill-set>/manifest.jsonl` | Yes, after generator/provenance exists | Manifest generator under `Infrastructure/scripts/lifecycle-and-sync/` | Manifest validator and budget validator | Never hand-edit |
| Runtime surface reports | `Infrastructure/artifacts/runtime-surface/**` | No | `ask skills budget --json` or follow-on report command | JSON schema and budget validator | Never hand-edit |
| Workout scorecards | `Infrastructure/artifacts/skill-workouts/**` | No by default | Workout runner | Workout score validator | Never hand-edit |
| Amendment decisions | `.skill-telemetry/amendments/**` | No by default until governance decides otherwise | Amendment workflow | Amendment validator | Never hand-edit |

Rules:

- Generated surfaces must include enough provenance to identify the generator,
  projection mode, policy identity, and source revision when practical.
- Generated surfaces must not be the only place where source-of-truth
  configuration exists.
- Validators must flag hand-edited generated runtime files where the repo already
  has ownership rules for derived paths.
- Local plugin skill browseability is a source-layout/user-experience
  requirement. It must be preserved without counting every local plugin skill as
  a rooted first-level runtime entry.
- Plugin runtime mirrors are copied runtime surfaces, not canonical plugin
  sources. After changing `Plugins/<plugin>` or `Plugins/marketplace.json`, the
  mirror replacement command must run before claiming Codex runtime behavior is
  updated.
- Generated command handles are runtime pointers for `$<handle>` mentionability.
  They are generated from rooted manifests and must not be treated as full
  workflow sources.
- Project skill sources are canonical within their repository and may be
  committed when a project needs repo-specific skills.
- Global skill sources must not be edited to satisfy one project's local
  workflow; use project skill overlays instead.
- A generated artifact may be committed only when the repo already treats that
  artifact class as committed state or this spec's implementation plan explicitly
  adds that policy.
- If implementation discovers that `.skillsets/**` should be ephemeral rather
  than committed, the plan must update this ownership table before writing code.
- The ownership table is authoritative. Later sections must reference these
  paths rather than introducing alternate candidate locations.

## Migration and Cutover Rules

### Phase Gates

The migration must proceed through these gates:

```text
G0 baseline_reported
G1 mode_parsed_flat_default
G2 flat_parity_proven
G3 rooted_dry_run_available
G4 rooted_mutation_available
G5 manifests_complete_or_advisory_reported
G6 routers_bounded
G7 budget_validator_enforced
G8 workouts_pass
G9 rooted_soak_passed
G10 default_flipped
```

No gate may be skipped. If a later implementation discovers that two gates must
merge, the plan must explicitly preserve the verification evidence for both.

### Cutover Preconditions

`rooted` cannot become the default until:

- `flat` rollback command is documented.
- `flat` parity tests pass.
- Rooted projection validation passes.
- Router validation passes.
- Five consecutive runs of the same validation command set pass on the same
  branch after rooted mutation support lands.
- Rooted mode has a committed or artifacted soak record for at least three
  representative non-default sync/report cycles.
- Each soak record includes timestamp, git SHA, projection mode, exact command,
  validation result, runtime surface report artifact path, and runtime surface
  report hash.
- No P0/P1 routing regression remains open.
- At least three diagnostic workouts pass with scorecards.
- Docs describe `flat`, `rooted`, any `skill-tree` alias, and explicitly state
  that `hybrid` is deferred.
- Generated-surface ownership is documented.
- Existing user/system bridge lanes are preserved or explicitly migrated.

### Default Flip Gate

Forward command contract:

```bash
ask skills sync --scope workspace --projection rooted
ask skills sync --scope user --projection rooted
```

Rollback command contract:

```bash
ask skills sync --scope workspace --projection flat
ask skills sync --scope user --projection flat
```

Default flip must be reverted if any of these occur before the first stable
release after cutover:

- Core `ask skills` commands are blocked by rooted projection.
- Rooted projection exposes latent modules at first level.
- System or primary-runtime bridge lanes disappear.
- Router `low_confidence` or `no_match` outcomes block a workflow that flat mode
  handled and no documented fallback exists.
- Validation fails in a way that flat rollback resolves.

### Rollback Command Contract

The implementation must document a rollback command equivalent to:

```bash
ask skills sync --scope workspace --projection flat
ask skills sync --scope user --projection flat
```

If environment variables are part of runtime selection, rollback docs must also
include the environment override required to restore flat behavior.

## Security and Safety Requirements

- Router task input may contain secrets or sensitive repo context; persisted
  router logs must store a redacted task summary, not the raw task by default.
- Manifests must not include secret values, environment variables, tokens, or
  private user data extracted from skill bodies.
- Telemetry must not store raw prompts unless an explicit debug mode is enabled.
- Generated reports must avoid leaking absolute home-directory paths unless the
  existing repo convention requires them for local-only artifacts.
- Workouts must prevent shortcuts such as editing verifier files, hardcoding
  dynamic flags, or bypassing validation.
- Amendment proposals must not auto-apply patches without validation and rollback
  metadata.
- Any future remote or network-backed router is out of scope for this spec and
  requires a separate security review.

## Failure Model

### Policy Drift

Selection policy and runtime projection disagree. Recovery: report policy
identity, compare sync paths, and fail validation until the mismatch is resolved.

### Sync Path Divergence

`sync_skills.sh` and `ask skills sync` produce different runtime surfaces.
Recovery: make one path delegate to the other or add parity tests that fail on
different file inventories.

### Latent Exposure

Rooted mode exposes individual latent modules at first level. Recovery: fail
budget validation and regenerate projection from canonical manifests.

### Router Over-Output

Router returns a catalog-sized response. Recovery: fail router tests and budget
validation; cap and schema-check all JSON output.

### Metadata Gaps

Skills are missing `skill_set`, `level`, triggers, or exclusions. Recovery:
report as advisory during migration, then escalate to validation failure after
cutoff.

### Workout Flake

Workout passes once but is unreliable. Recovery: require scorecards with pass
rate and flake rate before amendment promotion.

### Rooted Default Regression

Rooted mode blocks normal work after becoming default. Recovery: retain `flat`
mode escape hatch and document rollback command.

### Bridge Lane Regression

System or primary-runtime bridge skills disappear, move into ordinary root
counts, or become duplicated at first level. Recovery: fail runtime-surface
validation and restore lane-specific projection rules.

### Stale Baseline

The baseline counts in this spec drift before implementation begins. Recovery:
regenerate the baseline in the first reporting PR and update docs before using
the old numbers for acceptance.

### Generated Artifact Drift

Generated manifests or runtime projections are stale relative to canonical
sources. Recovery: fail provenance or regeneration checks and rerun the generator.

### Telemetry Leakage

Telemetry captures raw task prompts, secrets, or unnecessary absolute paths.
Recovery: redact records, disable persistence by default, and add regression
fixtures before re-enabling telemetry.

## Observability

Required machine-readable surfaces:

- `ask skills budget --json`
- Router JSON output
- Manifest generation report
- Context budget validator output
- Workout scorecards
- Amendment decision records

Telemetry and workout records must not be projected into normal runtime context.
They must use the canonical artifact paths from the ownership table:

```text
.skill-telemetry/
Infrastructure/artifacts/skill-workouts/
Infrastructure/artifacts/runtime-surface/
```

Recommended event fields for generated reports:

```json
{
  "schema_version": 1,
  "timestamp": "2026-04-24T00:00:00Z",
  "projection_mode": "rooted",
  "policy_identity": "ccc42d9df4a2db2e",
  "source_revision": "git-sha-or-null",
  "generator": "route-or-sync-command",
  "status": "pass",
  "counts": {},
  "violations": [],
  "advisories": []
}
```

## Acceptance Criteria

- Flat mode produces the same default-visible runtime surface as today.
- Runtime surface reporting distinguishes default-visible, advanced-visible,
  hidden/system, primary-runtime, and plugin-cache surfaces.
- Runtime surface reporting distinguishes global, project, local-plugin, system,
  and primary-runtime scopes.
- Local plugin skills remain separately browsable in local plugin packages, in
  the same spirit as OpenAI-curated plugin skill folders.
- Project-level skills can add or explicitly shadow global skills without
  mutating global skill sources.
- Projection mode can be selected by CLI and environment variable.
- Rooted mode projects no more than 10 visible root skill sets.
- Rooted mode does not project individual latent modules as first-level skills.
- Hybrid mode is documented as deferred and is not required for wave 1.
- Root skills obey description and body budgets.
- Manifest generation maps every in-scope module to exactly one root skill set.
- Router output returns at most three candidates and no full manifest.
- Router input supports `--task-stdin` or `--task-file` for sensitive task text.
- Module loading reads selected canonical `source_path` files without projecting
  latent modules into first-level runtime surfaces.
- Budget validation is wired into existing repo validation.
- Workouts are introduced after routing and budget validation, not before.
- The default flips from `flat` to `rooted` only after validation, docs, and at
  least three diagnostic workouts pass.
- The implementation documents rollback to `flat`.
- Router and telemetry persistence redact raw task text by default.
- Generated artifacts include provenance or a documented reason why provenance is
  unavailable.

## Verification Matrix

| Area | Expected Verification |
| --- | --- |
| Baseline report | `python3 bin/ask skills budget --json` reports current bounded flat surface |
| Flat parity | Dry-run sync in `flat` mode matches existing first-level default projection |
| Mode parsing | CLI accepts `flat`, `rooted`, and optional `skill-tree` alias; `hybrid` is rejected or explicitly marked deferred |
| Projection dispatch | `--projection` reaches the sync/projection engine as a distinct value and cannot be parsed then ignored |
| Sync parity | Shell sync and Python `ask skills sync` produce equivalent inventories |
| Scope mapping | Shell and Python sync scopes have a documented canonical mapping before parity is claimed |
| Scope precedence | Project skills shadow global skills only when explicitly reported and validated |
| Local plugin browseability | Local plugin packages expose separate skill folders for human inspection without increasing rooted first-level runtime count |
| Rooted projection | Root count is within budget and latent modules are not first-level entries |
| Root budgets | Descriptions and bodies stay within configured word limits |
| Manifests | Every in-scope module maps exactly once and selected paths exist |
| Manifest provenance | Generated `.skillsets/**` rows include provenance and validators catch missing or stale provenance |
| Module loading | Selected canonical `source_path` is loadable without first-level latent projection |
| Router | Router emits valid JSON, at most three candidates, and no full manifest |
| Router input safety | Sensitive task input can be supplied through stdin or file without raw task text in argv |
| Budget validator | Validator fails seeded over-budget fixtures and passes valid rooted fixture |
| Validation integration | `bash Infrastructure/scripts/validate_all.sh --ephemeral` includes budget gate |
| Workout MVP | First workout records pass rate, flake rate, wall-clock, and context estimate |
| Workout CLI | `ask workouts list/run/score/promote` parse and dispatch before workout validation relies on them |
| Amendment loop | Promotion rejects patches that improve pass rate by exceeding context budget |
| Bridge preservation | System and primary-runtime bridge lanes are reported and preserved separately |
| Generated ownership | Validators or tests catch hand-edited derived runtime files where ownership policy applies |
| Rollback | Documented flat rollback command restores bounded flat projection |
| Redaction | Router or telemetry fixtures prove raw sensitive task text is not persisted by default |

## Open Questions

- What is the final root skill-set inventory for the first migration wave?
- Should `codex-primary-runtime` remain a separate primary-runtime lane forever,
  or become a governed root-like system lane later?
- When does missing skill-set metadata become a hard validation failure rather
  than an advisory migration report?
- Should rooted projection use repo-local roots only, plugin roots only, or a
  merged namespace with collision handling?
- What exact installed-plugin path should be treated as the local plugin skill
  browse view when source plugins and cache plugins both exist?
- What confidence threshold should cause router status to become
  `low_confidence`?

## Definition of Done

Phase A is complete when:

- Runtime surface reporting is accurate and checked into docs as a baseline.
- Projection mode plumbing exists and defaults to `flat`.
- Runtime surface reporting includes counts and collisions by skill scope.
- `flat` parity tests pass.

Phase B is complete when:

- Rooted projection can be generated in dry-run and mutation modes.
- Manifests and routers support selected module loading without context bloat.
- Local plugin skills remain separately browsable without becoming rooted
  first-level runtime entries.
- Project-level skills can be included as canonical project overlays without
  editing global skill sources.
- Context budget validation runs through existing validation entrypoints.
- Documentation explains flat, rooted, any skill-tree alias, and that hybrid is
  deferred.
- Security and redaction fixtures pass for router and telemetry paths.
- Generated-surface ownership rules are documented and enforced for the new
  artifact classes.

Phase C is complete when:

- At least three diagnostic workouts pass with scorecards.
- Five consecutive executions of the same validation command set pass on the
  same branch after rooted mutation support.
- Rooted non-default soak passes without P0/P1 regressions.
- Default projection flips to rooted with `flat` retained as rollback.

## Handoff to `he-plan`

Use this spec to create an incremental PR plan. The first implementation slice
should extend the existing budget/reporting surface before changing projection
behavior. The second slice should add projection-mode parsing and parity tests
while keeping the default `flat`.

Recommended planning order:

1. Extend runtime surface reporting.
2. Add projection-mode contract without behavior change for `flat` and `rooted`.
3. Add root skill-set generation behind dry-run.
4. Add latent manifests.
5. Add bounded router MVP.
6. Add context-budget validation fixtures and gate wiring.
7. Add workout MVP.
8. Add amendment proposal flow.
9. Flip default after preconditions pass.
10. Consider `hybrid` only after rooted has production evidence of an emergency
    direct-skill allowlist need.
