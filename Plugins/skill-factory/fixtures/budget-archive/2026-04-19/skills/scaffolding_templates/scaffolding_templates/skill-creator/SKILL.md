---
name: skill-creator
description: Guide for creating effective skills. Use this skill when users need to create a new skill or reshape a draft skill package before hardening, benchmarking, or distribution.
metadata:
  short-description: Create or update a skill
  skill-type: scaffolding_templates
---

# Skill Creator

Use this skill to create or restructure a skill package so it is ready for hardening.

## When to use
- New skill creation from user intent.
- Major reshape of an existing draft skill.
- Packaging alignment across `SKILL.md`, `references/`, `scripts/`, and `agents/openai.yaml`.

## Do not use
- Release-hardening/evals: route to `[[skill-builder]]`.
- Install/import flows: route to `[[skill-installer]]`.

## Core Philosophy
- Start with a narrow, executable scope.
- Keep routing intent explicit in `SKILL.md`.
- Preserve required context by relocating detail to `references/`.

## Core workflow
1. Confirm goal, trigger phrases, and category.
2. Define smallest viable package boundary.
3. Create/update required files with canonical names.
4. Move deep details to references and keep `SKILL.md` route-focused.
5. Run baseline validation commands and report outcomes.

## Required output contract
Provide:
- `schema_version`
- `mode`
- `skill_path`
- `changed_files`
- `context_routes`
- `validation_evidence`
- `risks`

## Progressive disclosure policy
Never drop required context; relocate depth into `references/` with explicit signposts.

Read when:
- drafting structure and routing text: [foundations](./references/foundations.md)
- creating reusable handoff payloads: [handoff package template](./references/handoff-package-template.md)
- shaping examples and edge handling: [examples and gotchas](./references/examples-and-gotchas.md)

## Anti-Patterns to Avoid
- Building broad package scaffolds without a clear trigger surface.
- Duplicating long policy text in `SKILL.md` instead of references.
- Returning unvalidated scaffolds as production-ready outputs.

## Constraints
- Preserve user constraints exactly.
- Use deterministic, reproducible edits.
- Redact sensitive values in outputs.
