# Codex Hook Pack

## Table of Contents
- [Overview](#overview)
- [Files](#files)
- [Install shape](#install-shape)
- [What this pack does](#what-this-pack-does)
- [Validation](#validation)

## Overview
This hook pack was scaffolded from `utilities/codex-hooks-builder` and targets
the March 2026 supported Codex command-hook contract.

## Files
- `/Users/jamiecraik/dev/Agent-Skills/.codex/hooks.json`
- `/Users/jamiecraik/dev/Agent-Skills/.codex/hooks/session-start.sh`
- `/Users/jamiecraik/dev/Agent-Skills/.codex/hooks/user-prompt-submit.sh`
- `/Users/jamiecraik/dev/Agent-Skills/.codex/hooks/stop-guard.sh`

## Install shape
- active config layer: `/Users/jamiecraik/dev/Agent-Skills/.codex`
- hook scripts folder: `/Users/jamiecraik/dev/Agent-Skills/.codex/hooks`
- command paths in `hooks.json` are absolute so they keep working from nested working directories

## What this pack does
- `SessionStart` adds concise repo-aware startup context
- `UserPromptSubmit` blocks obvious instruction-bypass attempts and annotates risky shortcuts
- `Stop` blocks clearly incomplete final handoffs once, then fails open on retry

## Validation
```bash
zsh -n /Users/jamiecraik/dev/Agent-Skills/.codex/hooks/session-start.sh
zsh -n /Users/jamiecraik/dev/Agent-Skills/.codex/hooks/user-prompt-submit.sh
zsh -n /Users/jamiecraik/dev/Agent-Skills/.codex/hooks/stop-guard.sh
jq . /Users/jamiecraik/dev/Agent-Skills/.codex/hooks.json
```
