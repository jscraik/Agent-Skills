---
source: https://docs.coderabbit.ai/tools/golangci-lint
---

# golangci-lint

## Files
golangci-lint will run on files with the following extensions:

- `.go`

- `go.mod`

## Configuration
golangci-lint supports the following config files:

- User-defined config file set at `reviews.tools.golangci-lint.config_file` in your project’s `.coderabbit.yaml` file or setting the “Reviews → Tools → golangci-lint → Config File” field in CodeRabbit’s settings page.

- `.golangci.yml`

- `.golangci.yaml`

- `.golangci.toml`

- `.golangci.json`

## What CodeRabbit runs
We run golangci-lint in a sandbox with `--out-format=json` and per-module scoping. No plugins or external binaries are loaded.
## Security policy and restrictions

- Plugins are disallowed. If plugins are referenced in config, we skip.

- Advanced or unsafe options cause a skip: top-level plugins, non-empty `linters-settings` that imply external executors, or preset bundles that expand to plugins.

- Config version is validated; an “unsafe” evaluation returns version `0` and we fail-closed.

- Blocked configurations include:

- Any `plugins` entries (in any form)

- Non-empty `linters-settings` values that imply external executors

- Presets that expand to plugins

## When we skip golangci-lint
CodeRabbit will skip running golangci-lint when:

- The config references plugins (in any form).

- The config contains advanced or unsafe options we can’t guarantee are safe.

- The config cannot be parsed confidently (YAML/JSON/TOML errors).

## Links

- golangci-lint Configuration
