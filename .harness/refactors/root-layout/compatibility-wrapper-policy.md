# Compatibility Wrapper Policy

Date: 2026-07-01

## Purpose

Define which legacy root entrypoints can survive during the foundry/ and
skills-sdk/ layout migration, and what proof is required before removing them.

This policy supports Phase 1 of the root-layout migration plan. It does not
authorize moving files.

## Phase 1 Reconciliation

The selected `brand/` bucket is complete: commit
`ed9d3fd840e540b2e1a5b625bfaf5e8993b6c16f` moved it to
`skills-sdk/brand/`. Its receipt is
`phase-2-brand-migration-report.md`. `brand/` is therefore neither a current
legacy root nor a candidate for a repeat move.

## Wrapper Classes

### Public Operator Entrypoints

Keep wrappers or compatibility aliases until every documented operator command
has a replacement and the replacement is validated.

Examples:

- ./bin/ask
- scripts/
- docs-policy.json
- GOVERNANCE
- README/AGENTS documented commands

Removal proof:

- caller inventory has no remaining public operator references to the alias;
- replacement command appears in AGENTS.md or the relevant docs;
- repo validation passes after removing the alias from repo-layout.v1.json.

### Internal SDK Entrypoints

Prefer updating callers directly once the new path exists. Use wrappers only
when the entrypoint is imported or executed from many places and direct
migration would be unsafe in one slice.

Examples:

- Infrastructure/scripts/**
- Infrastructure/scripts/lib/ask/**
- Infrastructure/config/schemas/**
- Infrastructure/config/skills-sdk/**

Removal proof:

- tests and wrapper commands resolve the new path;
- ask CLI routes continue to work from repository root;
- generated artifacts record the new source path or a compatibility source.

### Foundry Source Entrypoints

Keep old source roots as compatibility aliases until runtime projection,
skillset manifests, package verification, and Skill Factory routes all consume
the new source root.

Examples:

- Skills/
- Plugins/
- skills-system/

Removal proof:

- skillset generation points at foundry/ paths;
- .agents runtime projections point at the new canonical source or an explicit
  compatibility alias;
- package verify passes for representative first-party, plugin-owned, and
  system-skill packages.

### Runtime And Generated Surfaces

Do not hand-maintain wrappers for generated runtime or evidence paths. Regenerate
them from canonical sources after a source move.

Examples:

- .agents/
- .skillsets/
- .harness/evidence/**
- Infrastructure/artifacts/**
- artifacts/**

Removal proof:

- generator command succeeds;
- generated output no longer references retired roots except in historical
  evidence.

## Current Deprecated Aliases

The layout validator currently allows these deprecated compatibility aliases:

- GOVERNANCE
- docs-policy.json
- scripts

These aliases should ratchet down, not grow. Adding another top-level root or
alias requires an ADR or an update to repo-layout.v1.json with tests.

## Blocking Rule

Unknown top-level roots and unknown symlinks must block migration. The current
Prototypes/ root is intentionally classified as evidence_control for bounded
prototype workbenches only; that classification must not become a general place
for product source, runtime projection, or unmanaged experiments.
