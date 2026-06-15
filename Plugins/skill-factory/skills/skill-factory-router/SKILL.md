---
name: skill-factory-router
description: "Analyzes Codex skill-management requests, selects the workflow lane, and returns selected_lane, mode, next_step, and blockers. Use when the user says create a skill, add/update/fix/review a skill, install/sync/list skills, choose a workflow, or merge/retire a skill."
metadata:
  version: "1.0.0"
  skill-type: team_automation
  lifecycle_state: active
  maturity: canonical
  owner: Agent Skills Team
  provenance: frontmatter:Agent Skills Team:2026-05-28:canonical-source
  share_readiness: ready
  review_cadence: quarterly
  last_reviewed: "2026-05-28"
  metadata_source: frontmatter
  compatible_roles: default, worker, skill-inspector
  runtime_needs: repo-owned skill source path; Skill Factory skill inventory; ./bin/ask skills external-review
---

# Skill Factory Router

Select one downstream workflow for Codex skill-management requests. Return the routing handoff before loading deeper instructions.

## When to use

Use when the user asks to create, capture, improve, audit, refactor, install, sync, or route a Codex skill and the correct Skill Factory lane is not already certain.

## Required inputs

- User request or named target skill.
- Current authority boundary: read-only routing, approved edit, install/sync, or eval execution.
- Available evidence handle when the request depends on Tessl, Plugin Eval, validation, runtime, or session artifacts.

## Deliverables

- One YAML handoff with `schema_version`, `selected_lane`, `mode`, `rationale`, `next_step`, `first_principles_check`, and `blocked_by`.
- Expected artifacts: no source edits from the router itself; downstream lanes own review reports, eval artifacts, package outputs, and runtime evidence.

## Discovery Interview

When target, lane, write authority, or validation requirement is missing, ask one plain-language question. Use [discovery interview](./references/discovery-interview.md) only when the ambiguity cannot be resolved from the user request.

## Decision Table

| User says | Selected lane | Mode |
| --- | --- | --- |
| create a skill, draft a new skill, make a new `SKILL.md` | `.system/skill-creator` | `create` |
| skillify this workflow, save this process as a skill, make reusable guidance | `skillify` | `capture` |
| fix this skill, improve this skill, raise Tessl score, repair evals, reduce token cost | Skill Factory hardening workflow | `harden` |
| why is this skill failing, compare duplicate skills, merge this skill, retire this skill | `skill-refactor` | `analyze` |
| install a skill, list skills, sync skills, prove Codex can see a skill | `.system/skill-installer` | `install` |
| copy or fork the system skill creator or installer into Skill Factory | block fork; route to the matching system lane | `create` or `install` |

For `.system/skill-creator` or `.system/skill-installer`, attach Skill Factory references or eval contracts; do not fork the system skill body.

## Philosophy

Route to the smallest durable factory surface that can prove the result. Prefer existing system lanes, validators, scripts, and references over new skill bodies when they already encode the contract.

## Procedure

Apply the context-disposition policy: move important still-valid context to references, and intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.

1. Match the request to the decision table. Explicit lane names win unless the user names multiple lanes or asks for an unsafe action.
2. If target, authority, evidence, or lane selection is ambiguous, ask one blocking discovery question.
3. For major new-skill or broad-rewrite requests, check whether the better answer is a skill, docs, script, hook, validator, rule, or direct answer.
4. Return the handoff template and stop unless the user explicitly asks this router to execute the selected lane.

Use `Infrastructure/references/first-principles-factory-gate.md` as the factory gate for broad create, harden, merge, or retire decisions.

## Handoff Template

Return:

```yaml
schema_version: 1
selected_lane: .system/skill-creator|skillify|skill-factory-router|skill-refactor|.system/skill-installer
mode: create|capture|harden|analyze|install
rationale: <one sentence tied to the request shape>
next_step: <specific skill or system lane to load next>
first_principles_check:
  required: true|false
  result: skill|docs|script|hook|validator|rule|answer|not_checked
blocked_by: null
```

## Example

User: "Tessl says this skill has weak content; inspect it and validate the fix."

Return:

```yaml
schema_version: 1
selected_lane: skill-factory-router
mode: harden
rationale: The user has an existing skill with Tessl and local audit findings.
next_step: Use the Skill Factory hardening workflow, patch the canonical target skill, then rerun strict audit and local external review.
first_principles_check:
  required: false
  result: not_checked
blocked_by: null
```

## Constraints

- Keep routing read-only: do not edit, install, sync, publish, mutate trackers, run downstream commands, or load references before lane selection.
- Route plugin package lifecycle work to `plugin-factory`.
- Route system creator and installer requests to the system lanes, not forks.
- Claim environment/auth/runtime state only from current-turn evidence, and redact secrets, tokens, PII, and sensitive local paths.

## Execution Boundaries

- This router only selects a lane and reports the next action.
- Downstream lanes own source edits, runtime sync, external review, Tessl evals, packaging, publishing, and install proof.
- A route decision is not proof that a skill is installed, visible in Codex, or passing evals.

## Anti-Patterns

- Do not resurrect retired flat command handles, generated aliases, or
  projection-only manifest rows to satisfy a route, projection, or test.
- Do not copy the system skill creator or installer into Skill Factory when the system lane can be referenced.
- Do not treat plugin-cache visibility, command-surface rows, and flat skill symlinks as the same proof surface.

## Failure Mode

If no single lane fits, set `blocked_by` to the ambiguity and ask the smallest routing question.

## Gotchas

- `skill-builder` is a canonical package under
  `skills/code_quality_review/skill-builder`; keep flat command handles and
  generated aliases separate from that source package.
- Runtime picker visibility depends on regenerated projections and local sync, not only canonical source edits.
- Use exact current evidence before claiming Tessl, plugin cache, command surface, or Codex picker state.

## Validation

Run `bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh` and `./bin/ask skills external-review Plugins/skill-factory/skills/skill-factory-router --audit-level compat --json`.

Fail fast: stop at the first failed required gate, classify it, and do not sync, commit, publish, or install until it is fixed or explicitly blocked.

## References

Load only the reference needed for the selected routing question:

Read when:
- You need package contract or eval expectations: [contract](./references/contract.yaml), [evals](./references/evals.yaml), [task profile](./references/task-profile.json).
- You need ambiguous request questions: [discovery interview](./references/discovery-interview.md).
- You need source-repo routing policy handles: [routing policy](./references/routing-policy.md).
