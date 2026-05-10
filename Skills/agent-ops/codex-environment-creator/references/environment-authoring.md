# Codex Environment Authoring Notes

## Canonical Path

Default to `.codex/environments/environment.toml` for repo-local project setup and actions.

Do not confuse this file with `$CODEX_HOME/environments.toml`, which recent Codex runtime code uses to configure execution environment providers and default environment selection.

Common drift paths to triage before editing:

- `.codex/environmental.toml`
- `.codex/environmentals/environmental.toml`
- `.codex/environmentals/enviromental.toml`
- docs or scripts that mention `environmental.toml` without a live file

If multiple files exist, identify which one is consumed by the current Codex runtime, preserve user changes, and migrate only after reporting the conflict.

## Current Minimal Shape

Live Codex source and `codex-repo` evidence currently show this project file shape:

```toml
version = 1
name = "project-name"

[setup]
script = ""

[[actions]]
name = "Run"
icon = "run"
command = "repo-owned command"
```

Treat this as a current evidence point, not a permanent schema guarantee. Re-check Codex docs or source before adding new keys.

## Runtime Provider Shape

Recent `~/dev/codex` updates added `$CODEX_HOME/environments.toml` as a runtime provider file. Use it only when the request is about Codex runtime environment selection, remote exec servers, or disabling default shell/filesystem access.

Observed current shape:

```toml
default = "ssh-dev"

[[environments]]
id = "devbox"
url = "ws://127.0.0.1:4512"
connect_timeout_sec = 12.0
initialize_timeout_sec = 34.0

[[environments]]
id = "ssh-dev"
program = "ssh"
args = ["dev", "codex exec-server --listen stdio"]
cwd = "/tmp"

[environments.env]
CODEX_LOG = "debug"
```

Current rules from the live fork:

- If `$CODEX_HOME/environments.toml` is missing, Codex falls back to legacy `CODEX_EXEC_SERVER_URL` behavior.
- `default` omitted selects `local`; `default = "none"` disables the default model-facing environment.
- `local` and `none` are reserved ids for configured environments.
- Ids must be unique, not empty, no surrounding whitespace, at most 64 characters, and contain only ASCII letters, numbers, `-`, or `_`.
- A remote entry must set exactly one of `url` or `program`.
- `url` must use `ws://` or `wss://`.
- `args`, `env`, and `cwd` require `program`.
- Relative `cwd` is resolved from the CODEX_HOME config directory when loaded from disk.
- `connect_timeout_sec` applies only to URL transports; `initialize_timeout_sec` applies to URL and stdio transports.
- Unknown fields are rejected.

## Authoring Procedure

1. Read target repo instructions and ownership boundaries.
2. Locate existing environment files with `find . -path "*/.codex/*" -maxdepth 4` or an equivalent focused search.
3. Read package and tooling files such as `package.json`, `pnpm-lock.yaml`, `pyproject.toml`, `uv.lock`, `Cargo.toml`, `go.mod`, `Makefile`, `.mise.toml`, and project scripts.
4. Choose setup commands that are repeatable in fresh containers and aligned with lockfiles.
5. Keep `[setup].script` narrowly focused on installing or preparing dependencies. Put validation and app launch commands in `[[actions]]`.
6. Prefer shell-safe commands with explicit working assumptions. Avoid secret interpolation in TOML.
7. Parse the TOML after edits and run the repo's smallest relevant environment or preflight check.

## Triage Checklist

- Canonical path exists or a drift path needs migration.
- Request is classified as project bootstrap file or CODEX_HOME runtime provider file.
- TOML parses and uses expected scalar, table, and array-of-table shapes.
- `version` is an integer and `name` is a stable project identifier.
- `[setup].script` is present, even when intentionally empty.
- Every `[[actions]]` entry has `name`, `icon`, and `command`.
- Commands use repo wrappers and lockfile-aware package managers.
- Setup does not publish, delete data, reset caches, or mutate secrets.
- Network-dependent installs are expected, documented, and minimal.
- Validation commands and known blockers are recorded.

## Cache Notes

OpenAI Codex cloud environments can cache setup output. Current docs state that setup runs before a cache is stored, an optional maintenance script can run when a cached container resumes, and cache invalidation can happen when setup scripts, maintenance scripts, environment variables, or secrets change.

When changing setup behavior, report whether a cache reset may be needed. Do not reset cache or modify secrets unless the user explicitly asks.

## Safe Output Shape

For triage or update work, report:

```yaml
schema_version: 1
mode: create|triage|update
target_path: .codex/environments/environment.toml
path_decision: canonical|migrated|blocked
changes:
  - summary
validation:
  - command: "<exact command>"
    outcome: pass|fail|blocked
    note: "<short evidence>"
risks:
  - "<cache, setup, command, or ownership risk>"
```
