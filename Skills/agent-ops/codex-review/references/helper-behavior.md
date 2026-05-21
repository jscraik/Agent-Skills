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
- `--runtime-skills-dir DIR`: opt-in path that adds a Codex runtime skills directory to the nested review sandbox before the `review` subcommand. `CODEX_REVIEW_RUNTIME_SKILLS_DIR` enables the same behavior for scripts.
- `--no-runtime-skills-dir`: disables runtime skills `--add-dir`, even when `CODEX_REVIEW_RUNTIME_SKILLS_DIR` is set.
- `--fetch-required` or `CODEX_REVIEW_FETCH_REQUIRED=1`: in branch mode, fail with `codex-review blocked: blocked_fetch` if `git fetch origin --quiet` cannot refresh refs. Without this, the helper emits `codex-review warning: degraded_existing_refs` and reviews with existing refs.

## Permission Posture

- Normal sandbox/approval prompts are the tested default in this repo state.
- Use `--full-access` or `CODEX_REVIEW_YOLO=1` only when elevated review mode is needed and approved by the active policy.
- Use `--no-yolo` or `CODEX_REVIEW_YOLO=0` to force normal prompts in scripts or automation.
- Runtime retry profile for `failed to initialize in-process app-server client`, sandbox setup, approval-policy, or data-disclosure blockers:
  - filesystem read: `$HOME/.codex`, `$HOME/.codex/skills`, `${XDG_DATA_HOME:-$HOME/.local/share}/mise`
  - filesystem write: `$HOME/.codex`, `$HOME/.codex/skills`, `${XDG_DATA_HOME:-$HOME/.local/share}/mise`, `${TMPDIR:-/tmp}`
  - network: do not request extra network permission when the workspace already has network access
  - target repo: read access to the repo under review; add write access to `<repo>/.git` only when branch ref freshness is required
- If the exact runtime retry profile still fails, stop retrying nested Codex and perform a source-backed review of the selected diff in the active agent context.

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

- `--dry-run` prints target, branch, PR URL when available, review command, test command, fetch command, and whether fetch is required.
- The printed review command should include `--add-dir <runtime-skills-dir>` only when `--runtime-skills-dir DIR` or `CODEX_REVIEW_RUNTIME_SKILLS_DIR` opts in. That keeps ordinary reviews inside the repo sandbox unless runtime skill access is explicitly needed.
- `--output FILE` or `CODEX_REVIEW_OUTPUT` saves review output.
- The helper prints `codex-review clean: no accepted/actionable findings reported` when the selected review command exits 0 and no actionable finding pattern is detected.
- If branch fetch fails, the helper prints `codex-review warning: degraded_existing_refs`, the exact fetch blocker text, and the recovery options. Set `--fetch-required` when stale refs would make the review invalid.
- If nested Codex review fails during app-server or runtime initialization, rerun this helper once from the active Codex session with the runtime retry profile above. The helper reports blockers; the outer operator grants or requests the filesystem-only retry. Do not add extra network permission in already-network-enabled workspaces; that can trigger tenant disclosure denial for local diff review.
- If nested Codex review still fails with app-server, sandbox, approval, or data-disclosure policy text and no actionable findings were produced, the helper prints `codex-review blocked: blocked_runtime` plus a fallback instruction. Use that signal to run a source-backed local review in the active agent context.
