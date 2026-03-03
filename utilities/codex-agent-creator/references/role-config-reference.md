# Role Config Reference (Codex Multi-Agent, March 2026)

## Table of Contents
- [Canonical sources](#canonical-sources)
- [Validation baseline](#validation-baseline)
- [Role declaration shape in `config.toml`](#role-declaration-shape-in-configtoml)
- [Global multi-agent controls](#global-multi-agent-controls)
- [Role `config_file` shape](#role-config_file-shape)
- [Runtime behavior that affects role design](#runtime-behavior-that-affects-role-design)
- [Configuration categories with examples](#configuration-categories-with-examples)
- [Inheritance rule of thumb](#inheritance-rule-of-thumb)

## Canonical sources

- Codex config reference: <https://developers.openai.com/codex/config-reference/>
- Codex multi-agent guide: <https://developers.openai.com/codex/multi-agent/>
- Codex multi-agent concepts: <https://developers.openai.com/codex/concepts/multi-agents/>
- Canonical config schema URL: <https://developers.openai.com/codex/config-schema.json>

## Validation baseline

Use the active Codex schema (`config-schema.json`) for top-level role-config validation.

The role creator scripts validate:
1. `[agents.<role>]` key shape in target `config.toml`
2. required role-config fields (`model`, `model_reasoning_effort`, `developer_instructions`)
3. top-level role-config keys against schema

## Role declaration shape in `config.toml`

```toml
[agents.researcher]
description = "Read-only researcher role"
config_file = "~/.codex/agents/researcher.toml"
```

### Supported keys under `[agents.<role>]`

- `description`
- `config_file`

Unknown fields under `[agents.<role>]` are rejected.

## Global multi-agent controls

These belong under `[agents]` in main config (not inside role `config_file`):

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

## Role `config_file` shape

Role `config_file` is parsed as a full config layer.  
Top-level keys must match schema keys.

### Minimum policy for this skill

Require these fields in every role config:

- `model`
- `model_reasoning_effort`
- `developer_instructions`

Do not add optional keys (`sandbox_mode`, `web_search`, `mcp_servers`, `apps`, etc.) unless explicitly requested.

Recommended default profile (if user does not specify):

- `model = "gpt-5-codex"`
- `model_reasoning_effort = "medium"`

### Useful enums

- `model_reasoning_effort`: `none|minimal|low|medium|high|xhigh`
- `model_reasoning_summary`: `auto|concise|detailed|none`
- `model_verbosity`: `low|medium|high`
- `personality`: `none|friendly|pragmatic`
- `sandbox_mode`: `read-only|workspace-write|danger-full-access`
- `web_search`: `disabled|cached|live`

## Runtime behavior that affects role design

- Spawn starts from parent turn runtime settings.
- Role config is merged as an additional config layer.
- Parent runtime overrides still apply (sandbox/approval settings set interactively or by run mode).
- Relative `config_file` paths resolve from the `config.toml` that declares the role.
- If role config fails to load, spawns can fail until fixed.

Practical implication: keep role instructions narrow and deterministic, and do not rely on role config to sidestep runtime safety settings.

## Configuration categories with examples

### 1) Minimal role (recommended default)

```toml
model = "gpt-5-codex"
model_reasoning_effort = "medium"
developer_instructions = """
You are a focused implementation assistant.
Work only in requested files, validate changes, and report exact evidence.
"""
```

### 2) Model/reasoning/style knobs

```toml
model = "gpt-5-codex"
model_reasoning_effort = "high"
model_reasoning_summary = "concise"
model_verbosity = "high"
personality = "pragmatic"
developer_instructions = "..."
```

### 3) Sandboxing and workspace controls

```toml
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = false
writable_roots = ["/absolute/path/to/repo"]
```

### 4) Search and feature toggles

```toml
web_search = "disabled"

[features]
shell_tool = true
memory_tool = false
```

### 5) MCP server controls (basic and rich)

```toml
[mcp_servers.linear]
enabled = true
required = false
```

```toml
[mcp_servers.linear]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-linear"]
env_vars = ["LINEAR_API_KEY"]
enabled = true
required = false
```

### 6) App connector toggles

```toml
[apps.notion]
enabled = true

[apps.monday]
enabled = false
```

## Inheritance rule of thumb

- Configure only what must differ from parent.
- Leave everything else omitted to inherit.
- Keep role configs minimal unless stronger constraints are explicitly requested.
