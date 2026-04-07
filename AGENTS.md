---
schema_version: 1
---

# agent-skills Agent Guide

Canonical source of Codex skills, operator docs, and agent workflows.

## Table of Contents

- [Quick Start](#quick-start)
- [Unified Interface](#unified-interface-ask)
- [Robot Mode](#robot-mode)
- [Agent-Specific Guidance](#agent-specific-guidance)
- [Testing](#testing)
- [Shell Scripting](#shell-scripting)
- [Git Workflow](#git-workflow)
- [Configuration Files](#configuration-files)
- [Code Review Fixes](#code-review-fixes)
- [Refactoring](#refactoring)
- [Documentation](#documentation)
- [Browser/Playwright](#browserplaywright)
- [Skill Management](#skill-management)
- [See Also](#see-also)

## Quick Start

```bash
ask repo status          # Check repo health
ask skills list          # List available skills
ask skills audit <path>  # Audit before editing
```

## Unified Interface: `ask`

All agents (Gemini, Codex, Claude) MUST use `bin/ask` for repo operations.

| Task | Command |
|------|---------|
| Repo health | `ask repo status` |
| Full validation | `ask repo validate` |
| List skills | `ask skills list --category <topic>` |
| Audit skill | `ask skills audit <path> --level strict` |
| Install skill | `ask skills install <url> --remediate` |
| Find related | `ask graph related <skill> --depth 2` |

## Robot Mode

The CLI is designed for AI agents. Use `--robot` (or `--agent-mode`, `-r`) for fuzzy command matching.

**Examples:**
- `ask skill list` → corrected to `ask skills list`
- `ask graph search X` → corrected to `ask graph find X`
- `ask skills ls` → corrected to `ask skills list`

When intent is clear but syntax is off, the CLI honors your command and shows correct syntax for next time.

## Agent-Specific Guidance

| File | Purpose |
|------|---------|
| [CLAUDE.md](./CLAUDE.md) | Claude Code specific (AI artifacts, PR workflow) |
| [GEMINI.md](./GEMINI.md) | Gemini/Antigravity notes |

## Testing

After fixing any code, always run the relevant test suite to verify the fix works before committing. If tests fail, debug and iterate rather than committing broken code.

## Shell Scripting

When modifying shell scripts or configuration files, always use non-interactive command patterns. Avoid commands that require user input (like `op read` from 1Password) - they hang in CI/CD and headless environments.

## Git Workflow

When working with git branches, prefer merge over rebase for complex histories (>50 commits). Always run `git status` and resolve conflicts systematically before proceeding with changes.
For git operations like cherry-picking or branch syncing, prefer direct file restoration (`git checkout source_branch -- path/to/file`) over complex cherry-pick workflows when only specific files are needed.

## Configuration Files

For YAML schema changes and configuration files, validate against the schema immediately after editing. Do not assume syntax is correct without verification.

## Code Review Fixes

When fixing CodeRabbit or automated review comments, batch related fixes by file type and verify each category (types, security, validation, linting) before moving to the next category.

## Refactoring

When refactoring interfaces that affect multiple files, first update the interface/type definitions, then systematically update all consumers before running tests. Verify no 'conflated' concerns exist (e.g., subcommand vs. mode flags).

## Documentation

Always format markdown plan files cleanly before writing - avoid stray backticks, inconsistent heading levels, or mixed quote styles. Use `prettier --write` or equivalent for markdown files.

## Skill Management

**Install failure recovery:**
```bash
ask skills install <url> --remediate   # Scaffold missing files
ask skills audit <path> --level strict  # Mandatory hardening
```

**Folding strategy:** If `ask skills fold source target` returns confidence ≥ 0.2, fold rather than duplicate.

**Line budget:** Keep `SKILL.md` body ≤ 360 lines (see `docs/agents/02-tooling-policy.md`). Move bulk content to `references/<topic>.md`.

## Browser/Playwright

When browser cannot access local files:
```bash
python3 -m http.server  # in relevant directory
```

## See Also

- [CLAUDE.md](./CLAUDE.md) - Claude-specific governance
- [GEMINI.md](./GEMINI.md) - Gemini-specific notes
- `bin/ask --help` - Full CLI reference

---

*Entry: `bin/ask` | Implementation: `scripts/lib/ask/` | Specs: `docs/cli-specs/`*
