# Role Config Reference

## Source Baseline (Pinned)

This skill was installed from:

- `am-will/codex-skills` commit `21b613ea28df6c8bf2f2a452ed07ef1f96f53184`
- Skill path: `skills/codex-agent-creator`
- Companion role pack examples: `agents/`

## Canonical Validation Inputs

Use the active Codex `config.schema.json` for top-level key validation.

Typical locations:

- Local Codex source checkout: `codex-rs/core/config.schema.json`
- If you keep multiple Codex repos, use the one matching your installed Codex build.

The role creator scripts validate:

1. `[agents.<role>]` key shape in the target `config.toml`
2. required role-config fields
3. top-level role-config keys against `config.schema.json`

## Role Declaration Shape (`~/.codex/config.toml`)

```toml
[agents.researcher]
description = "Read-only researcher role"
config_file = "~/.codex/agents/researcher.toml"
```

### Supported keys under `[agents.<role>]`

- `description`
- `config_file`

Anything else under `[agents.<role>]` is unsupported.

## Role `config_file` Shape

Role `config_file` is parsed as a full config layer.
Top-level keys must be valid top-level keys from `config.schema.json`.

### Minimum policy for this skill

Require these fields in every role config:

- `model`
- `model_reasoning_effort`
- `developer_instructions`

Do not add optional keys (sandbox, `web_search`, `mcp_servers`, or others) unless explicitly requested by the user.

Recommended default profile (when user does not specify):

- `model = "gpt-5.3-codex"`
- `model_reasoning_effort = "medium"`

### Useful enums

- `model_reasoning_effort`: `none|minimal|low|medium|high|xhigh`
- `sandbox_mode`: `read-only|workspace-write|danger-full-access`
- `web_search`: `disabled|cached|live`

## Runtime Merge Notes

- Spawn starts from parent turn config.
- Role config file is merged as a config layer.
- Spawn-time constraints can still apply (for example, approval policy set by runtime).

Practical implication: role config can tune model/sandbox/tools/etc., but runtime-enforced overrides still win.

## Configuration Categories With Examples

### 1) Minimal role (recommended default)

```toml
model = "gpt-5.3-codex"
model_reasoning_effort = "medium"
developer_instructions = """
You are a focused implementation assistant.
Work only in requested files, validate changes, and report exact evidence.
"""
```

### 2) Model/reasoning/style knobs

```toml
model = "gpt-5.3-codex"
model_reasoning_effort = "high"
model_reasoning_summary = "detailed"
model_verbosity = "high"
personality = "pragmatic"
developer_instructions = "..."
```

### 3) Sandboxing and workspace controls

```toml
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = true
writable_roots = ["/absolute/path/to/repo"]
```

### 4) Search and feature toggles

```toml
web_search = "cached"

[features]
memory_tool = false
shell_tool = false
```

### 5) MCP server controls (basic and rich)

Basic enable/disable:

```toml
[mcp_servers.linear]
enabled = true
required = false
```

Rich server definition:

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

## Inheritance Rule Of Thumb

- Configure only what must differ from parent.
- Leave everything else omitted to inherit.
- Prefer minimal role config unless user explicitly requests stronger constraints.
