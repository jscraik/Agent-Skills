---
name: skill-factory-router
description: "Routes Codex skill lifecycle requests by selecting one Skill Factory lane, mode, and handoff. Use when users ask to create a skill, skillify a workflow, fix or audit a skill, improve skill quality, analyze routing failures, install a skill, or decide whether to keep, merge, split, or retire skill guidance."
metadata:
  version: "1.0.0"
  skill-type: team_automation
---

# Skill Factory Router

Choose one Skill Factory lane before loading deeper instructions or editing files.

## Philosophy

Route first, then load details. A good router narrows the work to one lane, keeps scope tight, and prevents accidental broad edits.

## When To Use

- The request is about creating, hardening, auditing, installing, refactoring, skillifying, evaluating, or retiring Codex skills.
- The user names a skill, plugin skill, skill handle, runtime skill, or repeatable workflow that may become skill guidance.
- The next step should be a lane handoff, not implementation.

Do not use for ordinary product implementation, generic repo maintenance, or plugin package lifecycle work that belongs to `plugin-factory`.

## Inputs

- User intent and target artifact, when available.
- Explicit skill names, plugin paths, install sources, or evidence paths.
- Stated write authority, publication target, validation requirement, or approval boundary.

## Outputs

- Exactly one selected Skill Factory lane.
- A mode, rationale, next step, and blocker field.
- One first-principles check when the request could be better served by docs, scripts, hooks, validators, rules, or a direct answer.

## Decision Table

| Request shape | Selected lane | Mode |
| --- | --- | --- |
| create a skill, draft a new skill, new SKILL.md | `.system/skill-creator` | `create` |
| skillify this, save this workflow, make reusable guidance | `skillify` | `capture` |
| fix this skill, improve quality, repair evals, reduce token cost | `skill-builder` | `harden` |
| why is this skill failing, review skill health, merge or retire | `skill-refactor` | `analyze` |
| install skill, list skills, sync skill, prove runtime visibility | `.system/skill-installer` | `install` |

Explicit lane names win unless the user names multiple lanes or asks for an unsafe action.

## Procedure

1. Identify the target artifact and desired outcome.
2. Choose exactly one primary lane.
3. For major new-skill or broad-rewrite requests, make one first-principles check: skill vs docs vs script vs hook vs validator vs answer.
4. Return the handoff template below.
5. Load the selected lane only after routing is complete.
6. If lane choice affects writes and evidence is ambiguous, ask one blocking question or state one bounded assumption.

## Handoff Template

Return:

```yaml
schema_version: 1
selected_lane: .system/skill-creator|skillify|skill-builder|skill-refactor|.system/skill-installer
mode: create|capture|harden|analyze|install
rationale: <one sentence tied to the request shape>
next_step: <specific skill or system lane to load next>
first_principles_check:
  required: true|false
  result: skill|docs|script|hook|validator|rule|answer|not_checked
blocked_by: null
```

## Examples

- When the user asks, "Can you convert this successful GitHub release triage process into a skill?" -> `selected_lane: skillify`, `mode: capture`.
- When the user says, "Tessl says this skill has weak content; inspect it and validate the fix." -> `selected_lane: skill-builder`, `mode: harden`.
- When the user asks, "Which HE skill should we merge or retire after these session failures?" -> `selected_lane: skill-refactor`, `mode: analyze`.
- When the user says, "Install this skill and validate Codex can see it." -> `selected_lane: .system/skill-installer`, `mode: install`.

Example return:

```yaml
schema_version: 1
selected_lane: skill-builder
mode: harden
rationale: The user has an existing skill with Tessl and local audit findings.
next_step: Load skill-builder, patch the canonical target skill, then rerun strict audit and local external review.
first_principles_check:
  required: false
  result: not_checked
blocked_by: null
```

## Constraints And Boundaries

- Keep routing read-only.
- Prefer explicit user lane names unless multiple lanes or unsafe actions are requested.
- Ask one blocking question only when target, authority, or lane selection cannot be inferred safely.
- Redact secrets, credentials, API keys, tokens, PII, and sensitive data by default.

## Execution Boundaries

- Do not edit, install, sync, refresh projections, publish, or mutate trackers here.
- Do not load every reference before selecting a lane.
- Treat archive and deferred-store content as historical evidence, not live runtime context.
- Redact secrets, credentials, API keys, tokens, PII, and sensitive local paths.

## Failure Mode

If no single lane fits, return `blocked_by` with the ambiguity and the smallest question needed to route.

## Gotchas

- Plugin package lifecycle work belongs to `plugin-factory`, not this router.
- Broad "review this skill" requests may mean lifecycle analysis, not immediate edits.
- Generated overlays can mention system lanes that are not direct source-edit targets.

## Anti-Patterns

- Loading every Skill Factory reference before choosing a lane.
- Doing implementation work inside the router.
- Treating historical fixtures as current skill source.

## Validation

Run `python3 Infrastructure/scripts/validation-and-linting/check_plugin_active_archive_links.py --plugin skill-factory`, `python3 Infrastructure/scripts/validation-and-linting/check_skill_factory_system_overlays.py`, `bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh`, and `python3 Infrastructure/bin/ask skills external-review Plugins/skill-factory/skills/skill-factory-router --audit-level compat --json`.

Fail fast: stop at the first failed required gate, classify it, and do not sync, commit, publish, or install until it is fixed or explicitly blocked.

## References

- Local contract, evals, and task profile: `references/`
- Major authoring design check: `Infrastructure/references/openai-style-plugin-design-contract.md`
- First-principles gate: `Infrastructure/references/first-principles-factory-gate.md`
- Operator pattern map: `Plugins/skill-factory/references/operator-pattern-map.md`
- Live deferred-context policy: `Plugins/skill-factory/references/live-deferred-context.md`
