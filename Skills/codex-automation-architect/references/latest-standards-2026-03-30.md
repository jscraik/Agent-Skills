# Latest Standards Snapshot (March 30, 2026)

## Table of Contents
- [Purpose](#purpose)
- [Verification timestamp](#verification-timestamp)
- [Codex automation facts](#codex-automation-facts)
- [Sandbox and approvals](#sandbox-and-approvals)
- [Configuration and profiles](#configuration-and-profiles)
- [Release freshness baseline (codexRepo MCP)](#release-freshness-baseline-codexrepo-mcp)
- [RRULE guidance (Context7)](#rrule-guidance-context7)
- [Source links](#source-links)

## Purpose
Capture current, primary-source guidance for Codex automation recommendations so outputs remain auditable and date-scoped.

## Verification timestamp
`2026-03-30T19:02:00Z`

## Codex automation facts
- Automations run in the background in the Codex app.
- The Codex app must be running, and the selected project must be available on disk.
- In Git repositories, automations can run in local mode or dedicated background worktrees.
- In non-version-controlled projects, automations run directly in the project directory.
- `Managing tasks` guidance emphasizes inbox triage plus careful local-vs-worktree selection for isolation.
- Safe rollout pattern: manually test prompts in normal threads before scheduling unattended runs.

## Sandbox and approvals
- Automations are designed for unattended operation and inherit default sandbox settings.
- Read-only mode blocks actions needing file modifications, network access, or computer-app interactions.
- Workspace-write mode still blocks out-of-workspace writes and network/app calls unless explicitly allowed.
- Full access carries elevated risk for unattended runs and should only be used with explicit justification.
- Automations use `approval_policy = "never"` when org policy allows it.
- If org requirements disallow `approval_policy = "never"`, automations fall back to the selected approval behavior.

## Configuration and profiles
- Effective configuration precedence remains:
  1. CLI flags / `--config`
  2. Profile values
  3. Project `.codex/config.toml` (trusted projects)
  4. User `~/.codex/config.toml`
  5. System config
  6. Built-in defaults
- Profiles are still marked experimental.
- Profiles are not currently supported in the Codex IDE extension.

## Release freshness baseline (codexRepo MCP)
- Codex stable: `0.117.0` (`2026-03-26T22:27:39Z`)
- Codex alpha: `0.118.0-alpha.3` (`2026-03-27T23:09:25Z`)
- Recheck channel releases at runtime before high-impact automation recommendations.

## RRULE guidance (Context7)
- Prefer RFC 5545-compatible RRULEs with explicit `freq` and `dtstart`.
- Use `wkst` intentionally for weekly rules where week-boundary semantics matter.
- Use either `count` or `until` with clear intent; avoid ambiguous constraints.
- Set `tzid` for local-time schedules where timezone behavior matters.
- When emitting RRULE examples, keep timezone handling explicit to avoid offset surprises.

## Source links
- Codex automations:
  - https://developers.openai.com/codex/app/automations/
  - https://developers.openai.com/codex/app/automations/#permissions-and-security-model
- Agent approvals and security:
  - https://developers.openai.com/codex/agent-approvals-security/
  - https://developers.openai.com/codex/agent-approvals-security#common-sandbox-and-approval-combinations
- Config:
  - https://developers.openai.com/codex/config-basic/#configuration-precedence
  - https://developers.openai.com/codex/config-advanced/#profiles
  - https://developers.openai.com/codex/config-advanced/#approval-policies-and-sandbox-modes
- Codex releases (codexRepo MCP):
  - https://github.com/openai/codex/releases/tag/rust-v0.117.0
  - https://github.com/openai/codex/releases/tag/rust-v0.118.0-alpha.3
- RRULE library docs (Context7 -> `/jkbrzt/rrule`):
  - https://github.com/jkbrzt/rrule/blob/master/README.md
