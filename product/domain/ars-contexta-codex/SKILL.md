---
name: "ars-contexta-codex"
description: "Mirror Ars Contexta Claude plugin behavior in Codex using skills, prompts, agents, automations, and launchd/cron-compatible operations."
---

# Ars Contexta Codex Parity

## Table of Contents
- [Purpose](#purpose)
- [Canonical sources](#canonical-sources)
- [Parity surface](#parity-surface)
- [Execution workflow](#execution-workflow)
- [AskQuestion parity](#askquestion-parity)
- [Validation checklist](#validation-checklist)
- [Constraints](#constraints)

## Purpose
Use this skill to keep Codex behavior as close as possible to the Ars Contexta Claude plugin while preserving Codex-native execution.

## Canonical sources
- Codex Ars Contexta root: `/Users/jamiecraik/dev/agent-skills/product/domain/ars-contexta-codex`
- Upstream marketplace source (for refresh): `/Users/jamiecraik/dev/config/claude/plugins/marketplaces/agenticnotetaking`
- Codex config root: `/Users/jamiecraik/dev/config/codex`
- Codex prompts: `/Users/jamiecraik/dev/config/codex/prompts`
- Codex agents: `/Users/jamiecraik/dev/config/codex/agents`
- Codex automations: `/Users/jamiecraik/dev/config/codex/automations`
- Launchd scripts: `/Users/jamiecraik/dev/config/codex/scripts`

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

## AskQuestion parity
When a canonical spec expects Claude AskQuestion-style interaction (`askquestiontool` or `default_mode_request_user_input`), use Codex `request_user_input` as the equivalent.

## Validation checklist
- Prompt files resolve valid canonical paths.
- `[$ars-contexta-codex](...)` links point to this `SKILL.md`.
- Ars Contexta agent role files exist and are registered in Codex config.
- Ars Contexta automation TOMLs exist and are syntactically valid.
- launchd status script reports expected Ars Contexta jobs.

## Constraints
- Do not install dependencies or change system settings unless explicitly requested.
- Prefer idempotent edits and non-destructive operations.
- Keep parity updates auditable and minimal.
