---
name: skill-creator
description: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Codex's capabilities with specialized knowledge, workflows, or tool integrations.
metadata:
  short-description: Create or update a skill
---

# Skill Creator

Create and evolve Codex skills that are reusable, auditable, and easy for another agent to execute.

## Table of Contents

- [When to Use](#when-to-use)
- [Philosophy](#philosophy)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Procedure](#procedure)
- [Validation](#validation)
- [Antipatterns](#antipatterns)
- [Constraints](#constraints)
- [Examples](#examples)
- [References](#references)

## When to Use

Use this skill when work involves:

- Creating a new skill from user intent or a repo requirement.
- Refactoring an existing skill without losing behavior.
- Standardizing a skill package across `SKILL.md`, `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`.
- Adding robust validation and forward-testing coverage for a complex skill.

Do not use this skill for routine implementation work that does not change skill packaging or governance.

## Philosophy

Treat skill authoring as durable systems design:

- Keep routing and execution intent explicit.
- Preserve important context by relocating depth into `references/`, not by deleting meaning.
- Prefer reusable artifacts over repeated one-off prose.
- Optimize for maintainability by another agent with no prior context.

## Inputs

Collect these inputs before editing:

- The target outcome and trigger phrases the skill must cover.
- Concrete example prompts users are likely to issue.
- Target location for the skill folder. If unspecified, default to `${CODEX_HOME:-$HOME/.codex}/skills`.
- Required bundled resources (scripts, references, assets).
- Any explicit UI metadata provided by the user (`display_name`, icons, brand color, default prompt).

Assumptions and requirements:

- The skill name uses lowercase letters, digits, and hyphens.
- `SKILL.md` frontmatter includes valid `name` and `description`.
- The skill body is navigation-first and delegates deep detail to `references/`.

## Outputs

Produce these deliverables:

- A validated skill directory with:
  - `SKILL.md` as the concise operational entrypoint.
  - `references/` documents for detailed guidance and examples.
  - `scripts/` and `assets/` only when they provide real reuse value.
  - `agents/openai.yaml` aligned with the current skill intent.
- Validation evidence showing commands run and outcomes.
- A short handoff summary listing changed files, decisions, and remaining risks.

## Procedure

Follow this workflow in order unless the user asks for a scoped shortcut.

1. Clarify scope with concrete examples.
2. Plan reusable resource boundaries (`scripts/`, `references/`, `assets/`).
3. Initialize when creating from scratch:

```bash
scripts/init_skill.py <skill-name> --path <output-directory> [--resources scripts,references,assets] [--examples]
```

4. Implement reusable resources first, then update `SKILL.md` so it points to those resources.
5. Generate or refresh `agents/openai.yaml` when needed:

```bash
plugins/skill-factory/skills/skill-creator/scripts/generate_openai_yaml.py <path/to/skill-folder> --interface key=value
```

6. Forward-test complex changes with independent runs that use realistic artifacts and task prompts.

Detailed procedures, examples, and rationale live in:

- [references/foundations.md](./references/foundations.md)
- [references/creation-playbook.md](./references/creation-playbook.md)
- [references/openai_yaml.md](./references/openai_yaml.md)

## Validation

Run validation after each meaningful change and before handoff:

```bash
scripts/quick_validate.py <path/to/skill-folder>
./bin/ask skills audit <path/to/skill-folder> --level strict --robot
```

Fail-fast policy:

- Stop at the first failed gate and do not proceed until it is fixed.
- Re-run validation after each fix.
- Treat strict gate failures as blockers for handoff.

For complex revisions, run forward-testing and verify the skill can solve realistic tasks without privileged context leakage.

## Anti-Patterns

Avoid these pitfalls:

- Packing long tutorials into `SKILL.md` instead of moving detail into `references/`.
- Duplicating the same guidance in both `SKILL.md` and reference files.
- Shipping placeholder example files from initialization when they are not used.
- Adding docs unrelated to runtime execution of the skill.
- Writing frontmatter descriptions that are vague about trigger contexts.

## Constraints

Safety and quality constraints:

- Redact secrets, credentials, tokens, private keys, and sensitive personal data by default in outputs, logs, examples, and artifacts.
- Prefer offline-first workflows; require explicit user intent before network-dependent operations.
- Keep operations non-destructive unless destructive behavior is explicitly required and confirmed.
- Keep `SKILL.md` concise and delegate deep context to `references/` and scripts.
- Keep instructions actionable, imperative, and testable.

## Examples

Example requests this skill should handle:

- "Create a `gh-release-notes` skill in `${CODEX_HOME:-$HOME/.codex}/skills`, include `references/contract.yaml` and `references/evals.yaml`, then run strict audit."
- "Refactor this oversized `SKILL.md` by moving deep implementation details into `references/` while keeping behavior and triggers unchanged."
- "After I updated trigger phrasing in frontmatter, regenerate `agents/openai.yaml` and confirm metadata parity."

## References

Read these files based on the task:

- [references/foundations.md](./references/foundations.md): Core principles, anatomy, and progressive-disclosure patterns.
- [references/creation-playbook.md](./references/creation-playbook.md): Detailed step-by-step creation and iteration workflow.
- [references/openai_yaml.md](./references/openai_yaml.md): `agents/openai.yaml` field definitions and constraints.
- [references/contract.yaml](./references/contract.yaml): Machine-checkable purpose, triggers, inputs, outputs, risks.
- [references/evals.yaml](./references/evals.yaml): Evaluation cases and deterministic safety guards.
- [references/handoff-package-template.md](./references/handoff-package-template.md): Handoff structure for reviewer-ready summaries.

## See Also

| Skill | When to use together |
|---|---|
| [[skill-builder]] | Harden and benchmark completed skill drafts before release |
| [[skill-installer]] | Install already-validated skills into Codex environments |
| [[plugin-creator]] | Package finished skills into a plugin distribution scaffold |

**Topic map:** [[agent-ops]]
