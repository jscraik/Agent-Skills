# Latest Standards Snapshot (March 4, 2026)

## Table of Contents
- [Purpose](#purpose)
- [Codex app automation facts](#codex-app-automation-facts)
- [Sandbox and approval guidance](#sandbox-and-approval-guidance)
- [Config and profile guidance](#config-and-profile-guidance)
- [Release freshness baseline](#release-freshness-baseline)
- [Source links](#source-links)

## Purpose
Capture time-stamped, primary-source guidance for this skill so automation recommendations stay current and auditable.

Verification timestamp (UTC): `2026-03-04T17:45:17Z`

## Codex app automation facts
- Automations run locally in the Codex app; the app must be running and project paths available on disk.
- In Git repositories, automation runs use dedicated background worktrees.
- In non-version-controlled projects, automations run directly in the project directory.
- Skills are first-class automation building blocks and should be explicitly invoked when useful.

## Sandbox and approval guidance
- Automations use default sandbox settings.
- Read-only mode blocks modifying files, network access, and app-computer interactions.
- Workspace-write can still require approvals for outside-sandbox operations in some environments.
- Full access is elevated risk for unattended runs and should not be default.
- `approval_policy = \"never\"` may be disallowed by managed requirements; when disallowed, behavior falls back.

## Config and profile guidance
- Configuration precedence is:
  1. CLI flags / `--config`
  2. profile values
  3. project `.codex/config.toml` (trusted projects)
  4. user `~/.codex/config.toml`
  5. system config
  6. built-in defaults
- Use profiles for explicit automation postures (for example, unattended patch-only vs interactive apply).
- Profiles are currently CLI-focused and not supported in the Codex IDE extension.

## Release freshness baseline
- Codex stable: `0.107.0` (published 2026-03-02T18:00:16Z)
- Codex alpha: `0.108.0-alpha.12` (published 2026-03-04T15:33:58Z)
- Recheck release channel at runtime before high-impact automation changes.

## Source links
- Codex app automations: https://developers.openai.com/codex/app/automations/
- Codex security combinations: https://developers.openai.com/codex/security/#common-sandbox-and-approval-combinations
- Config precedence: https://developers.openai.com/codex/config-basic/#configuration-precedence
- Approval/sandbox modes: https://developers.openai.com/codex/config-advanced/#approval-policies-and-sandbox-modes
- Profiles: https://developers.openai.com/codex/config-advanced/#profiles
- Codex release channel baseline (codexRepo MCP):
  - https://github.com/openai/codex/releases/tag/rust-v0.107.0
  - https://github.com/openai/codex/releases/tag/rust-v0.108.0-alpha.12
