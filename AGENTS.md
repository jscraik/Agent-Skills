---
schema_version: 1
---

# agent-skills Agent Guide

This repository is the canonical source of Codex skills, docs, and agent workflow instructions.

## Table of Contents
- [Mandatory workflow snippet](#mandatory-workflow-snippet)
- [Required essentials](#required-essentials)
- [Command preflight](#command-preflight)
- [Verification default](#verification-default)
- [Instruction routing](#instruction-routing)
- [Documentation map](#documentation-map)
- [Git workflow](#git-workflow)
- [External integrations](#external-integrations)
- [Communication and file operations](#communication-and-file-operations)
- [Learnings](#learnings)
- [References (informational)](#references-informational)
- [Agent-First Scaffold Contract](#agent-first-scaffold-contract-managed-by-codex)
- [Repository preflight helper](#repository-preflight-helper)

## Mandatory workflow snippet

1. Explore project first, then invoke skill.
2. IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning for any React, Tauri, Apps-SDK-ui, Tailwind, Vite, Storybook + Chat Widget tasks.
3. Add a Table of Contents for docs.

## Required essentials
- Package manager: none at repository root (configuration-focused repo).
- Non-standard build/typecheck commands: none at repository root.
- Compatibility posture: canonical-only.
- Keep communication single-threaded by default.

## Command preflight

- Run shell commands with `zsh -lc` (fallback to `bash -lc` only when `zsh` is unavailable or script internals require bash).
- Confirm `pwd` is `/Users/jamiecraik/dev/agent-skills` before edits.
- Confirm required binaries for the task (`rg`, `fd`, `jq`, plus repo-specific tools).
- Use `which` before any `mise` tooling installs.
- Confirm target paths exist before editing and visually verify paths with `fd` before destructive operations.
- Fail fast if a required check is missing.

## Verification default

- Prefer one-shot, auditable commands.
- Run focused validation after each edit batch and broader validation before finalizing.
- Default root checks:
  - `bash scripts/sync_skills.sh`
  - `python3 scripts/docs_lint.py --mode warn --config docs-policy.json`
  - `just validate` (or `bash scripts/validate_all.sh`) for full repo gates
- After config-sensitive changes (`package.json`, CI workflows, `settings.json`, related config files), run applicable validation and confirm passing status before commit.
- For implementation work, run separate implementation and verification workflows, then run `codex review --uncommitted` before merge.

## Instruction routing

1. `/Users/jamiecraik/.codex/AGENTS.md`
2. Repository `AGENTS.md` (this file)
3. `/Users/jamiecraik/dev/agent-skills/docs/agents/README.md`
4. Linked docs under `docs/agents/`
5. If instructions conflict, pause and ask which one wins.

## Documentation map

- Use [`docs/agents/README.md`](docs/agents/README.md) as the front door.
- Keep root guidance minimal and move deep policy into linked docs.
- Maintain contradiction tracking in [`docs/agents/05-contradictions-and-cleanup.md`](docs/agents/05-contradictions-and-cleanup.md).

## Git workflow

- For rebase of 5+ commits, merge-conflict workflows, or force-pushes, pause and present:
  1. Current branch state.
  2. Proposed strategy and risks.
  3. Alternative approaches.
  4. User confirmation before proceeding.
- Never assume there are no conflicts without verification.
- Re-check PR comments and checks before reporting completion.

## External integrations

- Run `codex mcp list` before MCP-dependent implementation.
- Before external API or MCP operations, run this preflight in order:
  1. Verify env vars resolve (not placeholders).
  2. Verify 1Password session (`op account list`).
  3. Run a simple connectivity check.
  4. Then proceed with full operations.
- If auth fails, debug the auth layer before retrying operations.

## Communication and file operations

- When the user names a tool or skill, verify it exists before choosing fallback behavior.
- Verify file paths against documentation before commit (for example `.diagram/`).

## Learnings

- Read `~/.codex/instructions/Learnings.md` at session start.
- After bugs/tool failures/extra-effort fixes, append concise entries using:
  - `**YYYY-MM-DD [Codex]:** <problem> -> <fix>`

## References (informational)

- Global protocol: `/Users/jamiecraik/.codex/AGENTS.md`
- Security baseline: `/Users/jamiecraik/.codex/instructions/standards.md`
- RVCP source of truth: `/Users/jamiecraik/.codex/instructions/rvcp-common.md`
- Repository overview: `/Users/jamiecraik/dev/agent-skills/README.md`

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
  `bash ~/.codex/scripts/verify-work.sh`

State model: `S0 -> S1 -> S2 -> S3 -> S4 -> S5` with rollback to `Sx` on critical governance events.
<!-- AGENT-FIRST-SCAFFOLD:END -->

## Repository preflight helper

- Use `scripts/codex-preflight.sh` before multi-step, destructive, or path-sensitive workflows.
- Run with bash internals:
  - `bash -lc "source /Users/jamiecraik/dev/agent-skills/scripts/codex-preflight.sh && preflight_repo"`
- If the script is unavailable, run the manual preflight checklist above.
