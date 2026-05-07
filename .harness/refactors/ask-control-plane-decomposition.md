# Ask Control Plane Decomposition

# Refactor Classification

- orchestration simplification
- modularity correction
- cognition compression
- execution determinism
- moat reinforcement
- context-load reduction

# Problem Statement

`Infrastructure/scripts/lib/ask/commands/skills.py` has become the highest-risk structural choke point in the repository. It owns too many responsibilities: skill discovery, plugin cache behavior, catalog parity, projection coordination, command-surface behavior, proof/eval entrypoints, dynamic tool resolution, analytics, and CLI adaptation.

The operational issue is not file length alone. The issue is mixed bounded contexts behind one command module. Any skill lifecycle change can unexpectedly touch plugin cache state, runtime projection assumptions, catalog parity, command handles, and proof behavior.

Future-agent issue:

- agents must read a 3001-line file to understand small command behavior;
- local reasoning fails because responsibilities are interleaved;
- new feature logic tends to land in the same module because it is already the obvious place;
- refactors become risky because the blast radius is unclear.

Linear/execution issue:

- one Linear issue cannot safely represent the whole migration;
- many tiny issues would create coordination noise;
- the correct shape is one parent refactor program with staged service extraction.

Moat risk:

The repository's moat depends on trusted deterministic command contracts. If the command implementation becomes too dense for agents to reason about, the control plane stops being trustworthy.

# Root Cause Analysis

Why it emerged:

- `./bin/ask` and `ask commands` successfully became the canonical control plane.
- Skill lifecycle behavior grew quickly: list, resolve, audit, sync, projection, plugin cache, proof, and analytics all needed a command surface.
- Adding logic to the existing command module was faster than designing internal service boundaries.

Why it survived:

- Public behavior matters more than internal shape, so large-module risk stayed tolerable.
- Validation focused on command outcomes, not internal cohesion.
- The module continued working, which made the structural cost easy to defer.

Why current boundaries are insufficient:

- `commands/skills.py` is not only a CLI adapter.
- Service-like logic is not isolated behind importable, testable interfaces.
- Plugin cache, catalog, projection, proof, and tool-resolution concerns can change independently but are colocated.

Nature of issue:

- operational and accidental, not strategic;
- historically understandable;
- now harmful because the control plane is becoming the product spine.

# Evidence

Facts:

- `.harness/review/agent-skills-architecture-review.md` identifies `Infrastructure/scripts/lib/ask/commands/skills.py` as a 3001-line god command module.
- `.harness/triage/agent-skills-triage.md` ranks splitting `skills.py` as the first execution move.
- `.harness/strategy/agent-skills-strategy.md` says the first strategic execution move is structural: decompose `skills.py`.
- The strategy marks tactical internals safe to rewrite if public contracts and strategic boundaries are preserved.

Interpretation:

- `skills.py` is the primary source of change amplification in the skill lifecycle.
- The safest migration is service extraction while preserving command behavior.

Assumptions:

- Existing CLI behavior can be preserved with focused command smoke tests.
- Internal helpers can be moved incrementally without changing public JSON contracts.

# Architectural Impact

Affected systems:

- `./bin/ask` skill command surface;
- skill discovery;
- plugin cache refresh/report behavior;
- catalog parity;
- runtime projection coordination;
- command-handle validation;
- skill proof/eval entrypoints.

Likely files/directories touched:

- `Infrastructure/scripts/lib/ask/commands/skills.py`
- new `Infrastructure/scripts/lib/ask/services/skill_catalog.py`
- new `Infrastructure/scripts/lib/ask/services/skill_projection.py`
- new `Infrastructure/scripts/lib/ask/services/plugin_cache.py`
- new `Infrastructure/scripts/lib/ask/services/skill_proof.py`
- new `Infrastructure/scripts/lib/ask/services/skill_tool_resolution.py`
- tests or command smoke fixtures where they exist.

Blast radius:

- high, because many skill workflows route through this file.

Migration complexity:

- migration-risk, but controllable with behavior-preserving extraction.

Rollback difficulty:

- moderate if each extraction is small and public command output snapshots are retained.

Systems that must not be touched:

- public command names unless explicitly approved;
- `--json --robot` output contracts;
- source/projection semantics;
- command-handle semantics;
- selection policy semantics.

# Desired End State

