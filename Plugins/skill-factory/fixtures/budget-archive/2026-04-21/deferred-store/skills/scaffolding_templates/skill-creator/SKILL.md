---
name: skill-creator
description: Guide for creating effective skills. Use this skill when users need to create a new skill or reshape a draft skill package before hardening, benchmarking, or distribution.
metadata:
  short-description: Create or update a skill
  skill-type: scaffolding_templates
---

# Skill Creator

Create and evolve Codex skills that are reusable, auditable, and easy for another agent to execute.

## Table of Contents

- [When to Use](#when-to-use)
- [Philosophy](#philosophy)
- [Inputs](#inputs)
- [Agent Injection](#agent-injection)
- [Outputs](#outputs)
- [Procedure](#procedure)
- [Validation](#validation)
- [Antipatterns](#antipatterns)
- [Constraints](#constraints)
- [Examples](#examples)
- [References](#references)

## When to use

Use this skill when work involves:

- Creating a new skill from user intent or a repo requirement.
- Refactoring an existing skill without losing behavior.
- Standardizing a skill package across `SKILL.md`, `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`.
- Adding robust validation and forward-testing coverage for a complex skill.

Do not use this skill when the main request is:

- Release-hardening, benchmark comparisons, or contract readiness for an already-formed skill package; route to [[skill-builder]].
- Install/import/distribution tasks for already-valid skills; route to [[skill-installer]].
- Routine implementation work that does not change skill packaging or governance.

## Philosophy

Treat skill authoring as durable systems design:

- Keep routing and execution intent explicit.
- Never drop required context for brevity; move it into `references/` with explicit progressive-disclosure signposts.
- Do not remove important context for budget trimming; move it to `references/` and add explicit `Read when` signposts in `SKILL.md`.
- Prefer reusable artifacts over repeated one-off prose.
- Optimize for maintainability by another agent with no prior context.

## Required inputs

Collect these inputs before editing:

- The target outcome and trigger phrases the skill must cover.
- Concrete example prompts users are likely to issue.
- Target location for the skill folder. If unspecified, default to canonical repo category path `github/<skill-name>` under the git source tree.
- Required bundled resources (scripts, references, assets).
- Any explicit UI metadata provided by the user (`display_name`, icons, brand color, default prompt).

Assumptions and requirements:

- The skill name uses lowercase letters, digits, and hyphens.
- `SKILL.md` frontmatter includes valid `name` and `description`.
- The skill body is navigation-first and delegates deep detail to `references/`.

## Agent Injection

When the new skill needs a dedicated subagent path, handle role wiring during scaffold creation:

1. Check for reusable role TOMLs in `./configs/codex/agents/` when present, then fall back to project/global `.codex/agents/`.
2. If no reusable role exists, invoke [[codex-agent-creator]] to create a purpose-built agent file.
3. Validate the selected/generated role file:

```bash
bash Skills/codex-agent-creator/scripts/validate_role.sh --agent-name <name> --agent-file <path>
```

Note: the canonical skill route is `[[codex-agent-creator]]`; the helper scripts still live under the legacy directory name `Skills/codex-agent-creator/`.

4. If the user asks to install the role, run:

```bash
bash Skills/codex-agent-creator/scripts/install_role.sh --agent-name <name> --agent-file <path> --scope project|global [--update-existing]
```

5. Include the agent route in handoff notes as `agent_injection_mode: reuse-existing|create-purpose-built`.

## Deliverables

Produce these deliverables:

- A validated skill directory with:
  - `SKILL.md` as the concise operational entrypoint.
  - `references/` documents for detailed guidance and examples.
  - `scripts/` and `assets/` only when they provide real reuse value.
  - `agents/openai.yaml` aligned with the current skill intent.
- Validation evidence showing commands run and outcomes.
- A short handoff summary listing changed files, decisions, and remaining risks.

## Output contract

For non-trivial responses, include:

- `schema_version`
- `mode`
- `skill_path`
- `changed_files`
- `context_routes` as `[{from, to, read_when}]` whenever required detail moved from `SKILL.md` to `references/`
- `validation_evidence` as `[{command, outcome, note}]` with `outcome` in `pass|fail|blocked`
- `risks`

## Procedure

Follow this workflow in order unless the user asks for a scoped shortcut.

1. Clarify scope with concrete examples.
2. Plan reusable resource boundaries (`scripts/`, `references/`, `assets/`).
3. Initialize when creating from scratch:

```bash
python3 scripts/init_skill.py <skill-name> --path <output-directory> [--resources scripts,references,assets] [--examples]
```

`scripts/init_skill.py` renders `SKILL.md` from `templates/scaffold-simple-skill.md.tmpl`.

4. Implement reusable resources first, then update `SKILL.md` so it points to those resources.
   - If slimming `SKILL.md`, move required detail to `references/` before deleting prose and add a `Read when: <condition>` signpost from `SKILL.md`.
5. Generate or refresh `agents/openai.yaml` when needed:

```bash
python3 scripts/generate_openai_yaml.py <path/to/skill-folder> --interface key=value
```

6. Forward-test complex changes with independent runs that use realistic artifacts and task prompts.

Detailed procedures, examples, and rationale live in:

- [references/foundations.md](./references/foundations.md)
- [references/creation-playbook.md](./references/creation-playbook.md)
- [references/openai_yaml.md](./references/openai_yaml.md)

## Validation

Run validation after each meaningful change and before handoff:

```bash
python3 scripts/quick_validate.py <path/to/skill-folder>
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
- Replacing required caveats with a shorter summary instead of relocating full context into `references/`.
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

Read when:

- You need concrete request phrasing examples: [references/examples-and-gotchas.md](./references/examples-and-gotchas.md).
- You need quick troubleshooting cues for routing failures: [references/examples-and-gotchas.md](./references/examples-and-gotchas.md).

## References

Read these files based on the task:

- [references/foundations.md](./references/foundations.md): Read when defining scope, boundaries, and progressive-disclosure posture.
- [references/creation-playbook.md](./references/creation-playbook.md): Read when scaffolding or iterating on a skill package end to end.
- [references/openai_yaml.md](./references/openai_yaml.md): Read when editing `agents/openai.yaml` interface, policy, or dependencies.
- [references/contract.yaml](./references/contract.yaml): Read when validating trigger, input, output, and risk contract completeness.
- [references/evals.yaml](./references/evals.yaml): Read when adding or revising trigger and non-trigger evaluation coverage.
- [references/handoff-package-template.md](./references/handoff-package-template.md): Read when producing reviewer-ready handoff summaries.
- [references/examples-and-gotchas.md](./references/examples-and-gotchas.md): Read when you need concrete request examples or fast troubleshooting cues.

## See Also

| Skill | When to use together |
|---|---|
| [[codex-agent-creator]] | Create or update custom agents when skill workflows need dedicated role files |
| [[skillify]] | Convert hand-authored or rough skills into canonical, graph-aware skill packages |

**Topic map:** [[agent-ops]]

## Failure mode
- Stop at the first blocker, report root cause, and provide the safest next command.

## Gotchas
- Read when debugging ambiguous-scope failures: [references/examples-and-gotchas.md](./references/examples-and-gotchas.md).
