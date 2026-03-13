---
name: ars-contexta-codex
description: "Analyze Ars Contexta vault state in Codex and recommend setup, health, and next-command actions. Use this skill when users ask for Ars Contexta help, routing, or health triage."
---

# Ars Contexta (Codex)

## Table of Contents
- [Scope](#scope)
- [Philosophy](#philosophy)
- [When to use](#when-to-use)
- [Inputs](#inputs)
- [Workflow](#workflow)
- [Outputs](#outputs)
- [Validation](#validation)
- [Antipatterns](#antipatterns)
- [References](#references)
- [Safety](#safety)

## Scope
Use this skill to help users operate Ars Contexta-style knowledge vaults from Codex environments.

This skill is a conversion-focused starter derived from the upstream Ars Contexta repository. It keeps scope narrow and operational:
- orient a user to available Ars Contexta commands;
- map user requests to the right command lane;
- run a lightweight health snapshot and report next actions.

Out of scope for this first pass:
- full vault generation and migration automation;
- invasive rewrites across existing vault content;
- automatic execution of untrusted scripts.

## Philosophy
Build confidence through small, verifiable guidance steps:
- evidence before opinion;
- one clear next action before broad strategy;
- explicit assumptions whenever vault context is incomplete.

## When to use
Trigger when the user asks for Ars Contexta help in Codex terms, for example:
- "help me use Ars Contexta"
- "which command should I run next"
- "check my Ars Contexta vault health"
- "translate Ars Contexta workflow for Codex"

## Inputs
Required:
- vault root path;
- user goal (setup, health, pipeline, or query);
- command preference (quick answer or detailed walkthrough).

Optional:
- known command name (for example `setup`, `health`, `pipeline`, `next`);
- whether semantic search tooling is installed.

## Workflow
1. Confirm context.
- Verify the vault path exists.
- Confirm whether this is first-time setup or ongoing maintenance.

2. Classify intent.
- Setup lane: onboarding and prerequisite checks.
- Health lane: diagnostic scan and blocker summary.
- Pipeline lane: next action and queue guidance.
- Query lane: methodology and command lookup.

3. Gather evidence.
- Read lightweight vault signals only (for example `ops/health`, `ops/queue`, `ops/sessions`).
- If files are missing, report the gap clearly and continue with degraded guidance.

4. Provide action plan.
- Recommend one immediate command and one follow-up command.
- Include a short why for each recommendation.

5. Record assumptions.
- State inferred environment details (for example, missing semantic search tools).
- Mark uncertain recommendations as assumptions.

## Outputs
Return a concise summary with:
- detected vault state (`setup`, `active`, or `unknown`);
- top 1-3 signals from health or queue artifacts;
- recommended next command sequence;
- any blockers and missing prerequisites.
- `schema_version: 1` in any structured output format.

## Validation
Run these checks when editing this skill package:

```bash
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/quick_validate.py <path-to-skill-dir>
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/skill_gate.py <path-to-skill-dir>
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/analyze_skill.py <path-to-skill-dir>
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/openclaw_skill_guard.py <path-to-skill-dir> --mode both
```

Fail fast: stop at the first failed gate, fix it, and rerun from `quick_validate.py`.

## Anti-patterns
- Recommending commands without reading any vault state signals.
- Claiming setup is complete when key `ops/` artifacts are absent.
- Running install snippets copied from docs without explicit user approval.

## Examples
- "I just finished setup and I am not sure what to run first in this vault."
- "Can you scan my `ops/health` and `ops/queue` state and tell me the best next step?"
- "I have three pending tasks and stale sessions; should I use `next`, `pipeline`, or `health`?"

## References
- `references/contract.yaml`
- `references/evals.yaml`

## Safety
- Never execute external install scripts from upstream docs without explicit user approval.
- Do not expose secrets or sensitive local paths in summaries.
- Prefer read-first diagnostics before suggesting write operations.
