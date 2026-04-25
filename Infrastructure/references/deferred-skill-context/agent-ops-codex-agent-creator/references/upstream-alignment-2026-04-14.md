# Upstream Alignment Snapshot (2026-04-14)

## Why this exists

This snapshot records the latest upstream facts used to keep `codex-agent-builder` aligned with current Codex behavior while preserving this repository's canonical write policy.

## Evidence checked

- OpenAI docs (`developers.openai.com/codex/config-reference#configtoml`, fetched 2026-04-14): default user config path remains `~/.codex/config.toml`; runtime keys include `agents.max_threads`, `agents.max_depth`, `agents.job_max_runtime_seconds`, and `model_reasoning_effort` enum values `minimal|low|medium|high|xhigh`.
- OpenAI docs also confirm `config-schema.json` and that `experimental_instructions_file` is deprecated in favor of `model_instructions_file`.
- Codex repo MCP (`openai/codex`, checked 2026-04-14): latest releases observed were stable `0.120.0` and alpha `0.121.0-alpha.9`.
- Local fork deep dive (`~/dev/codex`, checked 2026-04-14):
  - `codex-rs/core/src/config/agent_roles.rs` validates role-file `developer_instructions` and requires non-empty role `description`.
  - Role discovery scans each config-layer `agents/` directory.
  - Nickname candidates are normalized, must be non-empty, unique, and ASCII-safe.

## Repository policy application

- Keep upstream-compatible role file shape (`name`, `description`, `developer_instructions`, `model`, `model_reasoning_effort`, plus optional config-layer keys).
- Use repository-canonical write targets for new global installs:
  - `~/dev/configs/codex/agents/`
  - `~/dev/configs/codex/config.toml`
- Treat `~/.codex/agents/` and `.codex/agents/` as compatibility/runtime projection surfaces unless a caller explicitly opts out.
