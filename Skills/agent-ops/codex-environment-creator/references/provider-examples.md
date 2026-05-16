# Environment Provider Examples

Use these examples when editing CODEX_HOME environments.toml or a repo-local
environment file. Pick one provider shape per environment; do not define both
url and program for the same provider.

## Local Default

~~~toml
[environments.default]
provider = "local"

[environments.default.setup]
script = ""
~~~

Use an empty setup script when the local machine already has the required
tooling and actions are the useful surface.

## URL Provider

~~~toml
[environments.devcontainer]
provider = "url"
url = "https://example.invalid/codex/environment"

[environments.devcontainer.setup]
script = "bash scripts/setup-codex.sh"
~~~

Use URL providers only when the repo or team owns the remote environment
definition and the URL is stable enough for unattended runs.

## Program Provider

~~~toml
[environments.generated]
provider = "program"
program = "/absolute/path/to/environment-provider"
args = ["--workspace", "/absolute/path/to/repo"]
cwd = "/absolute/path/to/repo"

[environments.generated.env]
CODEX_ENVIRONMENT_MODE = "generated"

[environments.generated.setup]
script = "uv sync --frozen"
~~~

Program providers should use absolute executable paths, explicit arguments, and
a deterministic working directory. Validate the program separately before
making it the default.
