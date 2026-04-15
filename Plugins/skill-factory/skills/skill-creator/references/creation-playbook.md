# Skill Creation Playbook

## Table of Contents

- [Step 1: Clarify Scope with Examples](#step-1-clarify-scope-with-examples)
- [Step 2: Plan Reusable Resources](#step-2-plan-reusable-resources)
- [Step 3: Initialize the Skill](#step-3-initialize-the-skill)
- [Step 4: Implement and Refine](#step-4-implement-and-refine)
- [Step 5: Validate](#step-5-validate)
- [Step 6: Iterate and Forward-Test](#step-6-iterate-and-forward-test)

## Step 1: Clarify Scope with Examples

Establish concrete user-style examples before implementation. Confirm:

- What functionality the skill must support.
- Phrases that should trigger the skill.
- Preferred installation path.

Prompting guidance:

- Ask only the minimum high-leverage questions first.
- Expand only when ambiguity would cause incorrect structure or scope.

## Step 2: Plan Reusable Resources

Translate examples into reusable package components:

- `Infrastructure/scripts/` for deterministic and repeated logic.
- `Infrastructure/references/` for domain rules, specs, and deep procedures.
- `assets/` for templates or files used in output artifacts.

Planning heuristic:

- If logic would be rewritten repeatedly, promote to script.
- If context is large but read-only, place in references.
- If file is consumed in output and not as context, place in assets.

## Step 3: Initialize the Skill

Use initialization for new skills:

```bash
python3 Infrastructure/scripts/init_skill.py <skill-name> --path <output-directory> [--resources scripts,references,assets] [--examples]
```

Run this from the repository root where `Infrastructure/scripts/init_skill.py` exists. If you are outside that root, call it with `python3 /absolute/path/to/init_skill.py ...`.

Scaffold source of truth:
- `SKILL.md` is rendered from `Infrastructure/templates/scaffold-simple-skill.md.tmpl` in this skill package.

Defaults and naming:

- Use the canonical repository category path (for example `github/<skill-name>`) when no path is provided.
- Use lowercase, digits, and hyphens only.
- Keep names short, action-oriented, and trigger-friendly.

## Step 4: Implement and Refine

Implementation order:

1. Add reusable resources first.
2. Write concise `SKILL.md` guidance that links to those resources.
3. Remove placeholder files not needed by final scope.

When updating metadata:

- Generate or refresh `agents/openai.yaml` with interface overrides.
- Keep optional fields only when explicitly provided.

## Step 5: Validate

Run baseline and strict checks:

```bash
python3 Infrastructure/scripts/quick_validate.py <path/to/skill-folder>
./bin/ask skills audit <path/to/skill-folder> --level strict --robot
```

Validation discipline:

- Treat failures as blockers.
- Re-run checks after each fix.
- Keep audit output in handoff notes for traceability.

## Step 6: Iterate and Forward-Test

Use forward-testing when behavior is complex or risk is high.

Execution guidance:

- Use independent threads for each pass.
- Provide realistic task artifacts, not precomputed conclusions.
- Evaluate whether the skill generalizes to unseen-but-related prompts.

Approval guidance:

Request user approval before forward-testing if likely to:

- consume significant time,
- require extra credentials or approvals, or
- touch live production systems.
