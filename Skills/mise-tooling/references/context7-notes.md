# Context7 Notes: Mise Tooling

- Retrieval path: `cli_primary`
- Auth wrapper: `op run --env-file ~/.codex/.env -- ...`
- Library id: `/jdx/mise`

## Queried commands

```bash
op run --env-file ~/.codex/.env -- ctx7 library mise "tool version management trust and config" --json
op run --env-file ~/.codex/.env -- ctx7 docs /jdx/mise "trust config files tool install use local global tasks env activation" --json
```

## Grounding highlights

- `mise use node@24` creates/updates local project config.
- `mise use --global node@24` sets global default tool version.
- `mise exec -- <cmd>` runs with selected managed runtime.
- `mise env -s bash` exports activation variables.
- Trust prompts are expected in paranoid mode and should be handled explicitly.
