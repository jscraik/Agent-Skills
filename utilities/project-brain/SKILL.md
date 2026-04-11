---
name: project-brain
description: Bootstrap and operate Project Brain correctly using the canonical instruction and bootstrap script.
metadata:
  short-description: Bootstrap and operate Project Brain
---

# Project Brain

## Table of Contents
- [When to Use](#when-to-use)
- [Inputs](#inputs)
- [Workflow](#workflow)
- [Guardrails](#guardrails)
- [Outputs](#outputs)
- [References](#references)

## When to Use
Use this skill when work involves:
- Bootstrapping Project Brain in a repository that does not yet have `.harness/`
- Explaining day-to-day Project Brain operation for Codex sessions
- Repairing or rerunning Project Brain initialization without inventing commands
- Routing repo-specific learnings, domain facts, decisions, and quality checks into the correct files

Do not use this skill for:
- Generic Local Memory setup that does not involve Project Brain files
- Ad hoc note systems that do not follow the canonical Project Brain instruction and bootstrap script
- Replacing the canonical bootstrap script with copied local variants

## Inputs
Collect these inputs before acting:
- Target repository root
- Whether `.harness/` already exists
- Desired initial domains, if any
- Whether the user wants indexing attempted after bootstrap

Canonical sources for this skill:
- `/Users/jamiecraik/dev/configs/codex/instructions/project-brain.md`
- `/Users/jamiecraik/dev/configs/codex/scripts/init-project-brain.sh`

If either source is missing, stop and ask the user where the Project Brain control plane is installed.

## Workflow
1. Inspect the repository root and confirm whether `.harness/` already exists.
2. Read the canonical instruction and bootstrap script before suggesting or running commands.
3. If setup is requested and `.harness/` is missing, run:
   `bash /Users/jamiecraik/dev/configs/codex/scripts/init-project-brain.sh [--domains ...] [--index]`
4. Use `--domains` only when the user requests specific domains. Otherwise use script defaults (`api,ui`).
5. Never source the bootstrap script and never swap `bash` for `sh`. The script is CLI-only.
6. If `.harness/` exists, do not overwrite by default. Use `--force` only when the user explicitly requests rebuild and prior state has been reviewed or backed up.
7. After bootstrap, direct users to fill:
   - `.harness/knowledge/INDEX.md` domain focus
   - `.harness/quality/criteria.md` project checks
   - `.harness/memory/LEARNINGS.md` first repo-specific learning
8. For ongoing operation, follow [Operating Routine](./references/operating-routine.md).
9. In handoff, report what initialized, what skipped, and whether indexing was attempted, skipped, or warned.

## Guardrails
- Treat `.harness/memory/LEARNINGS.md` as repo-specific and `~/.codex/instructions/Learnings.md` as cross-repo.
- Put confirmed facts in `knowledge.md`, unconfirmed theories in `hypotheses.md`, promoted patterns in `rules.md`, and significant choices in `decisions/YYYY-MM-DD-{topic}.md`.
- Read existing Project Brain files before writing new entries.
- Do not claim indexing will succeed. `--index` is best-effort and may skip when local-memory/index hooks are unavailable.
- Do not add custom bootstrap commands unless backed by canonical sources above.

## Outputs
Produce:
- The exact bootstrap command used or recommended
- A short summary of resulting `.harness/` layout
- Next Project Brain files the user should populate
- Blockers such as existing `.harness/`, missing canonical sources, or skipped indexing

## References
- [Setup and Bootstrap](./references/setup-and-bootstrap.md)
- [Operating Routine](./references/operating-routine.md)
