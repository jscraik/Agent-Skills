---
schema_version: 1
---

# Gemini Context

Always-on context for Gemini/Antigravity AI tooling.

For repository-wide rules, see [AGENTS.md](./AGENTS.md).

## Table of Contents

- [Gemini-Specific Notes](#gemini-specific-notes)
- [MCP Configuration](#mcp-configuration)
- [Shell Script Portability](#shell-script-portability)
- [TypeScript Configuration](#typescript-configuration)
- [TypeScript Development](#typescript-development)
- [Testing](#testing)
- [Git Workflow](#git-workflow)
- [Configuration Files](#configuration-files)
- [Code Review Fixes](#code-review-fixes)
- [Documentation](#documentation)
- [Examples](#examples)

## Gemini-Specific Notes

### Skill Install Failures

If skill-installer fails, follow the **Skill Management Protocol** in [AGENTS.md](./AGENTS.md): mandatory `skill-builder` pass after manual import.

## MCP Configuration

Keep MCP configuration explicit for both Codex and Claude automation.

Register with explicit argument separation:
```bash
claude mcp add <name> -- <command>
```

For 1Password: use `[ -e ]` instead of `[ -f ]` for named-pipe checks.

## Shell Script Portability

Prefer `[ -e "..." ]` over `[ -f "..." ]` for existence checks to support named pipes and special files.
When modifying shell scripts or configuration files, always use non-interactive command patterns. Avoid commands that require user input (like `op read` from 1Password) - they hang in CI/CD and headless environments.

## TypeScript Configuration

TypeScript strict mode is enabled where applicable; ensure null/undefined checks are present before property access.

Run `pnpm typecheck` after significant TypeScript changes (or repo-native equivalent).

## TypeScript Development

When refactoring interfaces that affect multiple files, first update the interface/type definitions, then systematically update all consumers before running tests. Verify no 'conflated' concerns exist (e.g., subcommand vs. mode flags).

## Testing

After fixing any code, always run the relevant test suite to verify the fix works before committing. If tests fail, debug and iterate rather than committing broken code.

## Git Workflow

When working with git branches, prefer merge over rebase for complex histories (>50 commits). Always run `git status` and resolve conflicts systematically before proceeding with changes.
For git operations like cherry-picking or branch syncing, prefer direct file restoration (`git checkout source_branch -- path/to/file`) over complex cherry-pick workflows when only specific files are needed.

## Configuration Files

For YAML schema changes and configuration files, validate against the schema immediately after editing. Do not assume syntax is correct without verification.

## Code Review Fixes

When fixing CodeRabbit or automated review comments, batch related fixes by file type and verify each category (types, security, validation, linting) before moving to the next.

## Documentation

Always format markdown plan files cleanly before writing - avoid stray backticks, inconsistent heading levels, or mixed quote styles. Use `prettier --write` or equivalent for markdown files.

## Examples

**Check repo health:**
```bash
ask repo status
ask skills list
```

**Audit a skill:**
```bash
ask skills audit backend/cli-spec --level strict
```

---

See [AGENTS.md](./AGENTS.md) for common rules and full quick-start.
