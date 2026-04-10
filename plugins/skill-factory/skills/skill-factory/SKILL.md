---
name: skill-factory
description: Front-door router for the Skill Factory plugin. Use when users ask generally to create, improve, install, or skillify skills and need the correct lane selected before deeper execution.
metadata:
  short-description: Route to the right skill-authoring lane
---

# Skill Factory

Route ambiguous skill-authoring requests to the correct lane before executing heavy workflows.

## Philosophy

- Route first, execute second.
- Ask one focused clarification when classification is ambiguous.
- Keep handoff contracts explicit so downstream lane skills can run without reinterpretation.

## When to use

Use this router when the request is broad or mixed, for example:
- "Help me with a skill"
- "Can you package this workflow?"
- "I need to install or improve a skill"

Skip this router when the user explicitly requests one lane:
- [[skill-creator]] for first-draft creation
- [[skill-builder]] for hardening/evals/quality work
- [[skillify]] for session-to-skill conversion
- [[skill-installer]] for installation/import flows

## Routing workflow

1. Identify primary intent: `create`, `improve`, `install`, or `skillify`.
2. If intent spans multiple lanes, pick the first lane that unblocks work and state the handoff order.
3. Confirm any high-risk ambiguity in one short question.
4. Hand off to the selected lane skill and keep this router out of the execution path.

## Required inputs

Collect only the minimum needed to route safely:
- primary intent (`create|improve|install|skillify`)
- target artifact path or source repo/path (if provided)
- constraints (security, policy, portability, timeline)

## Outputs

Return a compact routing handoff object:
- `schema_version`
- `mode`
- `selected_lane`
- `reason`
- `next_skill`
- `required_inputs`
- `blocked_by` (if any)

## Validation

- Confirm the selected lane matches the user's primary intent and constraints.
- Confirm all required inputs for that lane are either present or explicitly listed as missing.
- Do not run lane-specific scripts from this router.
- Fail fast: stop at the first failed gate, fix or report the blocker, and do not continue with downstream execution.

## Constraints

- Redact secrets, credentials, tokens, and sensitive personal data by default.
- Keep routing decisions reversible; avoid destructive actions at router stage.
- Prefer offline-safe triage and ask before network-dependent operations.

## Anti-patterns

- Running lane-specific tooling before intent classification is complete.
- Guessing a lane when a single clarification question would remove risk.
- Returning broad advice without naming a concrete next skill/handoff.

## Failure mode

If intent cannot be classified with safe confidence:
- ask one direct clarification question,
- avoid running lane-specific scripts,
- report the blocker and the minimum required answer.

## Examples

- "Create a new skill for release-note drafting." -> `selected_lane=create`, `next_skill=[[skill-creator]]`
- "Audit and harden this existing skill before rollout." -> `selected_lane=improve`, `next_skill=[[skill-builder]]`
- "Install two curated skills from openai/skills." -> `selected_lane=install`, `next_skill=[[skill-installer]]`
- "Turn this debugging session into a reusable skill." -> `selected_lane=skillify`, `next_skill=[[skillify]]`

## See Also

| Skill | When to use |
|---|---|
| [[skill-creator]] | Create or refactor skill packages |
| [[skill-builder]] | Run quality gates, evals, and hardening loops |
| [[skill-installer]] | Install validated skills from trusted sources |
| [[skillify]] | Capture a completed session as a reusable skill |

## References

- `references/contract.yaml`
- `references/evals.yaml`
- `references/task-profile.json`
