---
name: skill-creator
description: Create or reshape Codex skill packages from user intent, repo requirements, or draft workflow notes. Use when a skill needs scaffolding, routing, resources, examples, and validation coverage before hardening.
metadata:
  skill-type: scaffolding_templates
---

# Skill Creator

Read when: full authoring doctrine, templates, or role-wiring details are needed: [creation playbook](./references/creation-playbook.md)

## Philosophy

- Keep routing, execution intent, and reusable artifacts explicit.
- Do not remove important context for budget trimming; move it to `references/` and add `Read when` signposts.
- Never drop required context for brevity; relocate it before shortening `SKILL.md`.

## When to use

Use for creating a new skill, refactoring a draft, standardizing `SKILL.md` plus resources, or adding validation before release hardening.

Route elsewhere:
- release-hardening or benchmarks: `skill-builder`;
- install/import/distribution: `skill-installer`;
- repeatable workflow capture from a completed run: `skillify`.

## Required inputs

- target outcome, trigger phrases, and likely prompts;
- destination path, category, and bundled resources;
- optional interface metadata such as icons, brand color, or default prompt.

## Deliverables

- concise `SKILL.md` entrypoint;
- detailed `references/` docs for context, examples, contracts, and evals;
- durable `scripts/`, `assets/`, or `agents/openai.yaml` only when useful;
- validation evidence and handoff notes.

## Procedure

1. Clarify scope with concrete examples.
2. Plan resource boundaries before writing.
3. Scaffold with `scripts/init_skill.py` when creating from scratch.
4. Implement reusable resources, then point `SKILL.md` at them.
5. Move required detail to `references/` before deleting prose.
6. Refresh `agents/openai.yaml` when interface metadata changes.
7. Forward-test complex changes with realistic artifacts and prompts.

Read when commands or templates are needed: [foundations](./references/foundations.md), [openai yaml](./references/openai_yaml.md), [handoff template](./references/handoff-package-template.md)

## Validation

Run after each meaningful change:
- `python3 scripts/quick_validate.py <path/to/skill-folder>`
- `./bin/ask skills audit <path/to/skill-folder> --level strict --robot`

Fail fast: stop at the first failed gate, fix it, rerun it, then continue.

## Constraints

- Redact secrets, credentials, tokens, private keys, and sensitive personal data.
- Prefer offline-first workflows; require explicit user intent for network work.
- Keep operations non-destructive unless explicitly required and confirmed.
- Keep `SKILL.md` concise and delegate deep context to `references/`.

## Anti-patterns

- Packing tutorials into `SKILL.md`.
- Duplicating guidance in entrypoint and references.
- Shortening by deleting caveats instead of relocating them.
- Shipping unused placeholder examples.
- Writing vague trigger descriptions.

## Output contract

For non-trivial work include `schema_version`, `mode`, `skill_path`, `changed_files`, `context_routes`, `validation_evidence`, and `risks`.

## Examples

Read when request phrasing or troubleshooting cues are needed: [examples and gotchas](./references/examples-and-gotchas.md)

## See Also

| Skill | When to use together |
|---|---|
| [[codex-agent-creator]] | Dedicated role files |
| [[skillify]] | Canonicalize rough workflows |

**Topic map:** [[agent-ops]]

## Failure mode

- Stop at the first blocker, report root cause, and provide the safest next command.

## Gotchas

- Ambiguous scope usually means the category, destination, or trigger examples are missing.
