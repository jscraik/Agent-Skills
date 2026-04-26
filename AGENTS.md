---
schema_version: 1
---

# agent-skills Agent Guide

Canonical source of Codex skills, operator docs, and agent workflows.

## Table of Contents

- [Quick Start](#quick-start)
- [Unified Interface](#unified-interface-ask)
- [Shared Vocabulary](#shared-vocabulary)
- [Robot Mode](#robot-mode)
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

./bin/ask repo status          # Check repo health
./bin/ask skills list          # List available skills
./bin/ask skills audit <path>  # Audit before editing
```

## Unified Interface: `ask`

All agents MUST use `bin/ask` for repo operations.

| Task | Command |
|------|---------|
| Repo health | `./bin/ask repo status` |
| Full validation | `./bin/ask repo validate` |
| List skills | `./bin/ask skills list --category <topic>` |
| Audit skill | `./bin/ask skills audit <path> --level strict` |
| Install skill | `./bin/ask skills install <url> --remediate` |
| Find related | `./bin/ask graph related <skill> --depth 2` |

`bin/` and `scripts/` at repo root are stable wrapper entrypoints that forward into `Infrastructure/**`; keep them as real files/directories, not symlinks. `bin/ask` is the public wrapper and forwards to `Infrastructure/bin/ask`.

## Shared Vocabulary

Before changing skills, sync policy, runtime projections, or agent-facing docs, read [UBIQUITOUS_LANGUAGE.md](./UBIQUITOUS_LANGUAGE.md). Use its Prompt Translations table for terse, ambiguous, overloaded, or project-specific user wording.

## Robot Mode

Use `--robot` (or `--agent-mode`, `-r`) for AI-agent command handling.

Behavior contract:
- If intent is clear, `ask` executes the command even with minor syntax mistakes and prints a correction note.
- If intent is ambiguous, `ask` returns a detailed error that explains what failed, suggests likely fixes, and includes relevant valid examples.

**Examples (intent recovered):**
- `./bin/ask skill list --robot` -> runs as `./bin/ask skills list`
- `./bin/ask list skills --robot` -> runs as `./bin/ask skills list`
- `./bin/ask skills --advanced list --robot` -> runs as `./bin/ask skills list --advanced`

**Examples (needs clarification):**
- `./bin/ask status --robot` -> error explains ambiguity (`repo status` vs `plugins status`) with concrete examples.
- `./bin/ask skills audit --robot` -> error explains missing args and shows correct `skills audit` forms.

## Testing

For shared testing workflow guidance, see [Workflow and Safety Guidance](./Docs/agents/13-workflow-and-safety-guidance.md#testing).

When changing executable behavior, run the smallest real code path that exercises the exact production code touched before claiming the work is complete. If no existing test or command covers it, create a temporary reproduction under `/codex-scripts/` and keep that directory gitignored.

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
./bin/ask skills install <url> --remediate   # Scaffold missing files
./bin/ask skills audit <path> --level strict  # Mandatory hardening
```

**Folding strategy:** If `./bin/ask skills fold source target` returns confidence >= 0.2, fold rather than duplicate.

**Line budget:** Keep `SKILL.md` body ≤ 360 lines (see `Docs/agents/02-tooling-policy.md`). Move bulk content to `Infrastructure/references/<topic>.md`.

## Browser/Playwright

When browser cannot access local files:
```bash
python3 -m http.server  # in relevant directory
```

## See Also

- `./bin/ask --help` - Full CLI reference

---

*Entry: `./bin/ask` | Implementation: `Infrastructure/scripts/lib/ask/` | Specs: `Docs/cli-specs/`*
