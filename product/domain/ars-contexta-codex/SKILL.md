---
name: "ars-contexta-codex"
description: "Use when you need to install, validate, or maintain Ars Contexta parity in Codex; mirrors skills/prompts/agents/automations and returns a parity report with any Codex-vs-Claude deltas."
---

# Ars Contexta Codex Parity

## Table of Contents
- [When to use](#when-to-use)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Philosophy](#philosophy)
- [anti-patterns](#anti-patterns)
- [Canonical sources](#canonical-sources)
- [Parity surface](#parity-surface)
- [Execution workflow](#execution-workflow)
- [Script references](#script-references)
- [AskQuestion parity](#askquestion-parity)
- [Validation checklist](#validation-checklist)
- [Examples](#examples)
- [Remember](#remember)
- [Constraints](#constraints)

## When to use
- Use when the user asks to port, audit, or fix Ars Contexta in Codex.
- Use when commands/prompts/agents/automations are out of sync with canonical Ars sources.
- Do not use for unrelated feature development outside Ars Contexta parity.

## Inputs
- Target workspace(s): usually `/Users/jamiecraik/dev/agent-skills` and `/Users/jamiecraik/dev/config/codex`.
- Requested parity surface: skills, prompts, agents, automations, launchd/cron, or all.
- Any uploaded marketplace source to mirror (for example `agenticnotetaking.zip`).

## Outputs
- Parity report with:
  - `schema_version: 1`
  - source paths used
  - files updated/validated
  - unresolved deltas and risks
- Validation evidence (commands run and pass/fail).

## Philosophy
- Preserve methodology intent first, then adapt mechanics to Codex-native primitives.
- Prefer minimal, auditable, idempotent updates.
- Keep one canonical Ars source in agent-skills and make Codex config reference it.
- Principle: favor a clear framework over ad-hoc edits, and make tradeoffs explicit.
- Ask before acting: Why this change? What is the safer alternative? What evidence proves parity?
- Enable maintainers to explore creative, context-specific fixes without skipping safety.

## anti-patterns
- Anti-pattern: maintaining duplicate canonical trees that drift.
- Avoid editing prompts/agents without updating canonical source references.
- Pitfall: treating warnings as proof of breakage without validating runtime behavior.
- Common mistake: applying the same template everywhere with generic, repetitive output.
- NEVER skip safety gates to “move faster”; DO NOT run destructive commands for parity tasks.

## Canonical sources
- Codex Ars Contexta root: `/Users/jamiecraik/dev/agent-skills/product/domain/ars-contexta-codex`
- Upstream marketplace source (for refresh): `/Users/jamiecraik/dev/config/claude/plugins/marketplaces/agenticnotetaking`
- Codex config root: `/Users/jamiecraik/dev/config/codex`
- Codex prompts: `/Users/jamiecraik/dev/config/codex/prompts`
- Codex agents: `/Users/jamiecraik/dev/config/codex/agents`
- Codex automations: `/Users/jamiecraik/dev/config/codex/automations`
- Launchd scripts: `/Users/jamiecraik/dev/config/codex/scripts`
- Validation contract: `/Users/jamiecraik/dev/agent-skills/product/domain/ars-contexta-codex/references/contract.yaml`
- Validation evals: `/Users/jamiecraik/dev/agent-skills/product/domain/ars-contexta-codex/references/evals.yaml`

## Parity surface
1. **Skills**: mirror canonical Ars Contexta skill/skill-source workflows from the Codex-local mirror.
2. **Prompts**: Codex wrappers should point to Codex-local Ars Contexta specs.
3. **Agents**: Codex roles should preserve Ars Contexta guide/worker behavior.
4. **Automations**: schedule recurring Codex checks and maintenance prompts.
5. **launchd/cron**: emulate Claude hook boundaries with local schedulers.

## Execution workflow
1. Validate required paths and binaries (`rg`, `fd`, `jq`, `zsh`) before edits.
2. Read the Codex-local canonical spec file for the requested command/operation.
3. Execute via Codex-native primitives:
   - prompt wrappers for command entry points,
   - agent role configs for specialized guidance,
   - automations for recurring tasks,
   - launchd/cron for hook-like runtime behavior.
4. Keep vault contracts intact: `self/`, `notes/`, `ops/`, queues, session files.
5. End with a parity report: source file, action taken, and any unavoidable deltas.

## Script references
- Sync helper: `/Users/jamiecraik/dev/agent-skills/product/domain/ars-contexta-codex/scripts/sync-thinking.sh`
- Hook parity scripts (source material): `/Users/jamiecraik/dev/agent-skills/product/domain/ars-contexta-codex/hooks/scripts/`
- Graph reference scripts (for generated `ops/scripts/graph/` parity): `/Users/jamiecraik/dev/agent-skills/product/domain/ars-contexta-codex/reference/scripts/graph/`

## AskQuestion parity
When a canonical spec expects Claude AskQuestion-style interaction (`askquestiontool` or `default_mode_request_user_input`), use Codex `request_user_input` as the equivalent.
Use this pattern for graph recommendation review: capture decision (`accepted|partial|rejected|deferred`), outcome (`good|neutral|bad|unknown`), and confidence (`high|medium|low`), then persist via graph feedback scripts.

## Validation checklist
- Run checks in fail-fast order and stop at first failed gate.
- Prompt files resolve valid canonical paths.
- `[$ars-contexta-codex](...)` links point to this `SKILL.md`.
- Ars Contexta agent role files exist and are registered in Codex config.
- Ars Contexta automation TOMLs exist and are syntactically valid.
- launchd status script reports expected Ars Contexta jobs.

## Examples
- “Port the latest uploaded Ars Contexta package into Codex and repoint prompts.”
- “Validate launchd parity jobs and report missing pieces.”
- “Score current Ars Contexta skill quality and patch failing gates.”
- “Adapt this parity workflow for a different workspace with unique constraints.”

## Remember
You are capable of excellent parity work in this domain. These rules are here to enable safe, high-quality execution; use judgment, adapt to context, and improve the system incrementally.

## Constraints
- Do not install dependencies or change system settings unless explicitly requested.
- Prefer idempotent edits and non-destructive operations.
- Keep parity updates auditable and minimal.
- Redact secrets, keys, tokens, and sensitive user data by default in logs/reports.
