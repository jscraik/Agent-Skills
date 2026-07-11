# Skills Foundry Extraction And Skills SDK Separation Plan

Date: 2026-06-30; reconciled: 2026-07-11

## Purpose

Separate editable source from the Skills SDK pipeline without breaking existing
skill, plugin, SDK, Tessl, PR, or runtime lanes. The canonical target is two
external repositories: `~/dev/skills-foundry` for private editable source and
`~/dev/skills-sdk` for lifecycle tooling. This repository is transitional
evidence and pipeline implementation; it must not acquire new nested source or
SDK repository roots.

This plan is a migration-control artifact. It does not authorize repository
creation, initialization, extraction, runtime cutover, publishing, or a mass
move. Each mutation boundary needs its own acceptance and proof.

## Authority

The accepted architecture and implementation contract are recorded in:

- `/Users/jamiecraik/dev/jamie-brain/00-LLM Wiki/syntheses/Skills SDK And Foundry Architecture Decision - Current.md`
- `/Users/jamiecraik/dev/jamie-brain/00-LLM Wiki/syntheses/Skills SDK And Foundry Bounded Implementation Specification - Current.md`

The older local layout ADR remains historical evidence only. It is not source
topology authority when it conflicts with the external repository decision.

## Target Shape After Authorized Extraction

    ~/dev/skills-foundry/
      <direct Tessl project release units>

    ~/dev/skills-sdk/
      <Skills SDK lifecycle implementation>

    agent-skills/
      <legacy source candidates until extraction>
      <legacy nested SDK surface until repository separation>
      .harness/ <evidence and migration control only>

    ~/.codex/skills/ or <project>/.codex/skills/
      <immutable copied standalone installations>

    ~/.codex/plugins/
      <Codex-owned installed plugins>

## Migration Principles

1. Contract first, movement second.
2. Preserve package internals. Do not reshape a package while classifying it.
3. Source and installation stay separate; installed standalone skills are
   copies, never source symlink projections.
4. Preserve the root `./bin/ask` compatibility contract until characterization,
   migration proof, and any deprecation path are accepted.
5. Regenerate generated artifacts instead of promoting them to source.
6. Do one owner bucket per commit. Do not mix classification, rationalization,
   extraction, runtime changes, or PR cleanup.
7. Keep local, hosted PR, CircleCI, Tessl, registry, and runtime-install truth
   separate.

## Phase 0: Stabilize Current Branch

Exit criteria:

- Current PR stabilization is landed or explicitly parked.
- Dirty worktree buckets are triaged by owner.
- No unresolved merge-conflict strategy remains for the active branch.
- The layout validator passes on current HEAD.

Required command:

    python3 Infrastructure/scripts/validation-and-linting/validate_repo_layout.py --json

## Phase 1: Caller Inventory And Compatibility Contract

Do not move files yet. Inventory callers for legacy source candidates, SDK
implementation, generated evidence, runtime projections, and compatibility
entrypoints. Classify callers as internal imports, shell commands, ask routes,
CI or hook inputs, documentation links, generated inputs, runtime inputs,
Tessl staging, or external entrypoints.

Exit criteria:

- Caller inventory is portable and excludes generated evidence before scanning.
- Wrapper policy preserves only public entrypoints that must survive.
- The layout validator still passes.
- No new physical root move has occurred.

Checkpoint artifacts:

- `.harness/refactors/root-layout/caller-inventory.current.json`
- `.harness/refactors/root-layout/caller-inventory.current.md`
- `.harness/refactors/root-layout/compatibility-wrapper-policy.md`
- `.harness/refactors/root-layout/phase-1-first-bucket-selection.md`

The historical `brand` move is recorded separately. It does not authorize a
new source move or establish the external Skills SDK repository.

## Phase 2: Pre-Extraction Stabilization And Command/Service Rationalization

Complete the accepted stabilization receipt and command/service rationalization
before source admission inventory, repository creation, initialization, or
history extraction. Classify commands and services as retained lifecycle
surface, compatibility wrapper, generated projection, or deletion candidate;
deletion requires a separately approved, reversible batch.

Exit criteria:

- The stabilization receipt binds a clean worktree, SHA, command inventory,
  validation results, and excluded dirty state.
- Each command and service has one disposition and a caller/compatibility
  consequence.
- No source path has moved and no external repository has been initialized.

## Phase 3: Source Admission Inventory

Only after Phase 2 exits, do not move source yet. Classify every candidate as one of:

1. admitted private source release unit;
2. SDK lifecycle implementation;
3. generated projection or cache;
4. fixture, report, compatibility alias, or retained evidence; or
5. excluded material.

For each candidate bucket:

- bind a digest and owner to its disposition;
- prove it is canonical editable source before admitting it;
- reject generated projections, plugin caches, fixtures, reports, aliases, and
  runtime copies as source merely because of directory presence; and
- keep `skills-system` out of the source candidate set until its generated
  projection and compatibility-link ownership are independently resolved.

Exit criteria:

- Every candidate has one disposition and evidence reference.
- No source path is changed.
- The layout validator rejects new nested repository roots and runtime skill
  symlink projections.

## Phase 4: Repository Formation And Extraction Rehearsal

Complete the accepted stabilization receipt and command/service rationalization
before repository creation, initialization, or history extraction. Then, only
with explicit authorization:

1. create isolated, private extraction rehearsal output;
2. audit included and excluded paths, secrets, generated state, and history;
3. obtain independent QA and acceptance for the digest-bound extraction; and
4. create the external Foundry repository by history-preserving extraction.

The original source remains intact until extraction, SDK references, validation,
pilots, and rollback are accepted.

## Phase 5: Pilots, Runtime Cutover, And Retirement

Run standalone and plugin pilots before any runtime cutover. The separate
CircleCI, Tessl, registry, local installation, and independent-QA truth lanes
remain separate. Compatibility aliases and any later retirement require caller
proof, rollback, and separate authorization.

## Explicit Non-Goals

- Do not redesign package internals during migration.
- Do not collapse Tessl registry identity into repository source shape.
- Do not make `.agents` canonical source or an installed-skill root.
- Do not initialize Foundry, extract history, or change runtime installation
  under this plan alone.
- Do not move dirty worktree buckets as part of this plan.
- Do not treat a layout-validator pass as PR, registry, or runtime readiness.

## Pre-Migration Gate

Before any physical move, run:

    python3 Infrastructure/scripts/validation-and-linting/validate_repo_layout.py --json
    bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest -q tests/test_repo_layout.py
    uv run --python 3.12 python /Users/jamiecraik/dev/jamie-brain/tools/validate-skills-sdk-foundry-topology.py \
      --agent-skills-root <candidate-root> \
      --expected-agent-skills-head <candidate-head>

The move can start only when the relevant commands pass, the active branch has
a clean intentional migration scope, and the governing extraction authority is
explicit.
