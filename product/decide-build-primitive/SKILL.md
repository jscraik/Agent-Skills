---
name: decide-build-primitive
description: "Provide a repeatable decision workflow to choose the right Codex primitive (Skill vs Custom Prompt vs Agent/automation) for any requested capability.. Use when Use this skill when the task matches its description and triggers.."
---

# Decide Build Primitive

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md
- Check against GOLD Industry Standards guide in `~/.codex/AGENTS.override.md`.

## Purpose
Provide a repeatable decision workflow to choose the right Codex primitive (Skill vs Custom Prompt vs Agent/automation) for any requested capability.

## When to run
- User asks how to implement/package/structure a capability in Codex.
- You need to choose between Skill, Custom Prompt, or autonomous Agent/`codex exec`.
- You want a reusable, cross-project decision framework.

## Quick use
1) Run the workflow below.  
2) Output must follow the required format block.

## Decision workflow
### Step 1 – Clarify (only ask what’s missing)
- What is being built? Inputs? Outputs? Where/when used?
- Required interaction model: interactive vs delegated vs autonomous?
- Any repo- or domain-specific constraints?

### Step 2 – Evaluate axes
- **Duration & Autonomy**: <5m / 5–15m / 30m+; human-in-loop vs delegated vs autonomous.
- **Context Sensitivity**: Does prior chat/repo help? Is clean-slate required?
- **Invocation Style**: Should it be implicitly triggerable? Must it be explicitly invoked? Who drives execution?
- **Complexity & Scope**: Single capability vs multi-step workflow vs orchestration; number of decision points.
- **Portability**: Cross-project reusable vs repo-specific vs environment-bound.
- **Output Needs**: Guidance only vs documentation/artifacts vs code/diffs/CI outputs.
- **Governance/CI Fit**: Need for repeatable checks, packaging, or later automation hooks.

### Step 3 – Decide
- **Choose SKILL when**: reusable across projects; methodology/checklist/decision logic; benefits from context; lightweight–moderate workflow; implicit triggering valuable.
- **Choose CUSTOM_PROMPT when**: personal/one-off macro; deterministic expansion; explicit invocation is fine; not intended for sharing/enforcement.
- **Choose AGENT_AUTOMATION when**: long-running or autonomous; clean isolation needed; produces structured artifacts/CI tasks; belongs in scripts/pipelines.

### Step 4 – Output (strict format)
Return exactly:
```
DECISION: [SKILL | CUSTOM_PROMPT | AGENT_AUTOMATION]
PRIMARY REASON:
SUPPORTING FACTORS:
IMPLEMENTATION NOTES:
POTENTIAL HYBRID:
```

### Step 5 – Follow-ups
- If AGENT_AUTOMATION: note entrypoint, guardrails, timeout/budget, logging/telemetry.
- If SKILL: outline triggers and any scripts/references/assets to include.
- If CUSTOM_PROMPT: note audience/scope and limitations.

## References
- `references/contract.yaml` — purpose, triggers, inputs/outputs, non-goals, risks.
- `references/evals.yaml` — evaluation cases to validate triggering and outputs.

## When to use
- Use this skill when the task matches its description and triggers.
- If the request is outside scope, route to the referenced skill.


## Inputs
- User request details and any relevant files/links.


## Outputs
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.


## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.


## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.


## Philosophy
- Favor clarity, explicit tradeoffs, and verifiable outputs.


## Anti-patterns
- Avoid vague guidance without concrete steps.
- Do not invent results or commands.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.
