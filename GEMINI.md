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

## TypeScript Configuration

TypeScript strict mode is enabled where applicable; ensure null/undefined checks are present before property access.

Run `pnpm typecheck` after significant TypeScript changes (or repo-native equivalent).

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
