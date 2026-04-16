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
- [Path Ownership](#path-ownership)
- [Code Review Fixes](#code-review-fixes)
- [Refactoring](#refactoring)
- [Documentation](#documentation)
- [Browser/Playwright](#browserplaywright)
- [Skill Management](#skill-management)
- [See Also](#see-also)

## Quick Start

```bash
# One-time per shell: load repo environment and add ask to PATH
source Infrastructure/scripts/codex_env_common.sh && codex_apply_env

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

For shared testing workflow guidance, see [Workflow and Safety Guidance](./Docs/agents/13-workflow-and-safety-guidance.md#testing).

## Shell Scripting

For shared shell scripting guidance, see [Workflow and Safety Guidance](./Docs/agents/13-workflow-and-safety-guidance.md#shell-scripting).

## Git Workflow

For shared git workflow guidance, see [Workflow and Safety Guidance](./Docs/agents/13-workflow-and-safety-guidance.md#git-workflow).

## Configuration Files

For shared configuration-file guidance, see [Workflow and Safety Guidance](./Docs/agents/13-workflow-and-safety-guidance.md#configuration-files).

## Path Ownership

For canonical source vs runtime/projection edit boundaries, see [Path Ownership Boundaries](./Docs/agents/14-path-ownership-boundaries.md).

## Code Review Fixes

For shared review-comment fix guidance, see [Workflow and Safety Guidance](./Docs/agents/13-workflow-and-safety-guidance.md#code-review-fixes).

## Refactoring

For shared refactoring guidance, see [Workflow and Safety Guidance](./Docs/agents/13-workflow-and-safety-guidance.md#refactoring).

## Documentation

For shared documentation guidance, see [Workflow and Safety Guidance](./Docs/agents/13-workflow-and-safety-guidance.md#documentation).

## Skill Management

**Install failure recovery:**
```bash
ask skills install <url> --remediate   # Scaffold missing files
ask skills audit <path> --level strict  # Mandatory hardening
```

**Folding strategy:** If `ask skills fold source target` returns confidence ≥ 0.2, fold rather than duplicate.

**Line budget:** Keep `SKILL.md` body ≤ 360 lines (see `Docs/agents/02-tooling-policy.md`). Move bulk content to `Infrastructure/references/<topic>.md`.

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

*Entry: `bin/ask` | Implementation: `Infrastructure/scripts/lib/ask/` | Specs: `Docs/cli-specs/`*