`commands/skills.py` becomes a thin CLI adapter.

Service modules own coherent responsibilities:

- catalog service: source inventory, manifest/catalog parity, resolution inputs;
- projection service: generated/runtime projection coordination;
- plugin cache service: cache refresh/report/error handling;
- proof service: proof/eval payload assembly and proof taxonomy integration;
- tool resolution service: skill-builder/installer path and dynamic module resolution;
- command adapter: argument parsing, human/robot response shaping, exit code mapping.

Improved reasoning model:

- agents inspect a service file for one domain;
- command behavior remains stable;
- new feature logic has an obvious non-command home;
- validation can target services directly over time.

# Migration Strategy

Use staged extraction. Do not rewrite behavior first.

Sequencing:

1. Create service package skeleton with no behavior change.
2. Extract lowest-risk pure helper clusters first.
3. Extract plugin cache behavior.
4. Extract catalog/projection boundaries.
5. Extract proof/tool-resolution behavior.
6. Leave CLI adapters in `commands/skills.py`.
7. Add anti-regression checks preventing new feature logic in the command module while over threshold.

Coexistence rules:

- command module may call services during migration;
- old helpers may remain temporarily if moved callers are not complete;
- no public command removal;
- no JSON contract drift without explicit ADR.

Rollback strategy:

- each phase must be revertible independently;
- if command output changes unexpectedly, rollback the phase, not the program;
- keep pre/post command samples for skill list/resolve/audit/proof paths.

Linear milestone/parent issue shape:

- milestone: `Ask Control Plane Decomposition`
- parent issue: `Decompose skills command module into bounded services`
- small active set: one service extraction issue active at a time.

# Execution Phases

## Phase 1 — Boundary Identification

Objective:

Map functions in `skills.py` to service boundaries without moving code.

Affected systems:

- `commands/skills.py`

Expected risk:

- low.

Can run in parallel:

- no.

Validation requirements:

- no behavior change;
- record current command smoke outputs for representative skill commands.

Rollback conditions:

- none; this is analysis-only unless annotations are committed.

Linear mapping:

- child issue: `Map skills.py responsibilities to service boundaries`

Agent-safe:

- yes.

Human review required:

- no, unless boundary map is disputed.

## Phase 2 — Plugin Cache Service Extraction

Objective:

Move plugin cache refresh/report/error behavior behind `ask/services/plugin_cache.py`.

Affected systems:

- plugin cache behavior;
- skill command paths that refresh or report plugin state.

Expected risk:

- medium.

Can run in parallel:

- no.

Validation requirements:

- plugin-related skill command smoke tests;
- no changed public output unless explicitly snapshotted.

Rollback conditions:

- plugin cache refresh regression;
- import path instability;
- robot output contract drift.

Linear mapping:

- child issue: `Extract plugin cache service`

Agent-safe:

- assisted.

Human review required:

- yes.

## Phase 3 — Catalog And Projection Service Extraction

Objective:

Separate catalog/parity and projection coordination into explicit services.

Affected systems:

- catalog parity;
- runtime projection;
- command handle validation inputs.

Expected risk:

- high.

Can run in parallel:

- no.

Validation requirements:

- catalog parity doctor signal;
- runtime budget command;
- command handle validation;
- skill list/resolve behavior.

Rollback conditions:

- catalog parity false positives/negatives;
- projection sync drift;
- generated/source ambiguity.

Linear mapping:

- child issue: `Extract skill catalog and projection services`

Agent-safe:

- assisted.

Human review required:

- yes.

## Phase 4 — Proof And Tool Resolution Extraction

Objective:

Move proof/eval payload assembly and dynamic tool-resolution logic out of the command module.

Affected systems:

- `skills prove`;
- skill-builder/installer resolution;
- future proof taxonomy integration.

Expected risk:

- medium-high.

Can run in parallel:

- only after Phase 3 is stable.

Validation requirements:

- proof command samples;
- skill-builder/installer resolution smoke tests;
- no proof-level semantic changes unless ADR exists.

Rollback conditions:

- proof payload ambiguity;
- builder/installer lookup regressions.

Linear mapping:

- child issue: `Extract proof and tool-resolution services`

Agent-safe:

- assisted.

Human review required:

- yes.

## Phase 5 — Command Module Size And Drift Gate

Objective:

