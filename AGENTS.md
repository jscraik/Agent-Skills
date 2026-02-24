---
schema_version: 1
---

# agent-skills Agent Guide

This repository is the canonical source of Codex skills, docs, and agent workflow instructions.

## References (informational)
- Global protocol: ~/.codex/AGENTS.md
- Security and standards baseline: ~/.codex/instructions/standards.md
- RVCP source of truth: ~/.codex/instructions/rvcp-common.md

## Required essentials
- Project description: one sentence, above.
- Package manager: none (configuration-only repository root).
- Non-standard build/typecheck commands: none.
- Compatibility posture: canonical-only.

## Global instructions discovery order
1. `~/.codex/AGENTS.md`
2. Repository root `AGENTS.md`
3. Linked instruction files (`README.md`, `.agent/PLANS.md`, `docs/agents/*.md`)
4. Ask before changing behavior when instructions conflict.

## Tooling essentials
- Run shell commands with `zsh -lc`.
- Prefer `rg`, `fd`, and `jq`.
- Read `~/.codex/instructions/tooling.md` before choosing tools.
- Use repository-verified paths from README, `docs/`, and scripts.
- Do not add dependencies or system settings.

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
