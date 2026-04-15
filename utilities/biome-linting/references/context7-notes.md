# Context7 Notes: Biome Linting

- Retrieval path: `cli_primary`
- Auth wrapper: `op run --env-file ~/.codex/.env -- ...`
- Library id: `/biomejs/biome`

## Queried commands

```bash
op run --env-file ~/.codex/.env -- ctx7 library biome "lint rules configuration and CLI check/fix commands" --json
op run --env-file ~/.codex/.env -- ctx7 docs /biomejs/biome "CLI lint check fix unsafe suppressions config and ci usage" --json
```

## Grounding highlights

- `biome lint .` for read-only diagnostics.
- `biome lint --write .` for safe autofix.
- `biome lint --write --unsafe .` for risky autofix requiring explicit approval.
- `npx @biomejs/biome ci` for CI contract enforcement.
- `--only` and `--skip` for rule-group targeting.
