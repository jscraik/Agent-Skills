# Alias Hardening Runbook

## Table of Contents
- [Goal](#goal)
- [Fast path](#fast-path)
- [What the guard enforces](#what-the-guard-enforces)
- [Troubleshooting](#troubleshooting)

## Goal

Keep `ck`, `cz`, and `cc` pinned to their intended providers even after CLI updates, shell profile edits, or config drift.

## Fast path

From any shell:

```bash
bash /Users/jamiecraik/dev/agent-skills/.agents/skills/claude-alias/scripts/claude_alias_guard.sh --check
bash /Users/jamiecraik/dev/agent-skills/.agents/skills/claude-alias/scripts/claude_alias_guard.sh --repair
bash /Users/jamiecraik/dev/agent-skills/.agents/skills/claude-alias/scripts/claude_alias_guard.sh --check
```

## What the guard enforces

- Canonical symlinks:
  - `~/.claude/claude-aliases.sh` -> `/Users/jamiecraik/dev/config/claude/bin/claude-aliases.sh`
  - `~/.claude/kimi_settings.json` -> `/Users/jamiecraik/dev/config/claude/kimi_settings.json`
  - `~/.claude/zai_settings.json` -> `/Users/jamiecraik/dev/config/claude/zai_settings.json`
- Exactly one alias source line in `~/.zshrc`
- Stable alias routing (`ck`/`cz`/`cc`)
- Pinned model defaults in provider settings JSON
- No literal `${VAR}` placeholders in provider settings JSON env blocks

## Troubleshooting

- Guard passes but CLI still returns 401:
  - Routing is likely correct; credentials are likely expired or mismatched.
  - Re-login or rotate provider keys, then re-test.

- Guard fails on `jq unavailable`:
  - Install `jq` (`brew install jq`) or run a fallback JSON inspection command.

- Guard keeps failing on symlink checks:
  - Confirm the config repo exists at `/Users/jamiecraik/dev/config`.
  - If repo path changed, set `CLAUDE_CONFIG_ROOT` before running guard.

