# Python Standards

## Table of Contents
- [Scope](#scope)
- [Runtime and environment](#runtime-and-environment)
- [Typing and API boundaries](#typing-and-api-boundaries)
- [Linting and formatting](#linting-and-formatting)
- [Testing](#testing)
- [Error handling and observability](#error-handling-and-observability)
- [Enforcement](#enforcement)

## Scope
- This module defines Python coding standards for repo scripts, utilities, and automation helpers.
- Follow these rules for `.py` files under repository control.

## Runtime and environment
- Use the Python version pinned by repo toolchain configuration.
- Keep Python invocations deterministic and scriptable (`python3 ...` from repo root when possible).
- Avoid user-specific paths and implicit global state in scripts.
- Python validation and utility scripts SHOULD run through repo-owned `uv`
  wrappers when a project has uv configured. Do not duplicate `UV_CACHE_DIR`,
  `UV_PROJECT_ENVIRONMENT`, Python version flags, or dependency-group flags in
  many package scripts.
- `UV_PROJECT_ENVIRONMENT` and `UV_CACHE_DIR` values used by repository
  scripts SHOULD resolve inside the repository or CI workspace unless an
  explicit platform contract requires another location.

## Typing and API boundaries
- Public functions and module entrypoints MUST have explicit type hints.
- Prefer concrete types and `typing` primitives over untyped dictionaries at boundaries.
- Validate external input payloads before use and narrow types early.
- For JSON/YAML/TOML or subprocess boundaries, prefer `dataclass`,
  `TypedDict`, Pydantic models, or schema validators over open-ended
  `dict[str, object]` plumbing after the boundary has been parsed.
- `subprocess.run` calls SHOULD use argument lists, `check=False` or
  well-scoped exception handling, explicit text/encoding expectations, and
  typed result objects when callers inspect exit status or output.

## Linting and formatting
- Ruff is the primary Python linter and MUST pass for changed Python paths.
- Keep style and import ordering consistent with repo lint configuration.
- Use Pyright for static type checks where configured; failing type checks MUST block merge.
- Waivers or suppressions MUST include reason, tracking reference, and expiry when temporary.

## Testing
- Use `pytest` for Python unit and behavior checks where Python logic is non-trivial.
- Keep tests deterministic and avoid network or clock coupling unless explicitly mocked.
- Co-locate tests near Python modules when practical.

## Error handling and observability
- Do not swallow exceptions.
- Add actionable context to raised errors and logs.
- When scripts produce machine-consumed output, keep message structure stable.

## Enforcement
- Python changes MUST pass the repository contract checks:
  - `pnpm lint`
  - `pnpm typecheck`
  - `pnpm test`
  - `bash scripts/verify-work.sh --fast`
- In this repository, Python artifact/type checks are routed through
  `bash scripts/check-python-types.sh`; keep package scripts on that wrapper
  instead of recreating `uv run --python ... --group ...` command lines.
- Python-focused checks SHOULD be run when relevant tooling is present in the touched project:
  - `ruff check <changed-python-paths>`
  - `pyright <changed-python-paths>`
  - `pytest <affected-tests>`
- Validation records MUST include exact commands and outcomes:
  - `Command: <exact command> -> pass|fail|blocked (<reason>)`
