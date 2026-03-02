# greptile skills

[Agent Skills](https://agentskills.io) for automated PR review workflows. Requires `git` + `gh` CLI.

## Table of Contents
- [Skills](#skills)
- [Greptile umbrella policy](#greptile-umbrella-policy)
- [How to setup](#how-to-setup)
- [Install](#install)
- [Usage](#usage)
- [License](#license)

## Skills

| Skill | Description |
|-------|-------------|
| [`check-pr`](check-pr/) | Policy-gated PR readiness audit (checks, unresolved threads, blockers, and governance compliance). |
| [`greploop`](greploop/) | Policy-gated bounded review/fix loop until target confidence and zero actionable feedback. |

## Greptile umbrella policy

Both skills run under the same organizational governance umbrella and must emit a runtime policy gate result on every execution.

- Setup and governance checklist: [`references/setup.md`](references/setup.md)
- Full policy framework: [`references/organizational-review-policy.md`](references/organizational-review-policy.md)

## How to setup

1. Authenticate GitHub CLI:

```bash
gh auth status
```

2. Configure Greptile MCP in your IDE/agent:
   - URL: `https://api.greptile.com/mcp`
   - Header: `Authorization: Bearer <GREPTILE_API_KEY>`

3. Verify MCP connectivity with `list_custom_context`.

4. Add repository-level `.greptile/` governance:
   - `config.json`
   - `rules.md`
   - `files.json` (required)

5. Review the full governance/setup guide:
   - [`references/setup.md`](references/setup.md)
   - [`references/organizational-review-policy.md`](references/organizational-review-policy.md)

## Install

```bash
git clone https://github.com/greptileai/skills.git ~/.claude/skills/greptile
cd ~/.claude/skills
ln -s greptile/check-pr check-pr
ln -s greptile/greploop greploop
```

Or as a submodule:

```bash
git submodule add https://github.com/greptileai/skills.git .skills/greptile
ln -s greptile/check-pr .skills/check-pr
ln -s greptile/greploop .skills/greploop
```

Claude Code discovers skills by looking for `SKILL.md` files at `~/.claude/skills/<skill-name>/SKILL.md`. Since this is a multi-skill repo, symlinks are needed to expose each sub-skill at the expected depth.

## Usage

Invoke by name in your agent (e.g. `/check-pr 123` or `/greploop`). If no PR number is given, both skills auto-detect the PR for the current branch.

## License

MIT
