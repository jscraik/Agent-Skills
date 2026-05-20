# Codex Review Helper Behavior

Bundled helper:

```bash
Skills/agent-ops/codex-review/scripts/codex-review --help
```

## Modes

- `--mode auto`: dirty work first, otherwise branch review when on a non-main branch, otherwise stop with no target on a clean main checkout.
- `--mode local`: `codex review --uncommitted`.
- `--mode branch`: `codex review --base <base>`.
- `--mode commit`: `codex review --commit <commit>`.

## Refs

- `--base REF`: explicit branch review base.
- `--commit REF`: explicit commit ref; defaults to `HEAD`.

## Permission Posture

- Normal sandbox/approval prompts are the tested default in this repo state.
- Use `--full-access` or `CODEX_REVIEW_YOLO=1` only when elevated review mode is needed and approved by the active policy.
- Use `--no-yolo` or `CODEX_REVIEW_YOLO=0` to force normal prompts in scripts or automation.

## Auto Parallel Tests

The helper auto-selects this parallel test command only when all conditions are true:

```bash
PNPM_CONFIG_PM_ON_FAIL=ignore PNPM_CONFIG_VERIFY_DEPS_BEFORE_RUN=false PNPM_CONFIG_OFFLINE=true pnpm run check
```

Conditions:

- `package.json` exists.
- `pnpm-lock.yaml` exists.
- `node_modules` exists.
- `pnpm` is available.
- `package.json` has `scripts.check`.

Disable auto selection with `CODEX_REVIEW_AUTO_TESTS=0`. Use `--parallel-tests "<cmd>"` for any other stack.

## Output

- `--dry-run` prints target, branch, PR URL when available, review command, test command, and fetch command.
- `--output FILE` or `CODEX_REVIEW_OUTPUT` saves review output.
- The helper prints `codex-review clean: no accepted/actionable findings reported` when the selected review command exits 0 and no actionable finding pattern is detected.
