---
name: claude-alias
description: "Diagnose, repair, and harden Claude wrapper alias routing (`ck`, `cz`, `cc`) when provider configs drift or auth/model conflicts return the wrong backend."
metadata:
  skill-type: infrastructure_ops
  lifecycle_state: active
  maturity: experimental
  owner: Jamie Craik
  last_updated: 2026-04-07
  review_cadence: quarterly
  metadata_source: frontmatter
---

# Claude Alias

## Table of Contents
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Inputs](#inputs)
- [Workflow](#workflow)
- [Validation](#validation)
- [Constraints](#constraints)
- [Anti-Patterns](#anti-patterns)
- [Philosophy](#philosophy)
- [Examples](#examples)
- [Deliverables](#deliverables)
- [Failure handling](#failure-handling)
- [Resources](#resources)

## When to use

Use this skill when a user reports any of the following:
- `ck`, `cz`, and `cc` route to the wrong provider/model.
- Claude CLI shows auth conflicts (token + API key) or repeated 401 errors.
- Alias behavior keeps drifting after updates.
- Shell startup files or `~/.claude/*_settings.json` may have been overwritten.

## When not to use

Route elsewhere when:
- The task is general shell alias customization unrelated to Claude providers.
- The user is asking for app-level Claude usage help, not alias reliability.

## Inputs

- Config repo root (default: `/Users/jamiecraik/dev/configs`)
- Expected canonical alias targets:
  - `~/.claude/claude-aliases.sh` -> `/Users/jamiecraik/dev/configs/claude/bin/claude-aliases.sh`
  - `~/.claude/kimi_settings.json` -> `/Users/jamiecraik/dev/configs/claude/kimi_settings.json`
  - `~/.claude/zai_settings.json` -> `/Users/jamiecraik/dev/configs/claude/zai_settings.json`
- Shell startup file: `~/.zshrc`

## Workflow

1. Run the guard script in check mode to detect drift:
```bash
bash <path-to-skill>/scripts/claude_alias_guard.sh --check
```

2. If drift is detected, run repair mode:
```bash
bash <path-to-skill>/scripts/claude_alias_guard.sh --repair
```
Repair mode now hardens the canonical alias wrapper as well as shell/source-link drift.

3. Re-run check mode and require a clean pass.

4. If provider auth still fails after repair, run one explicit auth-state reset and retest:
```bash
claude auth logout
cz --version
```
If failures persist after that, treat it as credential scope/expiry and not alias drift.

## Validation

The skill is considered successful only when all checks pass:
- Canonical symlinks for alias and provider settings exist.
- `~/.zshrc` contains exactly one Claude alias source line.
- `claude-aliases.sh` still maps:
  - `ck` -> `claude-kimi`
  - `cz` -> `claude-zai`
  - `cc` -> `claude`
- provider launchers enforce API-key-only mode (`--bare`) to prevent token+key auth conflicts.
- `claude()` clears provider-only env state (including `CLAUDE_CONFIG_DIR`) before first-party runs.
- OAuth scrub covers `~/.claude.json`, `~/.claude/.claude.json`, `~/.claude_kimi/.claude.json`, and `~/.claude_zai/.claude.json`.
- `kimi_settings.json` and `zai_settings.json` contain pinned model env values and no literal `${VAR}` placeholders.
- Validation is fail-fast: stop at the first failed gate, repair, then rerun from that gate.

## Constraints

- Do not overwrite unrelated shell configuration lines.
- Do not change provider credentials; only validate routing and config integrity.
- Do not proceed with partial repairs; return non-zero with precise failing checks.

## Anti-Patterns

- Treating 401 responses as alias bugs before running structural guard checks.
- Leaving duplicate alias source lines in `~/.zshrc`.
- Using `${VAR}` placeholders in provider settings JSON env blocks.

## Philosophy

Keep Claude alias routing deterministic:
- one canonical source of wrapper truth,
- one shell source line,
- one repeatable check/repair command path.

## Examples

- Triggering prompt: `When the user asks: "ck keeps opening standard Claude and cz no longer lands on glm-5.1 after shell reload. Please inspect and lock this down."`
- Triggering prompt: `User says: "I keep getting Auth conflict (token + ANTHROPIC_API_KEY) and my wrappers are inconsistent. Can you validate routing but leave credentials alone?"`
- Non-triggering prompt: `Help me compare Claude and GPT pricing for planning work.`

## Deliverables

- Pass/fail summary with each guard check result.
- Exact files repaired (if any).
- Canonical wrapper hardening status (`updated` or `unchanged`) from repair mode.
- Any remaining auth blocker with the safest next command.

## Failure handling

- If a required file is missing, fail fast with the exact path.
- If `jq` is unavailable, report JSON validation as blocked and include a concrete install or fallback command.
- Do not silently continue on partial repairs.

## Required inputs

- Config repo root path (default: `/Users/jamiecraik/dev/configs`)
- Shell startup file path (default: `~/.zshrc`)
- Claude settings links under `~/.claude/`

## Failure mode

- If routing check fails, the guard script returns non-zero with precise failing checks.
- If `jq` is unavailable, JSON validation reports as blocked with install instructions.
- If auth still fails after routing is clean, treat as credential scope/expiry, not alias drift.

## Gotchas

- Do not treat 401 responses as alias bugs before running structural guard checks.
- Avoid duplicate alias source lines in `~/.zshrc`—the guard script enforces exactly one.
- `${VAR}` placeholders in provider settings JSON will fail validation; env vars must be pre-expanded.

## Resources

- `scripts/claude_alias_guard.sh`: deterministic check/repair guardrail.
- `references/alias-hardening-runbook.md`: troubleshooting and operational notes.

## See Also

| Skill | When to use |
|-------|-------------|
| [[fix-mise]] | Diagnose and repair mise trust/runtime issues |
| [[bootstrap]] | Bootstrap a local development environment from a GitHub repository URL |

**Topic map:** [[infrastructure]]
