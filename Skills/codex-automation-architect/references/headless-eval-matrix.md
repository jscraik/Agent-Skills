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
- `gemini` CLI installed and authenticated.
- Settings files available:
  - `kimi_settings.json`
  - `zai_settings.json`

## Canonical command
```bash
CODEX_EVAL_TIMEOUT_SEC=600 \
~/.venvs/pyyaml/bin/python Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py \
  Skills/codex-automation-architect \
  --runners codex,claude-kimi,claude-zai,gemini \
  --claude-kimi-command ck \
  --claude-zai-command cz \
  --claude-kimi-settings /absolute/path/kimi_settings.json \
  --claude-zai-settings /absolute/path/zai_settings.json \
  --capture-jsonl \
  --tier2-mode warn \
  --sandbox read-only
```

## Lane notes
- `codex`: primary baseline.
- `claude-kimi`: quality/alternative reasoning pass.
- `claude-zai`: edge-case and adversarial pass.
- `gemini`: breadth and variance pass.

## Failure handling
- Continue with available lanes if one runner is unavailable.
- For Codex timeout (`exit 124`), reduce prompt complexity and rerun failed cases.
- For policy-blocked commit actions, switch verification to patch-only output.
