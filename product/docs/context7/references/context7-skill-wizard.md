# Context7 Skill Wizard Reference

This file is the command source of truth for Context7 CLI skill-management asks.

## Core command group

```bash
ctx7 skills <subcommand> [options]
```

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
- `--all` (for install-all or generate-for-all-ides behavior)

## Common command patterns

```bash
# generate a custom skill interactively
ctx7 skills generate

# generate for all detected IDE targets
ctx7 skills generate --all

# install all skills from a repository
ctx7 skills install /owner/repo --all

# install for specific targets
ctx7 skills install /owner/repo --cursor --claude

# list installed skills by target
ctx7 skills list --cursor
ctx7 skills list --claude
ctx7 skills list --universal
```

## Generate flow checklist

When users ask about "Skill Wizard" or `ctx7 skills generate`, ensure guidance covers:
1. Describe expertise target.
2. Select Context7 documentation sources.
3. Answer follow-up scope/constraint questions.
4. Review generated skill content before install.
5. Install to selected target directories.
6. Restart the agent if installed skills do not appear immediately.

## Verification commands

```bash
# verify generated/installed skills
ctx7 skills list
ctx7 skills list --cursor
ctx7 skills list --claude
```

## Sources
- Upstash docs: https://www.mintlify.com/upstash/context7/cli/skills
- Upstash announcement: https://upstash.com/blog/context7-skill-wizard
