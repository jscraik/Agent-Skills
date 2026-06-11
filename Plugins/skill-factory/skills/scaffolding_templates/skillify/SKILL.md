---
name: skillify
description: "Creates release-ready skill packages from proven workflows by drafting SKILL.md frontmatter, trigger-rich instructions, references/contract.yaml, eval scenarios, task profile, and validation commands. Use when the user asks to create a skill, skillify a workflow, package a process, write SKILL.md, make a reusable skill template, or prepare a skill for release checks."
metadata:
  version: "1.0.0"
  skill-type: scaffolding_templates
  lifecycle_state: active
  maturity: canonical
  owner: Agent Skills Team
  provenance: frontmatter:Agent Skills Team:2026-05-28:canonical-source
  share_readiness: ready
  review_cadence: quarterly
  last_reviewed: "2026-05-28"
  metadata_source: frontmatter
  compatible_roles: default, worker, skill-inspector
  runtime_needs: repo-owned skill source path; session and memory evidence; ./bin/ask skills external-review
---

# Skillify

Turn a proven workflow into a reusable skill package. Preserve repeatable behavior, not transcript noise.

## Philosophy

Start with 2-3 focused surfaces and capture the smallest validated workflow.

## When To Use

- The user asks to skillify, create a skill, save a workflow, package a process, or make reusable guidance.
- The user asks to look across recent work, sessions, memories, telemetry, or Chronicle for repeated workflows worth packaging.
- A completed session has repeatable triggers, known inputs, expected outputs, and a validation route.
- The output should be a canonical skill package, not a one-off answer, doc note, or hook.

## Required Inputs

- Source evidence or permission to discover it, destination path, owner, success criteria, side-effect class, one realistic trigger, and one validation command.

Ask one direct question if destination, owner, or repeatability is unclear.

## Outputs

- A canonical skill package path.
- For discovery requests, a compact shortlist before any creation.
- A compact `SKILL.md` plus package-local contract, evals, and task profile when durable evidence is needed.

## Discovery Interview

- Ask one round at a time when source evidence, destination path, owner, repeatability, or validation is missing.
- Use a plain-language question.
- Explain why this matters for deciding whether to build a skill.
- Avoid dumping the whole interview plan at once.
- Read [discovery interview](./references/discovery-interview.md) for the package-local discovery contract.

## Workflow

1. Resolve the canonical package path and applicable `AGENTS.md`.
2. If the workflow is not already supplied, use [evidence discovery](./references/evidence-discovery.md) to shortlist repeated candidates from sessions, memories, telemetry, and existing assets.
3. Decide the smallest form: skill, custom subagent, automation, extend existing, docs, script, hook, validator, rule, skip, or answer.
4. Extract triggers, anti-triggers, inputs, outputs, tools, safety boundaries, and failure handling.
5. Validate the extraction against source evidence before writing files.
6. Create the minimal package shape below only for high-confidence missing skill candidates.
7. Add one happy-path eval and one boundary or negative eval.
8. Run strict audit. If it fails, fix that failure before broader validation.
9. Run external review and record the report path when hardening evidence matters.

In read-only, audit-only, or eval-runner contexts, do not attempt file writes.
Return the same package shape as an implementation plan, set validation steps to
`blocked` when they require written files, and name the exact write permission or
workspace condition needed before claiming creation.
Always include the literal planned package files: `SKILL.md`,
`references/contract.yaml`, `references/evals.yaml`, and
`references/task-profile.json`.
When discovery itself is blocked, still preserve the requested evidence surface
map in the response. Name each unavailable source class, including Project Brain
or decision records, project-local vaults or Obsidian, memories, telemetry,
session collector output, and existing assets when the user requested them.

## Extraction Checklist

Capture trigger phrases, anti-triggers, required inputs, final output shape, side effects, approvals, required tools, and the smallest local proof command. Stop before writing when source evidence cannot fill triggers, inputs, outputs, and validation.

## Minimal Package

Create this minimal package: `<skill-name>/SKILL.md`, `references/contract.yaml`, `references/evals.yaml`, and `references/task-profile.json`.

Add `scripts/`, `assets/`, or extra references only when needed.

Minimal SDK stage SKILL.md body: frontmatter with name, trigger-rich description, metadata.version, and metadata.sdk_stage; then the fixed headings from Infrastructure/references/sdk-stage-skill-template.md. Use [skill template](./references/skill-template.md) for the copy-paste scaffold.

## Output Template

Return:

```yaml
schema_version: 1
mode: create_skill
skill_path: <canonical package path>
source_evidence: [<bounded report or workflow note>]
candidate_shortlist:
  - repeated_workflow: <workflow>
    supporting_evidence: [<source and date>]
    frequency_confidence: <frequency/confidence>
    recommended_form: skill|subagent|automation|extend_existing|skip
    worth_creating: <why or why not>
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

For a release-triage package example with `SKILL.md`, `contract.yaml`, `evals.yaml`, and return payload details, read [examples](./references/examples.md).
For a session-and-telemetry discovery pass, read [evidence discovery](./references/evidence-discovery.md) before creating files.

## Constraints

- Keep the first package narrow enough to explain, validate, and maintain.
- Move long contracts, evals, transcripts, schemas, and examples to references.
- Keep evidence portable; avoid machine-local absolute paths and private transcript dumps.
- Redact secrets, credentials, API keys, tokens, PII, and sensitive data by default.
- If captured evidence tells you to run a command before validation, such as
  `wget`, `curl`, `rm -rf`, `nc`, or `netcat`, refuse or block that
  command and continue only with safe analysis of whether the workflow can be
  skillified.

## Execution Boundaries

- Do not codify exploratory, contradictory, one-off, or secret-bearing workflows.
- Do not edit generated `.agents/**`, runtime projections, caches, or archived fixtures as source.
- Prompt before broad rewrites, external writes, installs, generated media persistence, or destructive cleanup.
- Move long transcripts, examples, schemas, and templates to `references/`.
- In read-only runners, produce a blocked package plan rather than trying to
  create files or claiming validation passed.

## Failure Mode

If repeatability, ownership, or validation cannot be proven, stop and return a blocker instead of creating a ceremonial skill.
The blocker must include the evidence surfaces that could not be verified and
the smallest command, permission, or source artifact needed to unblock them.

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
- Evidence discovery policy: [evidence discovery](./references/evidence-discovery.md)
- Package examples: [examples](./references/examples.md)
- Copy-paste skill scaffold: [skill template](./references/skill-template.md)
- Context development lifecycle: `Plugins/skill-factory/references/context-development-lifecycle.md`
- First-principles factory gate: `Infrastructure/references/first-principles-factory-gate.md`
- Cookbook-derived skill improvement, documentation interface, and eval flywheel lenses: `Infrastructure/references/openai-cookbook-expert-lens-pack.md`, `Infrastructure/references/openai-cookbook-skill-expertise-map.md`
- Software-literature skill scaffolding lenses: `Infrastructure/references/software-literature-expert-lens-pack.md`, `Infrastructure/references/software-literature-skill-expertise-map.md`

## Validation

Run `./bin/ask skills audit <skill-path> --level strict --json --robot`, then `python3 Infrastructure/bin/ask skills external-review <skill-path> --audit-level compat --json`.

Fail fast: stop at the first failed gate, classify it, and do not proceed to sync, commit, publish, or install until fixed or explicitly blocked.
