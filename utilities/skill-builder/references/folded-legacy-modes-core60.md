# Folded Legacy Modes (Core60)

Destination skill: `utilities/skill-builder`

This file captures legacy capabilities migrated from retired skills.

## `install-distribute`
- Source skill: `utilities/skill-installer`
- Legacy description: Plan and install skills into a Codex skills directory from curated or repo sources; use when a user asks to list available skills, install/update a skill, or validate a source before installation. Do not use for general app development, unrelated debugging, or docs-only rewrites.
- Fold rationale: Install/update/distribute are downstream lifecycle steps of skill building.
- Legacy section map:
  - Table of Contents
  - Compliance
  - Philosophy
  - Guiding questions
  - Scope and triggers
  - Required inputs

## `prompt-packaging`
- Source skill: `utilities/codex-prompt-creator`
- Legacy description: Create or update reusable Codex skills under .agents/skills and optionally local ~/.codex/prompts shortcuts. Use when a user asks to build, revise, or package prompts and skills for repeatable workflows.
- Fold rationale: Prompt-as-skill packaging is a subset of skill lifecycle management.
- Legacy section map:
  - Table of Contents
  - Scope and triggers
  - Required inputs
  - Deliverables
  - Philosophy
  - Gold prompt standard (Mar 2026 baseline)
