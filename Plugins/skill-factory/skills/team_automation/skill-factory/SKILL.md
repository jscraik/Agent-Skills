---
name: skill-factory
description: Front-door router for the Skill Factory plugin. Use when users ask generally to create, improve, install, or skillify skills and need the correct lane selected before deeper execution.
metadata:
  short-description: Route to the right skill-authoring lane
  skill-type: team_automation
---

# Skill Factory

Route ambiguous skill-authoring requests to the correct lane before executing heavy workflows.

## Table of Contents

- [Philosophy](#philosophy)
- [When to use](#when-to-use)
- [Execution modes](#execution-modes)
- [Routing workflow](#routing-workflow)
- [Required inputs](#required-inputs)
- [Outputs](#outputs)
- [Validation](#validation)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Failure mode](#failure-mode)
- [Examples](#examples)
- [See Also](#see-also)
- [References](#references)

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
- [[skill-refactor]] for session-health scans and skill coverage audits
- [[skillify]] for session-to-skill conversion
- [[skill-installer]] for installation/import flows

## Execution modes

Choose one mode before routing and report it in outputs:
- `direct`: intent is unambiguous, route without clarification.
- `clarify-once`: ask one focused question, then route.

## Routing workflow

1. Identify primary intent: `create`, `improve`, `refactor`, `install`, or `skillify`.
2. Select execution mode:
   - use `direct` when intent is clear;
   - use `clarify-once` when one answer will remove high-risk ambiguity.
3. If intent spans multiple lanes, pick the first lane that unblocks work and state the handoff order.
4. Confirm high-risk ambiguity with one short question only in `clarify-once`.
5. Hand off to the selected lane skill and keep this router out of the execution path.

## Required inputs

Collect only the minimum needed to route safely:
- primary intent (`create|improve|refactor|install|skillify`)
- target artifact path or source repo/path (if provided)
- constraints (security, policy, portability, timeline)

## Deliverables

Return one compact routing handoff object in this shape:

```yaml
schema_version: 1
execution_mode: "direct|clarify-once"
selected_lane: "create|improve|refactor|install|skillify"
reason: "<why this lane was selected>"
next_skill: "[[skill-creator|skill-builder|skill-refactor|skill-installer|skillify]]"
handoff_order:
  - "<lane-1>"
  - "<lane-2>"
required_inputs:
  - "<minimum missing/present inputs for next lane>"
blocked_by:
  - "<blocker>"  # optional
confidence: "high|medium|low"
```

## Validation

- Confirm the selected lane matches the user's primary intent and constraints.
- Confirm all required inputs for that lane are either present or explicitly listed as missing.
- Confirm `next_skill` is one of: `[[skill-creator]]`, `[[skill-builder]]`, `[[skill-refactor]]`, `[[skill-installer]]`, `[[skillify]]`.
- For skill-authoring family changes (`skill-builder`, `skill-creator`, `skill-installer`, `plugin-creator`), require CI `authoring-family-gate` and script `bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh`.
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
- "Scan the last 24h of sessions for skill failures and suggest fixes." -> `selected_lane=refactor`, `next_skill=[[skill-refactor]]`
- "Install two curated skills from openai/skills." -> `selected_lane=install`, `next_skill=[[skill-installer]]`
- "Turn this debugging session into a reusable skill." -> `selected_lane=skillify`, `next_skill=[[skillify]]`

## See Also

| Skill | When to use |
|---|---|
| [[skill-creator]] | Create or refactor skill packages |
| [[skill-builder]] | Run quality gates, evals, and hardening loops |
| [[skill-refactor]] | Scan Codex sessions for skill failures and coverage gaps |
| [[skill-installer]] | Install validated skills from trusted sources |
| [[skillify]] | Capture a completed session as a reusable skill |

## References

- `Infrastructure/references/contract.yaml`
- `Infrastructure/references/evals.yaml`
- `Infrastructure/references/task-profile.json`

## Gotchas
- Symptom: ambiguous scope. Cause: missing constraints. Do instead: ask one routing question. Check: plan and output contract are explicit.
