---
name: skill-creator
description: Guide for creating effective skills. Use this skill when users need to create a new skill or reshape a draft skill package before hardening, benchmarking, or distribution.
metadata:
  skill-type: scaffolding_templates
---

# Skill Creator

Create and evolve Codex skills that are reusable, auditable, and easy for another agent to execute.

## Table of Contents

- [When to Use](#when-to-use)
- [Philosophy](#philosophy)
- [Inputs](#inputs)
- [Agent Injection](#agent-injection)
- [Execution Boundaries](#execution-boundaries)
- [Outputs](#outputs)
- [Procedure](#procedure)
- [Validation](#validation)
- [Governance Spine](#governance-spine)
- [Encouraging Variation](#encouraging-variation)
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
- Apply the context-disposition policy: move important still-valid context to references, and intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.
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
- Every skill must satisfy the enforced agent-native contract: execution boundaries, expected artifacts, repair/failure behavior, and validation or acceptance criteria.
  Read when: applying that contract to generated artifacts, CLIs, subagents, credentials, or multi-phase repair: [agent-native skill contract](../../../../../Infrastructure/references/agent-native-skill-contract.md).
- For non-trivial operational skills, apply the agent-native operational pattern extraction checklist before drafting: requested vs implied work, tool resolution, stale-evidence handling, inspectable outputs, safety class, retry, and closeout.
  Read when: adapting reusable patterns from compact operational skills without copying local assumptions or prose style: [external skill pattern extraction](../../../../../Infrastructure/references/external-skill-patterns.md).
- Every non-trivial skill must satisfy the OpenAI-style design contract: one primary user intent, explicit side-effect class, minimized context surface, stable output contract, and confirmation behavior for consequential writes.
  Read when: shaping triggers, side effects, structured output, or headless assumptions: [OpenAI-style plugin design contract](../../../../../Infrastructure/references/openai-style-plugin-design-contract.md).
- Read when: choosing whether the requested factory work should build a new artifact, improve an existing one, stay docs-only, or stop: [First-principles factory gate](../../../../../Infrastructure/references/first-principles-factory-gate.md).
- For non-trivial factory work, include `first_principles_gate` or an explicit `first_principles_gate_status: not_applicable` with the reason in the output or handoff before claiming readiness.

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

## Execution Boundaries

Create or reshape only canonical skill source packages, not generated runtime projections or command handles.

The entrypoint must keep execution ownership visible: who writes files, which artifacts are expected, when a subagent or external skill may be used, and which validation gate proves the package is ready for hardening.

Do not hide boundary decisions only in references. `SKILL.md` must expose enough boundary, artifact, repair, and validation guidance for another agent to run the workflow without guessing.

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
- `factory_governance` for non-trivial skills, including posture, traceability mode, eval coverage, and agent injection decision
- `session_evidence` when improving, refactoring, warning-cleaning, pruning, or deriving a skill from repeated session behavior
- `skill_improvement_loop` when improving or refactoring an existing skill
- `risks`

## Procedure

Follow this workflow in order unless the user asks for a scoped shortcut.

1. Clarify scope with concrete examples.
2. Plan reusable resource boundaries (`scripts/`, `references/`, `assets/`).
   - For non-trivial skills, classify the work with [references/factory-governance-spine.md](./references/factory-governance-spine.md) before editing.
   - Use bounded `~/.agents/session-collector` bundle evidence for skill improvement, warning cleanup, repeated workflow capture, pruning, or confidence-target work when available.
3. Initialize when creating from scratch:

```bash
python3 scripts/init_skill.py <skill-name> --path <output-directory> [--resources scripts,references,assets] [--examples]
```

`scripts/init_skill.py` renders `SKILL.md` from `templates/scaffold-simple-skill.md.tmpl`.

4. Implement reusable resources first, then update `SKILL.md` so it points to those resources.
   - If slimming `SKILL.md`, move required detail to `references/` before deleting prose and add a `Read when: <condition>` signpost from `SKILL.md`.
   - Keep the agent-native contract explicit in `SKILL.md`; do not hide ownership boundaries, artifact expectations, repair behavior, or acceptance criteria only in deep references.
   - For operational skills, preserve the first-command/tool-resolution path and the final proof path in the entrypoint; move bulky command examples and environment notes to references.
   - Keep the OpenAI-style design checkpoint explicit for non-trivial skills: primary intent, side-effect class, output shape, steering behavior, and validation evidence.
5. Generate or refresh `agents/openai.yaml` when needed:

```bash
python3 scripts/generate_openai_yaml.py <path/to/skill-folder> --interface key=value
```

6. Forward-test complex changes with independent runs that use realistic artifacts and task prompts.

Detailed procedures, examples, and rationale live in:

- [references/foundations.md](./references/foundations.md)
- [references/creation-playbook.md](./references/creation-playbook.md)
- [references/factory-governance-spine.md](./references/factory-governance-spine.md)
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

## Governance Spine

Use [references/factory-governance-spine.md](./references/factory-governance-spine.md) when the skill is reusable, delivery-related, delegated to agents, connected to `coding_harness`, or being improved from existing behavior.

Keep `tiny_helper` skills light. Require traceability, session evidence, A/B/C improvement loops, and Linear or Project Brain lifecycle fields only when the classification calls for them.

## Encouraging Variation

Adapt the scaffold to the user's actual context instead of converging on a favorite shape:

- Use a small wrapper skill for narrow workflows and a references-heavy package for complex operational skills.
- Vary examples, eval prompts, and output contracts to match the domain, risk, and expected operator.
- Preserve required governance surfaces, but do not add scripts, assets, or agents unless they reduce real repeat work.

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

Example requests:

- "Can you convert this repeated review workflow into a skill under `agent-ops`, with realistic trigger and non-trigger evals?"
- "Please inspect this draft `SKILL.md`; it is too long, and I need the deep implementation detail moved into references without losing behavior."
- "Help me build a skill package for installing private GitHub repo templates, but keep network and credential boundaries explicit."

Read when:

- You need concrete request phrasing examples: [references/examples-and-gotchas.md](./references/examples-and-gotchas.md).
- You need quick troubleshooting cues for routing failures: [references/examples-and-gotchas.md](./references/examples-and-gotchas.md).

## References

Read these files based on the task:

- [references/foundations.md](./references/foundations.md): Read when defining scope, boundaries, and progressive-disclosure posture.
- [references/creation-playbook.md](./references/creation-playbook.md): Read when scaffolding or iterating on a skill package end to end.
- [references/factory-governance-spine.md](./references/factory-governance-spine.md): Read when classifying traceability depth, session-evidence intake, or A/B/C improvement-loop requirements.
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

## Remember
- The agent is capable of extraordinary work when the skill is clear enough to execute without guessing. Keep the entrypoint clear, preserve the deep context, and vary the package to fit the work.
