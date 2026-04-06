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
