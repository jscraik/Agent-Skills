# Context7 Notes: Vale

- Retrieval path: `cli_primary`
- Auth wrapper: `op run --env-file $CODEX_ENV_FILE -- ...` (replace `$CODEX_ENV_FILE` with your env file path)
- Library ids: `/errata-ai/vale`, `/websites/vale_sh`
- Freshness check: `/errata-ai/vale` lastUpdateDate `2026-03-14T22:19:37.568Z`

## Queried commands

```bash
op run --env-file $CODEX_ENV_FILE -- ctx7 library vale "installation setup GitHub Actions style packages minimumAlertLevel vale.ini" --json
op run --env-file $CODEX_ENV_FILE -- ctx7 docs /errata-ai/vale "installation .vale.ini config StylesPath Packages MinAlertLevel vale sync vale ls-config CLI options" --json
op run --env-file $CODEX_ENV_FILE -- ctx7 docs /websites/vale_sh "best practices CI GitHub Actions pre-commit style packages vale sync output checks" --json
op run --env-file $CODEX_ENV_FILE -- ctx7 docs /websites/vale_sh "installation macOS linux windows package managers brew winget apt latest release check version" --json
op run --env-file $CODEX_ENV_FILE -- ctx7 docs /errata-ai/vale "github actions integration pre-commit vale sync minAlertLevel" --json
```

## Skill Wizard note

```bash
op run --env-file $CODEX_ENV_FILE -- ctx7 skills generate --output /tmp/ctx7-vale-skill --universal
```

Result: blocked by OAuth login prompt (interactive browser flow required).

## Grounding highlights

- `.vale.ini` is the central config contract with `StylesPath`, `MinAlertLevel`, and scoped style bindings.
- External style packages use `Packages = ...` and require `vale sync`.
- Use `vale ls-config` and `vale ls-dirs` to debug config and asset resolution.
- CI and automation lanes commonly use `--output=line` or `--output=JSON`.
- Pre-commit best practice is running a `sync` hook before linting hook execution.