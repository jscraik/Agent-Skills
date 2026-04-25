# Headless Eval Matrix

## Table of Contents
- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Canonical command](#canonical-command)
- [Lane notes](#lane-notes)
- [Failure handling](#failure-handling)

## Purpose
Standardize headless multi-runner evaluation for this skill using `run_skill_evals.py`.

## Prerequisites
- `ck` and `cz` commands installed and logged in.
- `openai` CLI installed and authenticated.
- Settings files available:
  - `kimi_settings.json`
  - `zai_settings.json`

## Canonical command
```bash
CODEX_EVAL_TIMEOUT_SEC=600 \
~/.venvs/pyyaml/bin/python Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py \
  Skills/codex-automation-architect \
  --runners codex,codex-kimi,codex-zai,openai \
  --codex-kimi-command ck \
  --codex-zai-command cz \
  --codex-kimi-settings /absolute/path/kimi_settings.json \
  --codex-zai-settings /absolute/path/zai_settings.json \
  --capture-jsonl \
  --tier2-mode warn \
  --sandbox read-only
```

## Lane notes
- `codex`: primary baseline.
- `codex-kimi`: quality/alternative reasoning pass.
- `codex-zai`: edge-case and adversarial pass.
- `openai`: breadth and variance pass.

## Failure handling
- Continue with available lanes if one runner is unavailable.
- For Codex timeout (`exit 124`), reduce prompt complexity and rerun failed cases.
- For policy-blocked commit actions, switch verification to patch-only output.
