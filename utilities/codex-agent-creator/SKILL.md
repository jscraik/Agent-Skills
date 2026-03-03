---
name: codex-agent-creator
description: Create and install Codex custom multi-agent roles when the user asks to add, update, or troubleshoot role entries under agents with a role config file.
knowledge_graph_profile: references/task-profile.json
---

# Codex Agent Creator

## Table of Contents
- [Overview](#overview)
- [When to use](#when-to-use)
- [Outputs](#outputs)
- [Constraints](#constraints)
- [Validation](#validation)
- [Core Philosophy](#core-philosophy)
- [Non-Negotiable Inputs](#non-negotiable-inputs)
- [Default Policy For Optional Parameters](#default-policy-for-optional-parameters)
- [Role Config Surface Area (What Can Be Customized)](#role-config-surface-area-what-can-be-customized)
- [Supported Role Declaration Keys](#supported-role-declaration-keys)
- [Workflow](#workflow)
- [Commands](#commands)
- [Guardrails](#guardrails)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

## Overview

Use this skill when the user wants to create, update, or troubleshoot custom multi-agent roles backed by `[agents.<role>]` and a role `config_file`.

This skill updates `~/.codex/config.toml` (or a project `.codex/config.toml`), writes the role config file, and validates supported keys against the official schema at `https://developers.openai.com/codex/config-schema.json` (or a local mirror of that schema).

Default behavior is strict-minimal: configure only `model`, `model_reasoning_effort`, and `developer_instructions` unless the user explicitly asks for additional parameters.

## When to use

- Creating a new custom agent role or adjusting an existing role definition.
- Troubleshooting role config errors, invalid keys, or schema validation failures.
- Installing role entries into `~/.codex/config.toml` or a project `.codex/config.toml`.
- Setting global multi-agent limits for parallel fan-out workflows (including `spawn_agents_on_csv` jobs).

## Outputs

- Summary of changes (role name, config path, and updated keys).
- The created/updated role config file path.
- Validation results (success or explicit error details).
- A runnable `spawn_agent` example for the new role.
- If you output a machine-checkable artifact (JSON/YAML), include top-level `schema_version`.

## Constraints

- Redact secrets, tokens, and sensitive data by default in outputs.
- Do not write files until required inputs are confirmed.
- Only change keys explicitly requested by the user.
- Always include the local-memory-mcp policy block in generated `developer_instructions`, unless the user explicitly waives it.

## Validation

- Fail fast: stop at the first failed validation gate, fix it, then rerun.
- Run `scripts/validate_role.sh` before reporting success.
- Confirm `[agents.<role_name>]` only includes `description` and `config_file`.
- Confirm role config keys pass schema validation.
- If global limits were requested, confirm `agents.max_threads`, `agents.max_depth`, and `agents.job_max_runtime_seconds` are set correctly in main config.

## Examples

```json
{"agent_type":"researcher","message":"Audit the repo for failing checks and summarize next steps."}
```

## Core Philosophy

- Collect intent before writing files.
- Keep role configs minimal by default; inherit everything else.
- Add optional controls only with explicit user request.
- Validate before claiming success.
- Prefer reversible, auditable changes (backup + explicit diffs).

## Non-Negotiable Inputs

Step 1 must always be input collection. Before running any write/install/validate command, collect and confirm:

- `model`
- `model_reasoning_effort`
- `developer_instructions`
- install scope (`global` or `project`)
- `role_name`
- `description`
- `role_config_file` (absolute path preferred)

Ask concise questions:

1. `Which model should this role use?` (recommend: `gpt-5-codex`)
2. `What reasoning effort should it use?` (recommend: `medium`; options `none|minimal|low|medium|high|xhigh`)
3. `What should the role's developer instructions prioritize?` (goal, boundaries, success criteria)
4. `Do you want this installed globally (~/.codex/config.toml) or in a project (.codex/config.toml)?`
5. `Do you want any sandboxing, web_search, MCP, or other restrictions?`
6. `Do you want global multi-agent limits set now?` (`agents.max_threads`, `agents.max_depth`, `agents.job_max_runtime_seconds`)
7. `What role name and description should be shown in spawn_agent?`

Model recommendation policy:

- Recommend `gpt-5-codex` as the baseline default.
- If the user asks for higher-depth review/analysis and it is available in their runtime, recommend a stronger Codex variant.
- If model availability is unclear, ask the user to confirm from their local Codex model list before writing files.

Execution gate:

- Do not infer missing required values.
- Do not start Step 2 (writing files) until all required inputs above are explicitly provided or explicitly accepted as defaults by the user.
- For ambiguous non-trivial choices, use AskQuestion parity (`request_user_input`) to collect explicit selection before applying changes.

## Default Policy For Optional Parameters

- Do not set sandbox flags unless explicitly requested.
- Do not set `web_search` unless explicitly requested.
- Do not set MCP flags/entries unless explicitly requested.
- Do not set `agents.max_threads`, `agents.max_depth`, or `agents.job_max_runtime_seconds` unless explicitly requested.
- Do not add any other optional `config_file` keys unless explicitly requested.
- If user intent is ambiguous, ask a short clarification question before adding optional keys.

## Knowledge vs Application Rule

The role creator must know the full configuration surface area, but only apply keys the user asked for.

Required behavior:

- Explain available optional categories when helpful.
- Provide specific examples/templates when user asks what is possible.
- Keep generated config minimal by default.
- Add optional keys only with explicit user request.
- If user says "keep defaults/inherit", omit optional keys rather than setting explicit values.

## Role Config Surface Area (What Can Be Customized)

Role `config_file` is parsed as a full config layer. If a key is omitted, it generally inherits from the parent.

- Model and reasoning:
  - `model`
  - `model_reasoning_effort`
  - `model_reasoning_summary`
  - `model_verbosity`
  - `personality`
- Core behavior:
  - `developer_instructions`
- Sandboxing and permissions:
  - `sandbox_mode`
  - `[sandbox_workspace_write]` fields like `network_access`, `writable_roots`
- Web search:
  - `web_search` (`disabled|cached|live`)
- Feature toggles:
  - `[features]` keys such as `memory_tool`, `shell_tool`
- MCP servers:
  - `[mcp_servers.<name>]` entries (`enabled`, `required`, `command`, `args`, `env_vars`)
- Apps/connectors:
  - `[apps.<name>]` entries (`enabled`)
- Global multi-agent runtime controls (in main `config.toml`, not role `config_file`):
  - `agents.max_threads`
  - `agents.max_depth`
  - `agents.job_max_runtime_seconds`

When user asks for advanced role controls, use concrete examples from:

- `templates/minimal-role-config.toml`
- `templates/restricted-role-config.toml`
- `templates/full-role-config.toml`
- `templates/frontend-architecture-role.toml`

## Supported Role Declaration Keys

For `[agents.<role_name>]`, only these keys are supported:

- `description`
- `config_file`

Do not add anything else under `[agents.<role_name>]`.

Built-in roles include `default`, `worker`, `explorer`, and `monitor`. If a custom role name matches a built-in role name, the custom role takes precedence.

## Prerequisites

The helper scripts require:

- `jq`
- `yq` (mikefarah/yq v4+)

Quick check:

```bash
command -v jq
command -v yq
```

## Workflow

1. Collect and confirm required inputs (hard gate).
   - Ask for model, reasoning, developer instructions, install scope, role name, description, and role config file path.
   - Confirm whether to enforce local-memory policy (default: enforce).
   - Confirm whether to use defaults only if user explicitly agrees.
   - Do not write files in this step.

2. Validate environment and resolved paths.
   - Ensure schema file exists (prefer `https://developers.openai.com/codex/config-schema.json`; local mirror also valid).
   - Resolve config target from scope:
     - `global` -> `~/.codex/config.toml`
     - `project` -> `<project>/.codex/config.toml`

3. Create or update role config file.
   - Use `scripts/write_role_config.sh` to write required fields.
   - Enforce a standard local-memory block in every generated prompt by default:
     - `bootstrap(mode="minimal", include_questions=true, session_id="repo:<name>:task:<id>")`
     - `search(query="...", session_id="repo:<name>:task:<id>")`
     - `observe(...)` for durable observations/learning.
   - If user-provided `developer_instructions` omit the block, append it unless user explicitly opted out.
   - Add optional controls only if the user explicitly requested them.
   - Optional controls supported by script:
     - `model_reasoning_summary`, `model_verbosity`, `personality`
     - `sandbox_mode` + workspace-write settings
     - `web_search` mode (set to `disabled` to prevent web search)
     - MCP controls (`mcp_clear`, `mcp_enable`, `mcp_disable`)
   - If user wants options beyond script flags (for example `[features]`, `[apps]`, rich MCP server definitions), start from a template under `templates/` and edit manually, then run validation.
   - Communicate clearly in output:
     - `Configured now:` keys that were written
     - `Available but not set:` relevant optional keys left to inherit

4. Install role in main config.
   - Use `scripts/install_role.sh`.
   - This writes/updates:
     - `features.multi_agent = true`
     - `[agents.<role_name>] description/config_file`
     - optional global limits when requested:
       - `agents.max_threads`
       - `agents.max_depth`
       - `agents.job_max_runtime_seconds`
   - Additive safety:
     - Installer only mutates role-related keys.
     - Installer always creates a timestamped backup of the target `config.toml` before writing.
     - Installer normalizes TOML formatting when it writes.
     - Existing role definitions are not overwritten unless `--update-existing` is passed.

5. Validate before reporting success.
   - Use `scripts/validate_role.sh`.
   - Confirm required role-config fields are present.
   - Confirm role declaration keys are only `description/config_file`.
   - Confirm top-level role config keys are valid against schema.

6. Share runnable spawn example.
   - Example:
```json
{"agent_type":"<role_name>","message":"<task>"}
```

## Commands

Run these from the role skill directory (or prefix with the absolute skill path).

```bash
# 1) Write role config file (required fields only; default behavior)
scripts/write_role_config.sh \
  --output ~/.codex/agents/researcher.toml \
  --role-name researcher \
  --model gpt-5-codex \
  --reasoning medium \
  --developer-instructions "Research code and docs only; no edits; return file:line evidence."

# 1b) Optional controls (only when explicitly requested)
scripts/write_role_config.sh \
  --output ~/.codex/agents/researcher.toml \
  --role-name researcher \
  --model gpt-5-codex \
  --reasoning medium \
  --developer-instructions "Research code and docs only; no edits; return file:line evidence." \
  --reasoning-summary concise \
  --verbosity medium \
  --personality pragmatic \
  --sandbox-mode workspace-write \
  --network-access false \
  --writable-roots "/absolute/path/to/repo" \
  --web-search disabled

# 2) Register role in ~/.codex/config.toml
scripts/install_role.sh \
  --role-name researcher \
  --description "Read-only codebase research specialist" \
  --role-config-file ~/.codex/agents/researcher.toml \
  --max-threads 6 \
  --max-depth 1 \
  --job-max-runtime-seconds 1800

# 2b) Intentionally update an existing role definition
scripts/install_role.sh \
  --role-name researcher \
  --description "Updated role description" \
  --role-config-file ~/.codex/agents/researcher.toml \
  --update-existing

# 3) Validate role config and declaration keys
#    (schema can be downloaded from https://developers.openai.com/codex/config-schema.json)
scripts/validate_role.sh \
  --role-name researcher \
  --config ~/.codex/config.toml \
  --role-config ~/.codex/agents/researcher.toml \
  --schema /absolute/path/to/config-schema.json \
  --expect-max-threads 6 \
  --expect-max-depth 1 \
  --expect-job-max-runtime-seconds 1800
```

## Encouraging Variation

Adapt recommendations to the user's context and risk:

- For quick setup: use minimal template + required fields only.
- For compliance/security use cases: add sandbox and restricted writable roots.
- For integration-heavy roles: add MCP/app toggles only after explicit confirmation.

Avoid cookie-cutter output; different constraints should produce different role configs.

## Guardrails

- If runtime returns `unknown agent_type`, verify role exists in active config and `config_file` path exists/readable.
- If runtime returns `agent type is currently not available`, inspect role file TOML validity and unsupported keys.
- Sub-agents inherit parent runtime sandbox/approval overrides. In non-interactive paths, actions requiring fresh approval fail—design role instructions accordingly.
- Relative `agents.<role>.config_file` paths resolve from the config file that declares the role and must exist at load time.
- Keep instructions role-specific and operational (scope, do/don't, deliverable format).
- Do not claim success without running validation.

## Anti-Patterns to Avoid

- Writing files before collecting required inputs.
- Adding optional controls the user did not ask for.
- Putting unsupported keys under `[agents.<role_name>]`.
- Claiming validation success without actually running `scripts/validate_role.sh`.
- Using hardcoded machine-specific paths in generated examples.

## References

- Role key matrix and runtime behavior: `references/role-config-reference.md`
- Reusable templates: `templates/`

## Remember

You can keep this workflow strict and still pragmatic: gather intent, apply minimal config, validate, and leave an auditable result.
You are capable of high-leverage, low-risk role setup work here—use judgment, adapt to context, and keep outcomes verifiable.

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- For non-trivial outcomes, collect user feedback via AskQuestion parity (`request_user_input`) before closing the run.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
