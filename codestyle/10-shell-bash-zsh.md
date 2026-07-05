# Shell Standards (Bash and Zsh)

## Table of Contents
- [Scope](#scope)
- [Execution model](#execution-model)
- [Bash](#bash)
- [Zsh](#zsh)
- [Safety and portability](#safety-and-portability)
- [Structured data and regex](#structured-data-and-regex)
- [Helpers and script shape](#helpers-and-script-shape)
- [Enforcement](#enforcement)

## Scope
- This module covers shell scripts, command snippets, and execution conventions for Bash and Zsh.

## Execution model
- Run commands with `zsh -lc` in automation-oriented workflows.
- Invoke scripts explicitly with `bash` when script contracts require Bash.
- Do not source CLI scripts unless a script explicitly documents sourcing as the intended mode.

## Bash
- Use explicit shebangs and strict mode for script files where compatible.
- Quote expansions by default and avoid unbounded globbing.
- Use `[[ ... ]]` tests and clear exit-code paths.

## Zsh
- Keep interactive helpers in Zsh-compatible syntax when targeting Zsh startup flows.
- Avoid Bash-only constructs in Zsh files unless compatibility is explicitly managed.
- Keep shell-init behavior deterministic and low-noise.

## Safety and portability
- Use `rg`, `fd`, and `jq` over slower or brittle text pipelines when possible.
- Validate required binaries and paths before destructive or multi-step operations.
- Never use destructive git commands without explicit intent and confirmation.
- Prefer Bash parameter expansion for simple prefix/suffix normalization instead
  of spawning `sed`, `awk`, or `perl`.
- Use arrays for command arguments and options; avoid string-built commands.
- Temporary files MUST be created with `mktemp` and cleaned with `trap` unless
  the file is an intentional artifact.

## Structured data and regex
- JSON MUST be parsed with `jq`, Node, Python, or another structured parser;
  shell regex MUST NOT parse JSON.
- When shell values enter a `jq` program, pass them through `--arg` for
  strings or `--argjson` for JSON values. Do not interpolate untrusted shell
  values into jq filters.
- Use `jq -e` when a filter's truthiness or existence is the validation
  result. Remember that false/null and no-output exits are non-zero with
  `-e`.
- Regex in shell scripts SHOULD be limited to simple validation predicates.
  Prefer `case`, parameter expansion, path tools, `jq`, or a typed helper
  when the pattern starts carrying parsing or ownership rules.
- If a dynamic regex is unavoidable, escape variable fragments first and cover
  the boundary with a test or fixture.

## Helpers and script shape
- Extract repeated environment setup into repo-owned helpers or wrappers instead
  of copying command prefixes across package scripts.
- Long scripts SHOULD separate argument parsing, dependency checks, data
  collection, and output formatting into named functions.
- Scripts that support both human and machine consumption SHOULD keep
  machine-readable output on stdout and diagnostics on stderr.
- Shell wrappers around typed logic SHOULD stay thin; move complex JSON,
  schema, graph, or path semantics into TypeScript or Python when it improves
  validation and testability.

## Enforcement
- Shell workflow changes MUST pass:
  - `pnpm lint`
  - `pnpm typecheck`
  - `pnpm test`
  - `pnpm audit`
  - `pnpm check`
  - `bash scripts/validate-codestyle.sh`
  - `bash scripts/verify-work.sh --fast`
- Shell snippets in docs MUST use executable contract forms (`zsh -lc ...`, `bash script.sh`) and avoid sourced-CLI patterns.
- Shell changes that touch JSON, package-manager, `uv`, or toolchain routing
  SHOULD run `bash scripts/run-uv-python.sh <command> [args...]` in addition
  to `pnpm run quality:scripts`.
- Any exception to strict-mode, quoting, or destructive-command policy requires waiver metadata with rule ID or section, reason, tracking ticket, and expiry or ADR reference.
