# Repo Shape ADR: Foundry And Skills SDK Layout Boundary

Date: 2026-06-30

## Status

Accepted as a target architecture. Physical migration is deferred until the
current PR and dirty-worktree lanes are stabilized.

## Context

The repository currently carries several product roles in one top-level
namespace:

- canonical skill and plugin source packages;
- Skills SDK lifecycle implementation, schemas, validators, receipts, docs, and
  visual projections;
- runtime projections and local integration links;
- harness evidence, research, plans, reports, and PM thread handoffs;
- root governance and bootstrap files.

That shape has produced repeated source/projection confusion. Agents can mistake
runtime projections for editable source, compatibility symlinks for canonical
ownership, generated evidence for implementation truth, or the agent-skills
foundry role for the Skills SDK lifecycle contract.

## Decision

Adopt the following target architecture:

- foundry/ is the future canonical home for first-party skills, plugin-owned
  source packages, and system-skill overlays.
- skills-sdk/ is the future canonical home for the Skills SDK lifecycle engine,
  schemas, validators, product docs, visual artifacts, and brand material.
- .harness/ remains the evidence, planning, research, runtime-card, PM report,
  decision, and closeout surface.
- .agents/ remains a runtime projection and local integration surface in this
  repository. It is not editable skill source unless a separate owner repo
  declares it as project-local canonical source.
- Root remains a governance and bootstrap surface only.

The current paths Skills/, Plugins/, skills-system/, Infrastructure/, Docs/,
and artifacts/ remain legacy-compatible until explicit migration slices move
them.

## Symlink Policy

Symlinks are allowed only when classified:

- runtime_projection: generated or runtime-facing links such as
  .agents/skills/*.
- compatibility_alias: temporary root aliases such as scripts ->
  Infrastructure/scripts; these need an owner and migration path.
- external_runtime_link: local machine integration links such as personal
  plugin links or app-bundled plugin links.
- dependency_manager_link: ignored package-manager or virtualenv links.

Unknown symlinks block layout validation.

## Consequences

- The first implementation slice is a contract and validator, not a mass path
  move.
- New top-level directories must be classified before they are treated as source
  or evidence.
- Later migration PRs can move docs, SDK implementation, skills, and plugin
  roots one surface at a time with compatibility shims.
- Package internals such as SKILL.md, references/, scripts/, assets/, and evals/
  remain stable; repository layout and package projection layout are separate
  concerns.

## Validation

The target shape is enforced by:

- Infrastructure/config/repo-layout.v1.json
- Infrastructure/scripts/validation-and-linting/validate_repo_layout.py
- Infrastructure/tests/test_repo_layout.py
