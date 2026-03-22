# Project-tailored AGENTS baseline

## Table of Contents
- [When to use this reference](#when-to-use-this-reference)
- [Tailoring rules](#tailoring-rules)
- [Repository rules](#repository-rules)
- [Stack detection](#stack-detection)
- [Required tooling](#required-tooling)
- [Required repo paths](#required-repo-paths)
- [Local Memory policy](#local-memory-policy)
- [Startup workflow](#startup-workflow)
- [Supplemental context](#supplemental-context)
- [Validation checklist](#validation-checklist)

## When to use this reference

Use this when a user wants AGENTS guidance that carries a reusable repo-operating baseline, but still needs to be adapted to the actual project instead of pasted verbatim.

Source baseline in this revision:
- the current `codex-preflight.sh` script version verified during this update

## Tailoring rules

- Verify the repo root before inserting project rules.
- Prefer the repo's own preflight script and flags when they exist.
- Match the documented flag surface of the real script instead of paraphrasing from memory.
- Use `not observed` or omit a section instead of inventing commands, manifests, or directories.
- Keep root `AGENTS.md` high signal. Move detailed procedures into linked docs when they would bloat the root file.
- Preserve the user's requested policy strength. If they say Local Memory or preflight is required, keep the stop-on-failure behavior. If not, avoid silently promoting optional checks into mandatory policy.

## Repository rules

Use this section when the repo needs operator rules up front.

Preserve these points only after verification:
- Run `./scripts/codex-preflight.sh --stack auto --mode required` before substantive changes when that script and flag shape exist in the repo.
- Recognize the current flag surface:
  - `--stack <auto|repo|js|py|rust>`
  - `--mode <off|optional|required>`
  - `--repo-fragment <text>`
  - `--bins <csv>`
  - `--paths <csv>`
- If required-mode preflight fails, stop and report the blocker instead of continuing with speculative edits.
- Work only inside the active git repo root.
- Keep changes minimal and local unless the task explicitly calls for a broader refactor.
- Read `docs/` and `docs/plans/` when they are relevant and present.
- Preserve repo-root safety checks from the script when they matter:
  - repo must be a git repo,
  - script workspace must match the active repo root,
  - `--repo-fragment` can enforce a required repo-name fragment,
  - required paths must resolve inside the repo root and must not escape it through symlinks or path tricks.

If the repo uses a different preflight entrypoint, substitute the verified command and say so.

## Stack detection

Document stack detection from real repo evidence:
- JavaScript or TypeScript: `package.json`
- Python: `pyproject.toml`
- Rust: `Cargo.toml`
- Otherwise: generic repo mode

Only mention override flags like `--stack js|py|rust|repo` when the repo's preflight tooling or docs actually support them.

## Required tooling

Start from the common baseline only when the repo depends on it:
- `git`
- `bash`
- `sed`
- `rg`
- `fd`
- `jq`
- `curl`
- `python3`

Add language-specific tools only when the repo stack requires them:
- JS or TS: `node`, `npm`
- Rust: `cargo`

If the repo standardizes a different package manager or runtime toolchain, replace the defaults with the repo-native tools.

## Required repo paths

List only required paths that are real repo standards.

Common examples:
- `AGENTS.md`
- `docs/`
- `docs/plans/`

Language-specific modes may also require the root manifest:
- JS or TS: `package.json`
- Python: `pyproject.toml`
- Rust: `Cargo.toml`

Do not require paths just because they appear in another project template.

## Local Memory policy

Include this section only when the repo or user explicitly wants Local Memory required by default.

The current script supports Local Memory modes `off`, `optional`, and `required`. Document that behavior when it is part of the repo contract.

If Local Memory is enabled, preserve these checks:
- `local-memory` is installed.
- `jq` and `curl` are installed because the script uses both for Local Memory verification.
- The daemon is running.
- `local-memory status --json` returns a usable JSON payload.
- `rest_api_port` resolves to a numeric value.
- Config exists at `LOCAL_MEMORY_CONFIG_PATH` or `~/.local-memory/config.yaml`.
- Config includes `host: 127.0.0.1`.
- Config includes `auto_port: false`.
- REST health succeeds.
- Smoke cycle succeeds: two `observe` calls, one `relate`, and one `search`.
- Malformed REST payloads are rejected.
- Duplicate observe behavior is captured as a snapshot rather than silently ignored.
- Recent daemon log output is checked for migration-status signals when the log exists.

If Local Memory fails in required mode, stop. In optional mode, warn and continue. In off mode, skip Local Memory checks.

## Startup workflow

Keep the startup sequence short and operator-facing:
1. Read `AGENTS.md` and task-relevant docs.
2. Run the verified preflight command in required mode when the repo standard says so.
3. Summarize repo structure and blockers before editing.
4. Make the smallest change that satisfies the task.
5. Run the narrowest validation that proves the change works.

## Supplemental context

Optional extra context files can be mentioned when they exist and fit the repo's workflow:
- `~/dev/config/codex/instructions/Learning.md`
- `~/dev/config/codex/instructions/Learnings.md`
- legacy repo notes like `FORJAMIE.md`, but only when the file still exists and the repo intentionally uses it

Treat them as supplemental context, not a replacement for repo-local instructions.

If `FORJAMIE.md` appears in old docs but is gone from the repo, treat those references as stale cleanup work rather than as active instruction routing.

## Validation checklist

- Verify the preflight command exists and supports the documented flags.
- Verify any documented `--repo-fragment`, `--bins`, or `--paths` usage really matches the script.
- Verify any stack-detection rules match the repo's observed manifests.
- Verify required tooling matches the actual repo stack.
- Verify required repo paths exist before naming them as mandatory.
- Verify required paths stay inside the repo root after path resolution.
- Verify Local Memory is truly a repo requirement before making it mandatory.
- Verify Local Memory mode semantics match the script (`off`, `optional`, `required`).
- Verify supplemental context paths exist before referencing them.
- Verify any `FORJAMIE.md` mention points to a real file or an explicit fallback-filename policy before keeping it.
