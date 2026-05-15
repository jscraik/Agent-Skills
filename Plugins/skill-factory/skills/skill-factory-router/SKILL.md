---
name: skill-factory-router
description: "Use when the user asks to create, harden, refactor, skillify, install, or audit Codex skills/plugins; route to one Skill Factory lane and return the next executable step."
metadata:
  skill-type: team_automation
---

# Skill Factory Router

Route skill lifecycle requests to one primary lane before execution.

## Philosophy

Route first, then load depth. Keep this skill small enough to classify intent
quickly while preserving the boundaries that stop unsafe or noisy work.

## When To Use

- Use when the request is about creating, hardening, auditing, installing,
  refactoring, or skillifying Codex skills.
- Do not use for ordinary product implementation, generic repo maintenance, or
  plugin packaging that belongs to `plugin-factory`.

## Inputs

- User intent and target artifact, when available.
- Explicit skill names, plugin paths, or install sources.
- Any stated write authority, publication target, or validation requirement.

## Outputs

Return a compact handoff:

- `selected_lane`: `.system/skill-creator`, `skill-builder`, `skill-refactor`,
  `.system/skill-installer`, or `skillify`
- `mode`: `create`, `harden`, `analyze`, `install`, or `capture`
- `rationale`: one sentence
- `next_step`: first executable command, file read, or handoff action
- `blocked_by`: exact missing input only when lane choice or write authority is unsafe

Redact secrets and sensitive tokens from handoff text, paths, and examples.

## Decision Order

1. Explicit lane names win unless the user names multiple lanes.
2. New skill, draft package, or scaffold -> `.system/skill-creator` plus attached Skill Factory references.
3. Existing skill/plugin hardening, audit fixes, budget reduction, evals, or
   release readiness -> `skill-builder`.
4. Evidence-backed reliability analysis, merge/fold/retire decisions, recurring
   failures, or session-mining requests -> `skill-refactor`.
5. Completed workflow capture into a durable package -> `skillify`.
6. Install, list, import, sync, or runtime visibility proof for already-valid
   skills -> `.system/skill-installer` plus attached Skill Factory references.

## Procedure

1. Classify the user outcome and target artifact.
2. Choose exactly one primary lane.
3. If the request is a non-trivial new skill or major rewrite, make one short
   first-principles check: skill vs docs vs script vs hook vs validator vs answer.
4. Return the lane handoff. Load the selected lane only after this routing step.
5. For creation/install requests, load the Codex `.system` skill first, then
   read `skills-system/<skill>/references/skill-factory/` only when local
   contracts, evals, or hardening rules are needed.

## Scope Rule

Default to the narrowest current target. Widen only when the user asks for broad
portfolio analysis, cross-plugin cleanup, or repeated-failure mining.

Session evidence is optional unless the user mentions prior runs, session
collector, recurring failures, telemetry, or observed usage.

## Constraints

- Keep creation and installation on the Codex `.system` base skills.
- Add Skill Factory behavior through attached references, contracts, evals, and
  validators rather than forking upstream system `SKILL.md` bodies.
- Treat archive and deferred-store content as historical evidence, not live
  runtime context.
- Redact secrets, credentials, API keys, tokens, PII, and sensitive local paths
  from routing output unless the user explicitly needs a non-secret path.

## Execution Boundaries

- This router is read-only.
- Do not edit, install, sync, refresh projections, or mutate trackers here.
- Do not choose from keyword overlap alone when lane choice affects writes.
- If the user expected edits, route to the editing lane rather than returning a
  report-only answer.

## Gotchas

- `skill-creator` and `skill-installer` are upstream `.system` skills with
  local Skill Factory references attached.
- Session evidence is a route only when the user asks for prior-run mining,
  recurring-failure analysis, or evidence-backed reliability work.
- Handles may be aliases; inspect canonical paths before deciding ownership.

## Anti-Patterns

- Do not restore plugin-owned forks of `.system/skill-creator` or
  `.system/skill-installer`.
- Do not resolve live plugin files through `fixtures/budget-archive/**`.
- Do not load every reference before selecting a lane.
- Do not return a broad policy essay when a lane handoff is enough.

## Failure Mode

If lane choice is unsafe or ambiguous, return one blocking question or one
bounded assumption. Do not proceed to writes from the router.

## Validation

For Skill Factory routing changes, run:

- `python3 Infrastructure/scripts/validation-and-linting/check_plugin_active_archive_links.py --plugin skill-factory`
- `python3 Infrastructure/scripts/validation-and-linting/check_skill_factory_system_overlays.py`
- `bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh`

Fail fast: stop at the first failed required gate, classify the failure, and do
not proceed to sync, commit, publish, or install steps until it is fixed or
explicitly marked blocked.

## References

Read only when needed:

- Contract/evals: [references/contract.yaml](./references/contract.yaml),
  [references/evals.yaml](./references/evals.yaml)
- Design check for major authoring:
  [OpenAI-style plugin design contract](../../../../Infrastructure/references/openai-style-plugin-design-contract.md)
- First-principles gate:
  [First-principles factory gate](../../../../Infrastructure/references/first-principles-factory-gate.md)
- Positive/negative operator pattern map:
  [operator-pattern-map.md](../../references/operator-pattern-map.md)
- Live deferred-context policy:
  [live-deferred-context.md](../../references/live-deferred-context.md)
