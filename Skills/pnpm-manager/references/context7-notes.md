# Context7 Notes: PNPM Manager

- Retrieval path: `cli_primary`
- Auth wrapper: `op run --env-file ~/.codex/.env -- ...`
- Library id: `/websites/pnpm_io`

## Queried commands

```bash
op run --env-file ~/.codex/.env -- ctx7 library pnpm "workspace management filters recursive commands" --json
op run --env-file ~/.codex/.env -- ctx7 docs /websites/pnpm_io "pnpm workspace filtering recursive commands install update exec list" --json
op run --env-file ~/.codex/.env -- ctx7 docs /websites/pnpm_io "filter selector workspace recursive run exec install examples" --json
op run --env-file ~/.codex/.env -- ctx7 docs /websites/pnpm_io "pnpm filter include dependents dependencies changed since commit" --json
```

## Grounding highlights

- `pnpm --filter <package_selector> <command>` for scope targeting.
- `pnpm -r` runs commands recursively across workspaces.
- Change-based selectors like `...[<base-ref>]` target impacted packages.
- Combined selectors like `{packages/**}[<base-ref>]` allow path + change constraints.
