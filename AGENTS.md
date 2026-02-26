---
schema_version: 1
---

# agent-skills Agent Guide

This repository is the canonical source of Codex skills, docs, and agent workflow instructions.

## References (informational)
- Global protocol: ~/.codex/AGENTS.md
- Security and standards baseline: ~/.codex/instructions/standards.md
- RVCP source of truth: ~/.codex/instructions/rvcp-common.md

## Table of Contents
- [Required essentials](#required-essentials)
- [Package-manager command map](#package-manager-command-map)
- [Non-standard build/typecheck commands](#non-standard-buildtypecheck-commands)
- [Tooling essentials](#tooling-essentials)
- [Shell script conventions](#shell-script-conventions)
- [Global instructions discovery order](#global-instructions-discovery-order)
- [Documentation map](#documentation-map)
- [Planning](#planning)
- [Agent-First Scaffold Contract](#agent-first-scaffold-contract-managed-by-codex)

## Required essentials
- Project description: one sentence, above.
- Package manager: none for the repository root (configuration-only).
- Non-standard build/typecheck commands: none at repository root.
- Compatibility posture: canonical-only.

## Package-manager command map
- Root (configuration-only): install/run/exec are not observed at root.
- Use repository-verified root commands:
  - `bash scripts/sync_skills.sh`
  - `python3 scripts/docs_lint.py --mode warn --config docs-policy.json`
- Per directory, from lockfile evidence:
  - `github/automate-github-issues/` has `package-lock.json` (npm). Use:
    - install: `npm --prefix github/automate-github-issues install`
    - run: `npm --prefix github/automate-github-issues run <script>`
    - exec: `npm --prefix github/automate-github-issues exec <bin>`
  - `frontend/react-components/` has `package-lock.json` (npm). Use:
    - install: `npm --prefix frontend/react-components install`
    - run: `npm --prefix frontend/react-components run <script>`
    - exec: `npm --prefix frontend/react-components exec <bin>`
  - `utilities/video-transcript-downloader/` has `package-lock.json` (npm). Use:
    - install: `npm --prefix utilities/video-transcript-downloader install`
    - run: `npm --prefix utilities/video-transcript-downloader run <script>`
    - exec: `npm --prefix utilities/video-transcript-downloader exec <bin>`

## Non-standard build/typecheck commands
- This repository is configuration/content oriented; no root build or typecheck commands are defined here.
- In package-based subdirectories, use declared scripts (for example `typecheck`, `build`, or `test`) from that package’s own `package.json`.

## Tooling essentials
- Run shell commands with `zsh -lc` (fallback to `bash -lc` when `zsh` is unavailable).
- Prefer `rg`, `fd`, and `jq`.
- Read `~/.codex/instructions/tooling.md` before choosing tools.
- Use repository-verified paths from README, `docs/`, and scripts.
- Do not add dependencies or system settings without user approval.

## Shell Script Conventions
- Validate script syntax with `bash -n script.sh`.
- Run `shellcheck` on wrapper scripts when available in repo workflow.
- Keep shell scripts deterministic; avoid hidden environment assumptions.

## Global instructions discovery order
1. `~/.codex/AGENTS.md`
2. Repository root `AGENTS.md`
3. Linked instruction files (`README.md`, `.agent/PLANS.md`, `docs/agents/*.md`)
4. Ask before changing behavior when instructions conflict.

## Documentation map
### Table of Contents
- [01-instruction-map](docs/agents/01-instruction-map.md)
- [02-tooling-policy](docs/agents/02-tooling-policy.md)
- [03-local-memory](docs/agents/03-local-memory.md)
- [04-validation-and-checks](docs/agents/04-validation.md)
- [05-contradictions-and-cleanup](docs/agents/05-contradictions-and-cleanup.md)
- [06-security-and-governance](docs/agents/06-security-and-governance.md)
- [07a-role-governance](docs/agents/07a-role-governance.md)
- [07b-agent-governance](docs/agents/07b-agent-governance.md)
- [08-release-and-change-control](docs/agents/08-release-and-change-control.md)
- [09-audit-trail-policy](docs/agents/09-audit-trail-policy.md)
- [10-agent-testing-gates](docs/agents/10-agent-testing-gates.md)

## Planning
- For complex implementation work or architecture work, keep planning artifacts in `.agent/PLANS.md` with task `id`/`depends_on` checks.
- Validate plan files with `python3 ~/.codex/scripts/plan-graph-lint.py <plan-file>`.

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
