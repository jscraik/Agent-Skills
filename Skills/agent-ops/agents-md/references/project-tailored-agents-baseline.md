# Project-tailored AGENTS baseline

## Table of Contents
- [When to use this reference](#when-to-use-this-reference)
- [Tailoring rules](#tailoring-rules)
- [Repository rules](#repository-rules)
- [Stack detection](#stack-detection)
- [Required tooling](#required-tooling)
- [Required repo paths](#required-repo-paths)
- [Cross-agent instruction files](#cross-agent-instruction-files)
- [Local Memory policy](#local-memory-policy)
- [Project Brain policy](#project-brain-policy)
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
- Run `./Infrastructure/scripts/codex-preflight/codex-preflight.sh --stack auto --mode required` before substantive changes when that script and flag shape exist in the repo.
- Recognize the current flag surface:
  - `--stack <auto|repo|js|py|rust>`
  - `--mode <off|optional|required>`
  - `--repo-fragment <text>`
  - `--bins <csv>`
  - `--paths <csv>`
- If required-mode preflight fails, stop and report the blocker instead of continuing with speculative edits.
- Work only inside the active git repo root.
- Keep changes minimal and local unless the task explicitly calls for a broader refactor.
- Read `docs/` and `Docs/plans/` when they are relevant and present.
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
- `Docs/plans/`
- `instructions/project-brain.md` only when the repo actually documents Project Brain as part of the operating surface
- a documented architecture-diagram directory such as `.diagram/` or `.diagrams/` only when that exact path is a real repo standard
- `.harness/memory/LEARNINGS.md` only when the repo explicitly adopts the harness-memory convention for repo-specific learnings

Language-specific modes may also require the root manifest:
- JS or TS: `package.json`
- Python: `pyproject.toml`
- Rust: `Cargo.toml`

Do not require paths just because they appear in another project template.
Do not require `.harness/memory/LEARNINGS.md` unless the repo has explicitly standardized that harness-memory layout.
Do not silently rename or normalize architecture-diagram paths between `.diagram/`, `.diagrams/`, `AI/diagrams/`, or other variants.
When a documented architecture-diagram directory exists, treat it as high-value project context for faster repo understanding, but still verify the exact path before making it mandatory guidance.

## Cross-agent instruction files

Use this section when the repo maintains parallel instruction files such as `AGENTS.md`, `AGENTS.md`, and `AGENTS.md`.

- Keep durable repo-operating rules semantically aligned across all in-scope instruction files, but preserve each tool's official instruction-file behavior and any repo-specific filename configuration.
- For `AGENTS.md`, follow Anthropic's current guidance: keep instructions concise, specific, and verifiable, and prefer strengthening an existing rule over appending a second weaker version.
- For `AGENTS.md`, honor OpenAI CLI's current context-file configuration model. If the repo config sets `context.fileName`, use that verified filename behavior instead of assuming an unconfigured default.
- Prefer the same section names across agent files when the guidance is truly shared, so operators can find the rule quickly regardless of agent.
- For reusable Python runtime policy requests, mirror `## Python Environment and Dependency Management` across `AGENTS.md`, `AGENTS.md`, and `AGENTS.md` when those files are in scope and the section is missing.
- For that shared Python section, keep these defaults aligned unless repo evidence requires overrides: `uv`-only dependency/environment operations, Python `3.12` default for new environments, dependency declaration by `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, or `requirements.lock`, local `.venv` preference, activation before direct Python execution, and global fallback via `source ~/personal/bin/activate` only when no dependency files exist.
- For reusable preflight-enforcement requests, mirror both the mandatory workflow snippet and `## Preflight Enforcement (REQUIRED)` across in-scope instruction files when missing, using only repo-verified commands and supported flags.
- For coding-standards hardening requests, mirror `## Quality Checks` across `AGENTS.md`, `AGENTS.md`, and `AGENTS.md` when missing (or strengthen in place), and require repo-native formatter, lint, typecheck, and test commands with explicit pass-state confirmation before completion.
- For TypeScript validation guidance, use `## Quality Checks` across `AGENTS.md`, `AGENTS.md`, and `AGENTS.md`. If the section is missing, create it.
- In npm-based repos, make the rule explicit and verifiable: run `npm run lint` and `npm run test` after TypeScript changes, and confirm both pass before marking work complete. In non-npm repos, substitute the repo-native lint and test commands instead of hard-coding `npm`.
- For CI guidance, use `## CI/CD Workflow` when present or create it when missing. Require confirmation of the final authoritative pipeline status before ending CI/CD work. GitHub's protected-branch model relies on required status checks succeeding before merge, so avoid treating a local fix or partial rerun as completion.
- For pull-request coordination, use `## GitHub Workflow` or `## PR Management`. For multi-repo PR work, check merge-conflict state up front and flag blocked PRs early. GitHub blocks merge completion when conflicts remain unresolved, so the guidance should surface that blocker immediately rather than late in the session.
- If a weaker version of one of these rules already exists, strengthen it in place instead of duplicating it elsewhere in the file.

## Local Memory policy

Include this section only when the repo or user explicitly wants Local Memory required by default.

The current script supports Local Memory modes `off`, `optional`, and `required`. Document that behavior when it is part of the repo contract.

If Local Memory is enabled, preserve these checks:
- `local-memory` is installed.
- `jq` is installed for parsing JSON during Local Memory verification.
- `curl` is installed for REST endpoint checks, including `REST health succeeds`.
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

## Project Brain policy

Include this section only when the repo or user explicitly wants Project Brain in the AGENTS operating surface.

When Project Brain is in scope:
- Verify `instructions/project-brain.md` exists before adding it to AGENTS routing or documentation maps.
- Keep the root AGENTS Project Brain section concise and action-oriented, and route procedural depth to `instructions/project-brain.md`.
- If the workflow references a bootstrap helper (for example `Infrastructure/scripts/init-project-brain.sh`), verify that script path exists before insertion.
- If Local Memory is also part of the repo contract, preserve the relationship explicitly (for example "use both together") rather than presenting the two systems as independent or conflicting flows.
- Do not invent `.harness/` requirements; only include them when the repo has actually standardized those paths.

## Startup workflow

Keep the startup sequence short and operator-facing:
1. Read `AGENTS.md` and task-relevant docs.
2. Run the verified preflight command in required mode when the repo standard says so.
3. Summarize repo structure and blockers before editing.
4. Make the smallest change that satisfies the task.
5. Run the narrowest validation that proves the change works.

## Supplemental context

Optional extra context files can be mentioned when they exist and fit the repo's workflow:
- `~/dev/configs/codex/instructions/Learning.md`
- `~/dev/configs/codex/instructions/Learnings.md`
- legacy repo notes like `FORJAMIE.md`, but only when the file still exists and the repo intentionally uses it

Treat organization `instructions/Learning.md` or `instructions/Learnings.md` as supplemental context, not a replacement for repo-local instructions.
Treat `.harness/memory/LEARNINGS.md` separately as a repo-operating path only in repos that adopt the harness-memory convention.

If `FORJAMIE.md` appears in old docs but is gone from the repo, treat those references as stale cleanup work rather than as active instruction routing.

## Validation checklist

- Verify the preflight command exists and supports the documented flags.
- Verify any documented `--repo-fragment`, `--bins`, or `--paths` usage really matches the script.
- Verify any stack-detection rules match the repo's observed manifests.
- Verify required tooling matches the actual repo stack.
- Verify required repo paths exist before naming them as mandatory.
- Verify required paths stay inside the repo root after path resolution.
- Verify any architecture-diagram path matches the repo's documented location exactly, and do not silently swap `.diagram/` for `.diagrams/` or another variant.
- Verify `.harness/memory/LEARNINGS.md` is required only when the repo has explicitly adopted the harness-memory convention.
- Verify Project Brain guidance is included only when the repo standardizes it, and that `instructions/project-brain.md` path references resolve.
- Verify any Project Brain bootstrap helper path (for example `Infrastructure/scripts/init-project-brain.sh`) exists before documenting it.
- Verify `Quality Checks` uses repo-native commands, and keep explicit `npm run lint` / `npm run test` wording only when the repo is actually npm-based.
- Verify CI guidance points to the authoritative provider status surface for the repo, and do not imply CI is complete before the final pipeline state is known.
- Verify PR guidance reflects real merge-conflict behavior for the host platform and flags blocked PRs early rather than after review or merge prep.
- Verify Local Memory is truly a repo requirement before making it mandatory.
- Verify Local Memory mode semantics match the script (`off`, `optional`, `required`).
- Verify supplemental context paths exist before referencing them.
- Verify organization `Learning.md` / `Learnings.md` references stay supplemental and are not presented as required repo-local instruction files.
- Verify any `FORJAMIE.md` mention points to a real file or an explicit fallback-filename policy before keeping it.
