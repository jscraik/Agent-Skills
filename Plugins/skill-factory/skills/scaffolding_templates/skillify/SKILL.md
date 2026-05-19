---
name: skillify
description: "Converts a successful repeatable workflow into a validated Codex SKILL.md package with triggers, examples, evals, and release checks. Use when users say create a skill, skillify this, package a workflow, save this process, make reusable guidance, or turn a session into a skill."
metadata:
  version: "1.0.0"
  skill-type: scaffolding_templates
---

# Skillify

Turn a proven workflow into a reusable skill package. Preserve repeatable behavior, not transcript noise.

## Philosophy

Start with 2-3 focused surfaces and capture the smallest validated workflow.

## When To Use

- The user asks to skillify, create a skill, save a workflow, package a process, or make reusable guidance.
- A completed session has repeatable triggers, known inputs, expected outputs, and a validation route.
- The output should be a canonical skill package, not a one-off answer, doc note, or hook.

## Required Inputs

- Source evidence, destination path, owner, success criteria, side-effect class, one realistic trigger, and one validation command.

Ask one direct question if destination, owner, or repeatability is unclear.

## Outputs

- A canonical skill package path.
- A compact `SKILL.md` plus package-local contract, evals, and task profile when durable evidence is needed.

## Workflow

1. Resolve the canonical package path and applicable `AGENTS.md`.
2. Decide: skill, docs, script, hook, validator, rule, or answer.
3. Extract triggers, anti-triggers, inputs, outputs, tools, safety boundaries, and failure handling.
4. Validate the extraction against the source evidence before writing files.
5. Create the minimal package shape below.
6. Add one happy-path eval and one boundary or negative eval.
7. Run strict audit. If it fails, fix that failure before broader validation.
8. Run external review and record the report path when hardening evidence matters.

## Extraction Checklist

Capture trigger phrases, anti-triggers, required inputs, final output shape, side effects, approvals, required tools, and the smallest local proof command. Stop before writing when source evidence cannot fill triggers, inputs, outputs, and validation.

## Minimal Package

Create this minimal package: `<skill-name>/SKILL.md`, `references/contract.yaml`, `references/evals.yaml`, and `references/task-profile.json`.

Add `scripts/`, `assets/`, or extra references only when needed.

Minimal `SKILL.md` body: frontmatter with `name`, trigger-rich `description`, and `metadata.version`; then `When To Use`, `Inputs`, `Workflow`, `Output Template`, `Execution Boundaries`, `Anti-Patterns`, and `Validation` sections. The validation section must say to run `./bin/ask skills audit <skill-path> --level strict --json --robot` and fail fast at the first failed gate.

## Output Template

Return:

```yaml
schema_version: 1
mode: create_skill
skill_path: <canonical package path>
source_evidence: [<bounded report or workflow note>]
first_principles_gate:
  decision: BUILD_SKILL|USE_DOCS|USE_SCRIPT|USE_RULE|ANSWER_DIRECTLY
  reason: <why this is the smallest durable artifact>
files_changed: [<path>]
validation:
  - command: <exact command>
    outcome: pass|fail|blocked
blocked_by: null
```

## Examples

When the user asks, "Can you convert our repeated GitHub release triage workflow into a validated skill?", build this shape:

Expected output: create `SKILL.md` with frontmatter name `release-triage`, a description that names release-failure trigger phrases, and four steps: check current release status, identify the first broken stage, compare rollback/hotfix/pause options, and report validation evidence.

Also add `references/contract.yaml` with owner `release-engineering`, side effect class `repo-write`, required release/repository inputs, expected blocker and recommendation outputs, and validation command `./bin/ask repo closeout --changed --json --robot`.

Add `references/evals.yaml` with one CI failure scenario and one missing-evidence scenario that requires asking for the release identifier rather than inventing state.

Example return: `skill_path: Plugins/release/skills/release-triage`, `first_principles_gate.decision: BUILD_SKILL`, `files_changed: [SKILL.md, references/contract.yaml, references/evals.yaml]`, and validation command `./bin/ask skills audit Plugins/release/skills/release-triage --level strict --json --robot` with outcome `pass`.

## Constraints

- Keep the first package narrow enough to explain, validate, and maintain.
- Move long contracts, evals, transcripts, schemas, and examples to references.
- Keep evidence portable; avoid machine-local absolute paths and private transcript dumps.
- Redact secrets, credentials, API keys, tokens, PII, and sensitive data by default.

## Execution Boundaries

- Do not codify exploratory, contradictory, one-off, or secret-bearing workflows.
- Do not edit generated `.agents/**`, runtime projections, caches, or archived fixtures as source.
- Prompt before broad rewrites, external writes, installs, generated media persistence, or destructive cleanup.
- Move long transcripts, examples, schemas, and templates to `references/`.

## Failure Mode

If repeatability, ownership, or validation cannot be proven, stop and return a blocker instead of creating a ceremonial skill.

## Gotchas

- A good transcript is not automatically a good skill; extract repeatable decisions.
- Tessl may reward concrete examples, while local gates also require repo-specific safety headings.
- Runtime projection files can look current while canonical sources have drifted.

## Anti-Patterns

- Packaging broad brainstorms, contradictory guidance, or private logs as durable instructions.
- Creating a skill when a script, validator, rule, or short answer is the clearer artifact.
- Claiming readiness after skipped validation.

## Handoff

- Existing skill hardening -> `skill-builder`.
- Skill health or keep/merge/retire analysis -> `skill-refactor`.
- Install, list, sync, or runtime visibility proof -> `skill-installer`.
- Plugin package lifecycle work -> `plugin-factory`.

## References

- Local contract, evals, and task profile: `references/`
- Context development lifecycle: `Plugins/skill-factory/references/context-development-lifecycle.md`
- First-principles factory gate: `Infrastructure/references/first-principles-factory-gate.md`
- Cookbook-derived skill improvement, documentation interface, and eval flywheel lenses: `Infrastructure/references/openai-cookbook-expert-lens-pack.md`, `Infrastructure/references/openai-cookbook-skill-expertise-map.md`
- Software-literature skill scaffolding lenses: `Infrastructure/references/software-literature-expert-lens-pack.md`, `Infrastructure/references/software-literature-skill-expertise-map.md`

## Validation

Run `./bin/ask skills audit <skill-path> --level strict --json --robot`, then `python3 Infrastructure/bin/ask skills external-review <skill-path> --audit-level compat --json`.

Fail fast: stop at the first failed gate, classify it, and do not proceed to sync, commit, publish, or install until fixed or explicitly blocked.
