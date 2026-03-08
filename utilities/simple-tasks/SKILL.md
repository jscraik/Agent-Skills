---
name: simple-tasks
description: Install a fast local task workflow for single-project planning with scripts/task.sh (claim, done, status, reporting) backed by tasks/TASKS.md and optional tasks/details/ notes. Use when you need lightweight in-progress task coordination rather than full team issue tracking.
---

# Simple Tasks

## Table of Contents
- [When to use](#when-to-use)
- [Philosophy](#philosophy)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Procedure](#procedure)
- [Validation](#validation)
- [Constraints / Safety](#constraints--safety)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [Resources](#resources)

## When to use
Use this skill when you want:
- quick local task tracking in a single project repo;
- lightweight CLI task flow (`claim`, `done`, `next`, `summary`) without external issue tooling;
- canonical markdown backlog in `tasks/TASKS.md` with optional detail notes.

## Philosophy
- Keep task management local, fast, and explicit.
- Optimize for in-progress execution, not enterprise workflow complexity.
- Preserve a single source of truth for task state.

## Inputs
- `--project-dir PATH` (required)
- `--mode install|upgrade` (default `install`)
- Optional: `--dry-run`

## Outputs
- Installed `scripts/task.sh` command interface.
- Created/updated task files:
  - `tasks/TASKS.md`
  - `tasks/details/<id>.md` (optional per task)
- Query commands and filters for status reporting.

## Procedure
1. Confirm target project path.
2. Run dry-run if uncertain about existing task files.
3. Install or upgrade simple-tasks scripts.
4. Verify `scripts/task.sh` and `tasks/TASKS.md` exist.
5. Run a status or summary command to validate output.

Install command:

```bash
skills/simple-tasks/scripts/install.sh --project-dir /path/to/project
```

Supported task commands include:
- `claim`, `done`, `status`, `next`, `plan`, `finished`
- `upcoming`, `needs-planning`, `blocked`, `summary`, `learn`

Supported filters include:
- `--today`, `--last-24h`, `--last-week`, `--last-month`
- `--days`, `--mine`, `--agent`, `--limit`

## Validation
- Ensure installer exits successfully and creates expected files.
- Run `scripts/task.sh status` and `scripts/task.sh summary` at minimum.
- Confirm updates are reflected in `tasks/TASKS.md`.
- **Fail fast:** if install output is incomplete or task files are missing, stop and fix before use.

## Constraints / Safety
- Redact secrets, tokens, credentials, API keys, and PII in task notes and shared logs.
- Keep scope to local project task tracking; do not imply external ticket sync.
- Use `--dry-run` before upgrades in repos with custom task file conventions.

## Anti-patterns
- Using simple-tasks as a replacement for multi-team issue tracking systems.
- Spreading task state across multiple markdown files without canonical `tasks/TASKS.md`.
- Skipping validation commands after install.

## Examples
```bash
skills/simple-tasks/scripts/install.sh --project-dir /tmp/demo --dry-run
skills/simple-tasks/scripts/install.sh --project-dir /tmp/demo --mode upgrade
```

## Resources
- `references/contract.yaml`
- `references/evals.yaml`

<!-- decision-feedback-protocol:v2 -->
## Decision Quality Feedback
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: decision (accepted|partial|rejected|deferred), outcome (good|neutral|bad|unknown), and confidence (high|medium|low).
- Persist feedback with python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "...".
<!-- /decision-feedback-protocol -->
