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
# Bash-first setup (recommended): open bash, then load repo environment
bash
source Infrastructure/scripts/codex-preflight/codex_env_common.sh && codex_apply_env

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

`bin/` and `scripts/` at repo root are stable wrapper entrypoints that forward into `Infrastructure/**`; keep them as real files/directories, not symlinks. `bin/ask` is the public wrapper and forwards to `Infrastructure/bin/ask`.

## Robot Mode

Use `--robot` (or `--agent-mode`, `-r`) for AI-agent command handling.

Behavior contract:
- If intent is clear, `ask` executes the command even with minor syntax mistakes and prints a correction note.
- If intent is ambiguous, `ask` returns a detailed error that explains what failed, suggests likely fixes, and includes relevant valid examples.

**Examples (intent recovered):**
- `ask skill list --robot` → runs as `ask skills list`
- `ask list skills --robot` → runs as `ask skills list`
- `ask skills --advanced list --robot` → runs as `ask skills list --advanced`

**Examples (needs clarification):**
- `ask status --robot` → error explains ambiguity (`repo status` vs `plugins status`) with concrete examples.
- `ask skills audit --robot` → error explains missing args and shows correct `skills audit` forms.

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
