# Custom Agent Config Reference (Codex Subagents, April 2026)

## Table of Contents
- [Canonical sources](#canonical-sources)
- [Preferred authoring model](#preferred-authoring-model)
- [Required custom-agent file fields](#required-custom-agent-file-fields)
- [Global agent runtime controls](#global-agent-runtime-controls)
- [Validation baseline](#validation-baseline)
- [Runtime behavior that affects agent design](#runtime-behavior-that-affects-agent-design)
- [Configuration categories with examples](#configuration-categories-with-examples)
- [Inheritance rule of thumb](#inheritance-rule-of-thumb)
- [Compatibility note](#compatibility-note)
- [Upstream alignment snapshot](#upstream-alignment-snapshot)

## Canonical sources

- Codex subagents guide: <https://developers.openai.com/codex/subagents/>
- Codex subagent concepts: <https://developers.openai.com/codex/concepts/subagents/>
- Codex config reference: <https://developers.openai.com/codex/config-reference/>
- Local codex fork deep dive: `~/dev/codex/codex-rs/core/src/config/agent_roles.rs` and `~/dev/codex/docs/config.md`
- Codex release feed for latest checks: <https://github.com/openai/codex/releases>

## Preferred authoring model

As of April 12, 2026 guidance, custom subagents should be authored as standalone TOML files.

In this workspace, the canonical source-of-truth paths are:

- `~/dev/configs/codex/agents/<name>/<name>.toml` for global/shared custom agents
- `~/dev/configs/codex/config.toml` for `[agents.<name>]` mappings and global runtime limits

Runtime/project projections may still exist at:

- `~/.codex/agents/` for personal/global agents
- `.codex/agents/` for project-scoped agents

Treat runtime/project projections as compatibility and discovery surfaces. In this workspace, new writes default to the canonical source-of-truth path above.

Each file defines exactly one custom agent. For global installs, include an explicit `[agents.<name>].config_file` mapping so runtime discovery remains deterministic even when active user config layers are symlinked.

## Required custom-agent file fields

Every standalone custom-agent file must define:

- `name`
- `description`
- `developer_instructions`
- `model`
- `model_reasoning_effort`

Optional fields can include:

- `nickname_candidates`
- `sandbox_mode`
- `mcp_servers`
- `skills.config`
- any other supported `config.toml` keys that are valid for a config layer

### Required example (minimal valid shape)

```toml
name = "reviewer"
description = "PR reviewer focused on correctness, security, and missing tests."
developer_instructions = """
Review code like an owner.
Prioritize correctness, security, behavior regressions, and missing test coverage.
"""
model = "gpt-5.4-mini"
model_reasoning_effort = "medium"
```

### Recommended minimal working profile

```toml
name = "reviewer"
description = "PR reviewer focused on correctness, security, and missing tests."
model = "gpt-5.4-mini"
model_reasoning_effort = "medium"
developer_instructions = """
Review code like an owner.
Prioritize correctness, security, behavior regressions, and missing test coverage.
"""
```

### Useful enums

- `model_reasoning_effort`: `minimal|low|medium|high|xhigh`
- `model_reasoning_summary`: `auto|concise|detailed|none`
- `model_verbosity`: `low|medium|high`
- `personality`: `none|friendly|pragmatic`
- `sandbox_mode`: `read-only|workspace-write|danger-full-access`
- `web_search`: `disabled|cached|live`

## Global agent runtime controls

Global spawned-agent limits belong under `[agents]` in the canonical Codex config (`~/dev/configs/codex/config.toml` by default):

- `agents.max_threads`
- `agents.max_depth`
- `agents.job_max_runtime_seconds`

Example:

```toml
[agents]
max_threads = 6
max_depth = 1
job_max_runtime_seconds = 1800
```

## Validation baseline

For this skill, validation must assert:

1. standalone agent file exists at the expected path
2. `name`, `description`, `developer_instructions`, `model`, and `model_reasoning_effort` are present and non-empty
3. `name` matches the intended installed agent name
4. optional `nickname_candidates`, if present, is unique and uses allowed characters
5. optional global limits match requested values when limit assertions are provided

This baseline intentionally avoids over-restricting optional top-level keys because standalone custom-agent files are config layers and can validly include broader `config.toml` settings.

## Runtime behavior that affects agent design

From current subagents guidance:

- Codex only spawns new subagents when explicitly asked.
- Subagents inherit parent sandbox and approval policy defaults.
- Parent turn runtime overrides are reapplied to children (including interactive override choices).
- Custom-agent defaults still matter, but they do not supersede parent runtime controls.
- If a custom agent name collides with a built-in one, the custom definition takes precedence.

Practical implication: keep instructions narrow and deterministic, and prefer explicit safety boundaries over hidden assumptions.

## Configuration categories with examples

### 1) Minimal custom agent (recommended default)

```toml
name = "implementer"
description = "Implementation-focused worker for scoped code changes."
model = "gpt-5.4-mini"
model_reasoning_effort = "medium"
developer_instructions = """
Own the requested implementation tasks end to end.
Keep changes scoped, run targeted validation, and report evidence.
"""
```

### 2) Read-only reviewer profile

```toml
name = "reviewer"
description = "Find correctness and security risks before merge."
model = "gpt-5.4"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = """
Review code for correctness, security, and behavioral regressions.
Lead with concrete findings and reproduction guidance.
"""
```

### 3) Optional display nicknames

```toml
name = "reviewer"
description = "PR reviewer focused on correctness and tests."
model = "gpt-5.4-mini"
model_reasoning_effort = "medium"
developer_instructions = "Review code like an owner."
nickname_candidates = ["Atlas", "Delta", "Echo"]
```

## Inheritance rule of thumb

- Configure only what must differ from parent.
- Leave everything else omitted to inherit.
- Keep custom-agent files minimal unless stronger constraints are explicitly requested.

## Compatibility note

`config-reference` still documents `agents.<name>.description`, `agents.<name>.config_file`, and `agents.<name>.nickname_candidates`. In this workspace, keep standalone custom-agent files as canonical source under `~/dev/configs/codex/agents/`, and keep explicit `[agents.<name>]` mappings in `~/dev/configs/codex/config.toml` for runtime discoverability. `.codex/agents/` and `~/.codex/agents/` are compatibility/runtime projections and require explicit override intent before writes.

## Upstream alignment snapshot

- Latest stable release observed: `openai/codex` `0.120.0` (published 2026-04-11 UTC).
- Latest alpha release observed: `openai/codex` `0.121.0-alpha.2` (published 2026-04-11 UTC).
- OpenAI Codex config reference still documents default user config path `~/.codex/config.toml`.
- Local fork deep dive confirms role discovery from each config-layer `agents/` directory and strict validation of `description`, `developer_instructions`, and `nickname_candidates` hygiene.
- Repository policy decision for this skill: write new global agents and `[agents]` runtime keys to `~/dev/configs/codex/agents/` and `~/dev/configs/codex/config.toml` by default.
