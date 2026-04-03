---
schema_version: 1
---

# agent-skills Agent Guide

This repository is the canonical source of Codex skills, linked operator docs, and agent workflow instructions.

## Table of Contents
- [Mandatory workflow snippet](#mandatory-workflow-snippet)
- [Required essentials](#required-essentials)
- [Error Handling Protocol](#error-handling-protocol)
- [Reporting & Insights](#reporting--insights)
- [Startup workflow](#startup-workflow)
- [Communication](#communication)
- [Efficiency](#efficiency)
- [Browser/Playwright](#browserplaywright)
- [Instruction routing](#instruction-routing)
- [Documentation map](#documentation-map)
- [Git workflow](#git-workflow)
- [Learnings](#learnings)
- [References (informational)](#references-informational)
- [Agent-First Scaffold Contract](#agent-first-scaffold-contract-managed-by-codex)

## Mandatory workflow snippet

1. Explore project first, then invoke skill.
2. IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning for any React, Tauri, Apps-SDK-ui, Tailwind, Vite, Storybook + Chat Widget tasks.
3. Add a Table of Contents for docs.

## Required essentials

- Package manager: none at repository root (configuration-focused repo).
- Non-standard build/typecheck commands: none at repository root.
- Compatibility posture: canonical-only.
- Keep communication single-threaded by default.
- Keep root `AGENTS.md` minimal; put volatile or category-specific policy in `docs/agents/*.md`.

## Error Handling Protocol

- When encountering API errors, model access issues, or unexpected failures, do not stop at reporting the error; always suggest a concrete workaround or alternative path that still advances the user's goal.

## Reporting & Insights

- For any report or insights generation task, verify required services and model access before starting.
- If required services or model access are unavailable, fall back to generating the report from local data using available tools such as Read, Bash, Glob, and Grep.

## Startup workflow

1. Run `bash scripts/codex-preflight.sh --stack auto --mode required` before multi-step, destructive, or path-sensitive work.
2. Read [docs/agents/README.md](docs/agents/README.md), then open only the task-relevant linked doc.
3. Run the narrowest proof first after edits, then broader checks from [docs/agents/04-validation.md](docs/agents/04-validation.md) before handoff.
4. If validation surfaces durable repo work rather than a one-off note, create or update a Linear issue in the `agent-skills` project instead of leaving the finding only in chat.

## Communication

- When the user explicitly states a root cause, confirm that understanding and proceed with their direction instead of proposing alternative fixes.

## Efficiency

- Before implementing multi-file edits or complex automation for a simple information request, pause and ask: `Would a direct answer or simple command suffice?`

## Browser/Playwright

- When browser tooling cannot access local files directly, immediately start `python3 -m http.server` in the relevant directory instead of cycling through fragile workarounds or abandoning the browser approach.

## Instruction routing

1. `/Users/jamiecraik/.codex/AGENTS.md`
2. Repository `AGENTS.md` (this file)
3. `/Users/jamiecraik/dev/Agent-Skills/docs/agents/README.md`
4. Linked docs under `docs/agents/`
5. If instructions conflict, pause and ask which one wins.

## Documentation map

- Use [docs/agents/README.md](docs/agents/README.md) as the front door for detailed policy.
- Use [docs/agents/02-tooling-policy.md](docs/agents/02-tooling-policy.md) for command style, preflight flags, and verified package roots.
- Use [docs/agents/03-local-memory.md](docs/agents/03-local-memory.md) for Local Memory workflow and session conventions.
- Use [docs/agents/04-validation.md](docs/agents/04-validation.md) for validation order and repo checks.
- Use [docs/agents/05-contradictions-and-cleanup.md](docs/agents/05-contradictions-and-cleanup.md) for live cleanup notes and resolved conflicts.
- Use [docs/agents/06-security-and-governance.md](docs/agents/06-security-and-governance.md) for MCP, auth, and disclosure guidance.
- Use [docs/agents/08-release-and-change-control.md](docs/agents/08-release-and-change-control.md) for risky git or release workflows.

## Git workflow

- For rebase of 5+ commits, merge-conflict workflows, or force-pushes, pause and present:
  1. Current branch state.
  2. Proposed strategy and risks.
  3. Alternative approaches.
  4. User confirmation before proceeding.
- Never assume there are no conflicts without verification.
- Re-check PR comments and checks before reporting completion.

## Learnings

- Read `~/.codex/instructions/Learnings.md` at session start.
- After bugs/tool failures/extra-effort fixes, append concise entries using:
  - `**YYYY-MM-DD [Codex]:** <problem> -> <fix>`

## References (informational)

- Global protocol: `/Users/jamiecraik/.codex/AGENTS.md`
- Security baseline: `/Users/jamiecraik/.codex/instructions/standards.md`
- RVCP source of truth: `/Users/jamiecraik/.codex/instructions/rvcp-common.md`
- Repository overview: `/Users/jamiecraik/dev/Agent-Skills/README.md`

<!-- AGENT-FIRST-SCAFFOLD:START -->
## Agent-First Scaffold Contract (managed by ~/.codex)

This repository participates in Jamie's global agent-first scaffold program.

Required global references:
- `~/.codex/instructions/openai-agent-workflow-playbook.md`
- `~/.codex/instructions/README.checklist.md`
- `~/.codex/instructions/validator-contracts.md`
- `~/.codex/instructions/strict-toggle-governance.md`
- `~/.codex/instructions/agent-first-scaffold-spec.md`

Repo-level requirements:
- Maintain `.agent/PLANS.md` using `tasks / id / depends_on` contract.
- Validate plan files with:
  `python3 ~/.codex/scripts/plan-graph-lint.py <plan-file>`
- Run canonical verification:
  `bash scripts/verify-work.sh`

State model: `S0 -> S1 -> S2 -> S3 -> S4 -> S5` with rollback to `Sx` on critical governance events.
<!-- AGENT-FIRST-SCAFFOLD:END -->
