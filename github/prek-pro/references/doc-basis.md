# Prek Doc Basis (Context7)

## Resolved library

- Context7 library id: `/j178/prek`
- Retrieval mode: MCP fallback path used in-session (`mcp__context7__resolve_library_id`, `mcp__context7__query_docs`)

## Retrieved guidance used

- `prek install` command shape and options (`--hook-type`, `--overwrite`, `--prepare-hooks`)
- `prek run` command patterns:
  - default staged run
  - `--all-files`
  - hook-id targeting
  - stage targeting (`--stage pre-push`)
  - ref-range execution (`--from-ref`, `--to-ref`)
- `prek validate-config` and `prek validate-manifest`
- cache operations:
  - `prek cache dir`
  - `prek cache size --human`
  - `prek cache gc [--dry-run]`
  - `prek cache clean`
- config behavior:
  - `default_install_hook_types` determines installed shims
  - hook `stages` determines eligibility at runtime
  - local hook examples (`repo = "local"`, `id`, `name`, `language`, `entry`)

## Notes for maintainers

- Treat the retrieved command set as drift-prone; re-query Context7 before changing command/flag guidance.
- Keep command examples in `SKILL.md` minimal and operational; put additional depth here.
