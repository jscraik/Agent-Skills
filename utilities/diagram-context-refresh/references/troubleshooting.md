# Diagram Context Refresh Troubleshooting

## Table of Contents

- [Quick reference fixes](#quick-reference-fixes)
- [Preflight fails](#preflight-fails)
- [Refresh script missing](#refresh-script-missing)
- [Global `diagram` command not found](#global-diagram-command-not-found)
- [Mise installed but package not detected](#mise-installed-but-package-not-detected)
- [Hook install fails in `silent-on-open` mode](#hook-install-fails-in-silent-on-open-mode)
- [CI workflow missing in `ci-only` mode](#ci-workflow-missing-in-ci-only-mode)
- [Generated artifacts missing after refresh](#generated-artifacts-missing-after-refresh)

## Quick reference fixes

| Symptom | One-line fix/check |
| --- | --- |
| Preflight fails | `bash "$SKILL_DIR/scripts/preflight.sh" --repo-root "$REPO_ROOT" --mode "$MODE"` |
| Refresh script missing | `test -f "$REPO_ROOT/scripts/refresh-diagram-context.sh"` |
| Global CLI missing | `command -v diagram >/dev/null && diagram --version` |
| Mise package missing | `command -v mise >/dev/null && mise current \| rg "@brainwav/diagram"` |
| Hook install issue | `bash "$REPO_ROOT/scripts/install-repo-open-hook.sh"` |
| CI-only workflow missing | `test -f "$REPO_ROOT/.github/workflows/refresh-diagram-context.yml"` |
| Outputs missing | `test -s "$REPO_ROOT/AI/context/diagram-context.md" && jq -e . "$REPO_ROOT/AI/context/diagram-context.meta.json" >/dev/null && ls "$REPO_ROOT"/AI/diagrams/*.mmd >/dev/null` |

## Preflight fails

1. Re-run preflight with explicit inputs:

   ```bash
   bash "$SKILL_DIR/scripts/preflight.sh" --repo-root "$REPO_ROOT" --mode "$MODE"
   ```

2. Fix the first reported `[FAIL]` item before retrying.
3. Do not continue to refresh steps while preflight is failing.

## Refresh script missing

Symptom: preflight reports missing `scripts/refresh-diagram-context.sh`.

Checks:

```bash
test -f "$REPO_ROOT/scripts/refresh-diagram-context.sh"
```

Fix:
- Point `REPO_ROOT` at the correct repository.
- Restore the script if it was deleted/moved.

## Global `diagram` command not found

Symptom: neither `src/diagram.js` nor global `diagram` is detected.

Checks:

```bash
test -f "$REPO_ROOT/src/diagram.js"
command -v diagram
```

Fix:
- Prefer repo-local `src/diagram.js` when present.
- Otherwise install/restore global `diagram` and verify:

```bash
command -v diagram >/dev/null && diagram --version
```

## Mise installed but package not detected

Symptom: warning that `@brainwav/diagram` is not reported.

Checks:

```bash
command -v mise
mise current | rg "@brainwav/diagram"
```

Fix:
- If global install is required, ensure `@brainwav/diagram` is installed via mise.
- If repo-local `src/diagram.js` exists, this warning is non-blocking.

## Hook install fails in `silent-on-open` mode

Symptom: `scripts/install-repo-open-hook.sh` missing or failing.

Checks:

```bash
test -f "$REPO_ROOT/scripts/install-repo-open-hook.sh"
bash "$REPO_ROOT/scripts/install-repo-open-hook.sh"
```

Fix:
- Ensure hook script exists and is executable.
- Fall back to `manual` mode if hook installation is intentionally disabled.

## CI workflow missing in `ci-only` mode

Symptom: preflight fails due to missing workflow.

Checks:

```bash
test -f "$REPO_ROOT/.github/workflows/refresh-diagram-context.yml"
```

Fix:
- Add or restore `.github/workflows/refresh-diagram-context.yml`.
- Do not use `ci-only` mode without the workflow.

## Generated artifacts missing after refresh

Checks:

```bash
test -s "$REPO_ROOT/AI/context/diagram-context.md"
jq -e . "$REPO_ROOT/AI/context/diagram-context.meta.json" >/dev/null
ls "$REPO_ROOT"/AI/diagrams/*.mmd >/dev/null
```

Fix:
- Re-run preflight and refresh in `manual` mode.
- Inspect the first failing command output and stop there (avoid cascading retries).
