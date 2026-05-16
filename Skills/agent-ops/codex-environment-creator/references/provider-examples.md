# Environment Provider Examples

Use these examples when editing CODEX_HOME environments.toml or a repo-local
environment file. Pick one provider shape per environment; do not define both
url and program for the same provider.

## Local Default

```toml
default = "local-dev"

[[environments]]
id = "local-dev"
program = "bash"
args = ["-lc", "codex exec-server --listen stdio"]
cwd = "/tmp"
```

Use an empty setup script when the local machine already has the required
tooling and actions are the useful surface.

## URL Provider

```toml
default = "devcontainer"

[[environments]]
id = "devcontainer"
url = "wss://example.invalid/codex/environment"
connect_timeout_sec = 12.0
initialize_timeout_sec = 34.0
```

Use URL providers only when the repo or team owns the remote environment
definition and the URL is stable enough for unattended runs.

## Program Provider

```toml
default = "generated"

[[environments]]
id = "generated"
program = "/absolute/path/to/environment-provider"
args = ["--workspace", "/absolute/path/to/repo"]
cwd = "/absolute/path/to/repo"

[environments.env]
CODEX_ENVIRONMENT_MODE = "generated"
```

Program providers should use absolute executable paths, explicit arguments, and
a deterministic working directory. Validate the program separately before
making it the default.
