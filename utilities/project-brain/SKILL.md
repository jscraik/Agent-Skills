---
name: project-brain
description: Bootstrap and operate Project Brain correctly using the canonical instruction and bootstrap script.
metadata:
  short-description: Bootstrap and operate Project Brain
  skill-type: runbook
---

# Project Brain

## Table of Contents
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Workflow](#workflow)
- [Harness-Managed Rollout Depth](#harness-managed-rollout-depth)
- [Guardrails](#guardrails)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Gotchas](#gotchas)
- [See Also](#see-also)
- [References](#references)

## When to use
Use this skill when work involves:
- Bootstrapping Project Brain in a repository that does not yet have `.harness/`
- Explaining day-to-day Project Brain operation for Codex sessions
- Repairing or rerunning Project Brain initialization without inventing commands
- Routing repo-specific learnings, domain facts, decisions, and quality checks into the correct files

Do not use this skill for:
- Generic Local Memory setup that does not involve Project Brain files
- Ad hoc note systems that do not follow the canonical Project Brain instruction and bootstrap script
- Replacing the canonical bootstrap script with copied local variants

## Required inputs
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
8. If the repository is harness-managed and enforces Project Brain via contract/tooling audit, apply the rollout lane in [Harness-Managed Rollout Depth](#harness-managed-rollout-depth) and [Setup and Bootstrap](./references/setup-and-bootstrap.md).
9. For ongoing operation, follow [Operating Routine](./references/operating-routine.md).
10. In handoff, report what initialized, what skipped, and whether indexing was attempted, skipped, or warned.

## Harness-Managed Rollout Depth
Read when the target repository enforces Project Brain using repo-local harness policy and readiness scripts, not bootstrap only.

- If the target repository has opted into Project Brain enforcement, verify `harness.contract.json` uses the active memory contract keys (`memoryPolicy`, `memoryMaintenancePolicy`, `memoryEvalPolicy`) with repo-accurate required paths.
- If the repo readiness scripts expose Project Brain gates, confirm those checks and required paths stay aligned before enabling strict enforcement.
- Keep policy and scaffold updates together; do not enable strict enforcement before both are aligned.
- Run `harness tooling-audit --path <repo-root>` before enabling strict gates so policy drift and readiness-script drift fail early.
- Validate with each repository's documented harness verification commands (at minimum `harness tooling-audit --path <repo-root>` plus the repository fast verify gate).
- For coding-harness specifically, run `bash scripts/verify-work.sh` (project-local scope) and `bash scripts/verify-work.sh --workspace-governance` (workspace scope).
- For gradual migration, land contract plus scaffold updates first, then turn on strict enforcement.

## Guardrails
- Treat `.harness/memory/LEARNINGS.md` as repo-specific and `~/.codex/instructions/Learnings.md` as cross-repo.
- Put confirmed facts in `knowledge.md`, unconfirmed theories in `hypotheses.md`, promoted patterns in `rules.md`, and significant choices in `decisions/YYYY-MM-DD-{topic}.md`.
- Read existing Project Brain files before writing new entries.
- Do not claim indexing will succeed. `--index` is best-effort and may skip when local-memory/index hooks are unavailable.
- Do not add custom bootstrap commands unless backed by canonical sources above.

## Deliverables
Produce:
- The exact bootstrap command used or recommended
- A short summary of resulting `.harness/` layout
- Next Project Brain files the user should populate
- Blockers such as existing `.harness/`, missing canonical sources, or skipped indexing

## Failure mode
- Missing canonical instruction/script sources: stop and ask for the installed control-plane path before proceeding.
- Existing `.harness/` with ambiguous rebuild intent: do not overwrite until the user confirms force/rebuild behavior.
- Harness policy mismatch (contract vs readiness scripts): treat as blocked until policy and scaffold checks are aligned.

## Gotchas
- `--index` is best-effort; report when indexing is skipped or unavailable instead of presenting it as guaranteed.
- `init-project-brain.sh` is CLI-only; do not source it and do not switch the shell interpreter from `bash`.
- Keep repository Project Brain memory files separate from cross-repo `~/.codex` memory files.

## See Also

| Skill | Why |
| --- | --- |
| [[coding-harness]] | Use when Project Brain rollout must align with harness contracts, gates, and tooling audits in a managed repository. |
| [[codex-home-audit]] | Pair when the user wants Codex control-plane drift analysis across agents, hooks, skills, and memory surfaces. |
| [[docs-expert]] | Use for follow-on documentation hardening after Project Brain bootstrap or rollout changes land. |

## References
- [Setup and Bootstrap](./references/setup-and-bootstrap.md)
- [Operating Routine](./references/operating-routine.md)
- `${CODING_HARNESS_ROOT}/docs/agents/20-project-brain-memory-extension-rollout.md` (set `CODING_HARNESS_ROOT` to your local coding-harness checkout when working in harness-managed repositories)