Prevent re-accumulation in `commands/skills.py`.

Affected systems:

- governance;
- future PR checks.

Expected risk:

- low-medium.

Can run in parallel:

- yes, after service extraction begins.

Validation requirements:

- docs/gate check for module threshold or explicit exception;
- no false block for trivial adapter changes.

Rollback conditions:

- gate blocks legitimate adapter-only fixes.

Linear mapping:

- child issue: `Add skills command module drift guard`

Agent-safe:

- yes.

Human review required:

- yes for threshold policy.

# Linear Mapping

Workspace/team: Jscraik

Team key: JSC

Top-level initiative: Dev Portfolio

Cross-repo project: Portfolio Ops

Repo-specific work: `agent-skills`

Target Linear project:

- `Agent Skills — Ask Control Plane Simplification`

Scope:

- repo-specific.

Belongs under `Portfolio Ops`:

- yes, because it changes the shared agent-control-plane pattern.

Affects `Dev Portfolio`:

- yes.

Recommended milestone:

- `Ask Control Plane Decomposition`

Recommended parent issue title:

- `Decompose skills command module into bounded services`

Recommended sub-issues:

- `Map skills.py responsibilities to service boundaries`
- `Extract plugin cache service`
- `Extract skill catalog and projection services`
- `Extract proof and tool-resolution services`
- `Add skills command module drift guard`

Suggested priority:

- urgent / P0.

Suggested labels:

- `architecture`
- `refactor`
- `agent-native`
- `control-plane`
- `migration-risk`

Dependencies:

- none for Phase 1;
- proof taxonomy should not block service extraction.

Project reactivation:

- yes if there is an existing dormant architecture/project lane.

Active set:

- keep small; one extraction child issue active at a time.

# Anti-Regression Constraints

Must not regress:

- public `./bin/ask` skill command names;
- `--json --robot` contracts;
- source/projection separation;
- catalog parity checks;
- runtime budget checks;
- command handle validation;
- plugin cache correctness.

Must not reappear:

- new feature logic added directly to `commands/skills.py`;
- service modules that become pass-through wrappers only;
- hidden dynamic imports without one owning service;
- proof semantics mixed with command formatting.

# Eval Requirements

Expected eval artifact:

`.harness/evals/agent-skills-ask-control-plane-decomposition-eval.md`

Required proof:

- before/after command output comparison for representative skill commands;
- module responsibility map;
- catalog parity pass or documented unrelated blocker;
- runtime budget pass;
- command handle validation pass;
- evidence that `commands/skills.py` no longer owns extracted responsibilities.

No related Linear parent issue should be closed without this eval artifact.

# Success Criteria

- `commands/skills.py` is a CLI adapter rather than a multi-context module.
- Plugin cache, catalog/projection, proof, and tool-resolution logic have clear homes.
- Public command behavior is preserved.
- Future agents can inspect one service for one concern.
- New feature logic has an obvious non-command destination.
- Command-module growth is guarded.

# Safe Rollback Conditions

Rollback if:

- public robot JSON changes without approval;
- catalog parity or projection sync behavior regresses;
- skill resolve/list/audit commands fail;
- plugin cache paths break;
- proof payloads lose semantic clarity.

Linear status if rollback is triggered:

- move active child issue to blocked;
- leave parent open;
- record failed phase and exact command output in the eval artifact.

# Future-Agent Guidance

Preserve:

- command contracts;
- service boundary intent;
- source/projection semantics.

Simplify further:

- pass-through service functions;
- duplicated helpers after extraction;
- unused compatibility shims.

Intentional complexity:

- command contract compatibility;
- source/projection protection.

Accidental complexity:

- mixed domain logic in command adapters.

Human review required:

- JSON contract changes;
- catalog/projection behavior changes;
- proof semantics changes.

# Related Systems

- `.harness/strategy/agent-skills-strategy.md`
- `.harness/triage/agent-skills-triage.md`
- `.harness/review/agent-skills-architecture-review.md`
- `Infrastructure/scripts/lib/ask/commands/skills.py`
- `Infrastructure/bin/ask`
- `Infrastructure/scripts/lifecycle-and-sync/selection_policy.py`
- `Infrastructure/scripts/lifecycle-and-sync/command_surface.py`
- future eval: `.harness/evals/agent-skills-ask-control-plane-decomposition-eval.md`
