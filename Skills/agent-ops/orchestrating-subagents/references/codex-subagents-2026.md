# Codex Subagents 2026

Current OpenAI-backed guidance for Codex-native subagent workflows.

## Table of Contents
- [Why this reference exists](#why-this-reference-exists)
- [Current Codex contract](#current-codex-contract)
- [Model guidance](#model-guidance)
- [Design pattern choice](#design-pattern-choice)
- [Local roster alignment](#local-roster-alignment)
- [Implications for this skill](#implications-for-this-skill)
- [Sources](#sources)

## Why this reference exists
The upstream `orchestrating-swarms` skill was built around Codex team, teammate, inbox, and task primitives. Codex in March 2026 exposes a different runtime:
- parent-mediated subagents
- custom agent roles
- shared sandbox inheritance
- shallow, explicit delegation

This reference keeps the converted skill aligned to the actual Codex contract rather than the older swarm runtime.

## Current Codex contract
- Codex subagent workflows are enabled by default in current releases.
- Codex only spawns subagents when the user explicitly asks for them.
- The parent thread owns orchestration: spawning, follow-up instructions, waiting, and closing completed agents.
- Built-in roles include `default`, `worker`, and `explorer`.
- Custom agents can override normal config keys such as `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, and `skills.config`.
- Current docs recommend keeping `agents.max_depth` low. A depth of `1` is the default and is the safest baseline for predictable shallow delegation.
- Subagents inherit the parent sandbox and approval posture, with parent turn runtime overrides reapplied when the child is spawned.

## Model guidance
OpenAI's March 17, 2026 announcement recommends a split pattern:
- `gpt-5.4` for planning, coordination, and final judgment
- `gpt-5.4-mini` for narrower supporting subtasks in parallel

That makes `gpt-5.4-mini` the default choice for read-heavy reviewers, explorers, docs researchers, and bounded workers unless the task is unusually high-stakes.

## Design pattern choice
Context7's OpenAI Agents JS docs describe two common multi-agent patterns:
- **Manager or agents-as-tools**: one coordinator delegates to specialized workers while keeping overall control.
- **Handoffs**: control transfers to a specialist for the rest of the interaction.

For Codex subagents, this skill should prefer the manager pattern because the Codex parent thread remains the coordinator and integration point. That maps much more closely to Codex's `spawn_agent` plus `wait_agent` model than a full handoff does.

## Local roster alignment
This environment already includes a strong installed roster:
- `explorer`
- `worker`
- `monitor`
- `framework-docs-researcher`
- `security-sentinel`
- `performance-oracle`
- `architecture-strategist`
- multiple language-specific reviewers

For general-purpose review fan-out, use `correctness-reviewer` as the default base reviewer and add narrower specialists only when justified.

## Implications for this skill
- Keep the root agent as the orchestrator.
- Prefer read-only fan-out first.
- Treat same-checkout parallel writes as opt-in and narrow.
- Route broad or conflicting write work to `using-git-worktrees`.
- Use installed roles first, and only co-trigger `codex-agent-builder` when the roster truly lacks a needed specialty.

## Sources
- OpenAI Codex Subagents docs: https://developers.openai.com/codex/subagents
- OpenAI Codex customization docs: https://developers.openai.com/codex/concepts/customization/#next-step
- OpenAI Codex config reference: https://developers.openai.com/codex/config-reference/#configtoml
- OpenAI GPT-5.4 mini and nano announcement: https://openai.com/index/introducing-gpt-5-4-mini-and-nano/
- Context7 OpenAI Agents JS docs: `/openai/openai-agents-js`
- Codex repo orchestrator template: https://github.com/openai/codex/blob/main/codex-rs/core/Infrastructure/templates/agents/orchestrator.md
