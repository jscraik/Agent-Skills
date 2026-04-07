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
For shell scripts in shared workflows, see [AGENTS.md](./AGENTS.md). (When modifying shell scripts or configuration files, use non-interactive command patterns and avoid commands requiring user input such as `op read` from 1Password.)

## TypeScript Configuration

TypeScript strict mode is enabled where applicable; ensure null/undefined checks are present before property access.

Run `pnpm typecheck` after significant TypeScript changes (or repo-native equivalent).

## TypeScript Development

When refactoring interfaces that affect multiple files, first update the interface/type definitions, then systematically update all consumers before running tests. Verify no 'conflated' concerns exist (e.g., subcommand vs. mode flags).
For cross-file TypeScript refactoring in generated AGENTS guidance, see [workflow and safety guidance](/docs/agents/13-workflow-and-safety-guidance.md#refactoring).

## Testing

For testing guidance used across shared operational instructions, see [Workflow and Safety Guidance](/docs/agents/13-workflow-and-safety-guidance.md#testing).

## Git Workflow

When working with git branches, prefer to merge rather than rebase for complex histories (>50 commits). Always run `git status` and resolve conflicts systematically before proceeding with changes.
For git operations like cherry-picking or branch syncing, prefer repository-guided file restoration through `bin/ask` rather than raw git checkout commands when only specific files are needed.
For shared workflow references, see [AGENTS.md](./AGENTS.md).

## Configuration Files

For configuration guidance, see [Workflow and Safety Guidance](/docs/agents/13-workflow-and-safety-guidance.md#configuration-files) and [AGENTS.md](./AGENTS.md).

## Code Review Fixes

For shared review-comment handling, see [Workflow and Safety Guidance](/docs/agents/13-workflow-and-safety-guidance.md#code-review-fixes) and [AGENTS.md](./AGENTS.md).

## Documentation

For formatting and generated-document guidance, see [Workflow and Safety Guidance](/docs/agents/13-workflow-and-safety-guidance.md#documentation) and [AGENTS.md](./AGENTS.md).

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
