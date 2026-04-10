# Context7 CLI + Skill Wizard Reference

This file is the command source of truth for Context7 CLI asks in this skill.

## Secure execution wrapper

For authenticated or generation flows, prefer this wrapper:

```bash
op run --env-file ~/.codex/.env -- ctx7 <command>
```

Examples:

```bash
op run --env-file ~/.codex/.env -- ctx7 whoami
op run --env-file ~/.codex/.env -- ctx7 skills generate
```

## Command families

```bash
# docs retrieval
ctx7 library <name> <query>
ctx7 docs <libraryId> <query>

# skills management
ctx7 skills <subcommand> [options]

# setup and auth
ctx7 setup [options]
ctx7 login [--no-browser]
ctx7 whoami
ctx7 logout
```

### Skills subcommands

Supported subcommands in this lane:
- `install`
- `search`
- `list`
- `remove`
- `info`
- `suggest`
- `generate`

## Install target flags

Use only these target flags when relevant:
- `--claude`
- `--cursor`
- `--universal`
- `--antigravity`
- `--global`
- `--all` (install all, or generate for all detected IDE targets)

## Setup mode flags

Use setup mode intentionally:
- `--mcp`
- `--cli`
- `--project`
- `--yes`
- `--api-key`
- `--oauth` (MCP mode only)

Agent targets for setup:
- `--claude`
- `--cursor`
- `--opencode`
- `--universal`
- `--antigravity`

## Docs workflow contract

Two-step docs retrieval unless user already provided a valid library ID.

1. Resolve with `ctx7 library`
2. Query with `ctx7 docs`

If the user already provides `/org/project` or `/org/project/version`, skip resolve and query directly.

Attempt caps per user question:
- max 3 `ctx7 library` attempts
- max 3 `ctx7 docs` attempts

Repository format for installs is always `/owner/repo`.

## Common command patterns

```bash
# docs lookup (CLI primary)
op run --env-file ~/.codex/.env -- ctx7 library react "useEffect cleanup with async"
op run --env-file ~/.codex/.env -- ctx7 docs /facebook/react "useEffect cleanup with async" --json

# generate a custom skill interactively
op run --env-file ~/.codex/.env -- ctx7 skills generate

# generate for all detected IDE targets
op run --env-file ~/.codex/.env -- ctx7 skills generate --all

# install all skills from a repository
op run --env-file ~/.codex/.env -- ctx7 skills install /owner/repo --all

# install for specific targets
op run --env-file ~/.codex/.env -- ctx7 skills install /owner/repo --cursor --claude

# list installed skills by target
op run --env-file ~/.codex/.env -- ctx7 skills list --cursor
op run --env-file ~/.codex/.env -- ctx7 skills list --claude
op run --env-file ~/.codex/.env -- ctx7 skills list --universal

# setup and auth
op run --env-file ~/.codex/.env -- ctx7 setup --mcp --claude
op run --env-file ~/.codex/.env -- ctx7 setup --cli --universal
op run --env-file ~/.codex/.env -- ctx7 login
op run --env-file ~/.codex/.env -- ctx7 whoami
```

## Generate flow checklist

When users ask about "Skill Wizard" or `ctx7 skills generate`, ensure guidance covers:
1. Describe expertise target.
2. Select Context7 documentation sources.
3. Answer follow-up scope/constraint questions.
4. Review generated skill content before install.
5. Install to selected target directories.
6. Verify install via `ctx7 skills list`.
7. Restart the agent if installed skills do not appear immediately.

## Fallback rules

- Docs retrieval fallback order: CLI primary -> MCP backup -> API helper backup.
- Skill install/generate/setup flows are CLI-only; do not substitute MCP for those actions.
- If quota is exceeded, state it explicitly and recommend `ctx7 login`.

## Verification commands

```bash
# verify generated/installed skills
op run --env-file ~/.codex/.env -- ctx7 skills list
op run --env-file ~/.codex/.env -- ctx7 skills list --cursor
op run --env-file ~/.codex/.env -- ctx7 skills list --claude

# verify auth state
op run --env-file ~/.codex/.env -- ctx7 whoami
```

## Sources
- Upstash docs (skills): https://www.mintlify.com/upstash/context7/cli/skills
- Upstash docs (setup): https://www.mintlify.com/upstash/context7/cli/setup
- Upstash docs (library/docs): https://www.mintlify.com/upstash/context7/cli/library
- Upstash announcement: https://upstash.com/blog/context7-skill-wizard
- Upstash skill refs at pinned commit: https://github.com/upstash/context7/tree/00833f92623032dd643974048f9817dd0f1694cc/skills
