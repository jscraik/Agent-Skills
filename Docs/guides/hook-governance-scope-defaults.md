# Hook Governance Scope Defaults

## Table of Contents

- [Intent](#intent)
- [Agent Mutation Default](#agent-mutation-default)
- [Changes Implemented (2026-04-11)](#changes-implemented-2026-04-11)
- [Scope Policy By Script](#scope-policy-by-script)
- [Required Invocation Pattern](#required-invocation-pattern)
- [Rollout Checklist For Other Projects](#rollout-checklist-for-other-projects)
- [Why This Matters](#why-this-matters)

## Intent

This document defines how governance-oriented commands in this repository should scope mutations and validation outputs.

- Local developer workflows default to project-local scope (exception: `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh` defaults to workspace scope unless `--project-local` is specified).
- Workspace or home projection updates remain available as an explicit mode.
- Standalone scripts should require explicit inputs where scope affects data sources or output destinations.

## Agent Mutation Default

These defaults are mandatory when an agent is asked to implement changes in this repository:

1. The agent applies code and config mutations in this local project by default.
2. Workspace-level or home-level projection mutation is opt-in only and must be explicitly requested (for example via `--workspace-governance` on `verify-work.sh`).
3. If no target project path is clear, the agent must stop and ask for the exact local project root instead of mutating shared workspace artifacts.
4. In project-local mode, generated validation outputs must be ephemeral or local to this project and must not overwrite shared tracked artifacts.
5. When docs and execution scope diverge, the executable project-local contract (`Infrastructure/scripts/validation-and-linting/verify-work.sh` plus explicit script inputs) takes precedence.

## Changes Implemented (2026-04-11)

1. `Infrastructure/scripts/validation-and-linting/verify-work.sh`
- Default governance scope is `project-local`.
- `--project-governance` keeps project-local checks.
- `--workspace-governance` enables explicit workspace scope.
- Project-local mode forces ephemeral validation artifacts.
- Workspace mode forces persistent validation artifacts.

2. `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh`
- Added explicit scope flags: `--project-local` and `--workspace`.
- Default behavior remains workspace-capable for direct invocation. Note: Unlike the project-local default stated above, `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh` intentionally defaults to workspace scope unless `--project-local` is explicitly passed.
- `--project-local` keeps sync mutations inside the repository and skips home runtime projections.

3. Standalone hook-governance scripts in this repository
- No standalone `Infrastructure/scripts/hook-governance/rollout_check.py` or `Infrastructure/scripts/hook-governance/evaluate_docstring_ratchet.py` currently exist in this repo.
- If introduced later, they must require explicit scope-bearing inputs (for example `--inventory`, `--classification`, `--metrics`) and must not silently fall back to shared workspace artifacts.

## Scope Policy By Script

1. Workspace-by-design scripts:
- `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh --workspace`
- Any future governance scripts that intentionally aggregate across repositories

2. Scope-inherited scripts (recommended to stay input-driven):
- `Infrastructure/scripts/validate_all.sh` (artifact mode selected by caller)
- Future governance analyzers that read inventory/classification/metrics artifacts

3. Entry-point behavior:
- `Infrastructure/scripts/validation-and-linting/verify-work.sh` stays project-local by default.
- Workspace mutation is explicit via `--workspace-governance`.

## Required Invocation Pattern

For project-local validation via wrapper:

```bash
bash Infrastructure/scripts/validation-and-linting/verify-work.sh
```

For explicit workspace governance:

```bash
bash Infrastructure/scripts/validation-and-linting/verify-work.sh --workspace-governance
```

For direct validation runner invocation:

```bash
bash Infrastructure/scripts/validate_all.sh --ephemeral   # project-local
bash Infrastructure/scripts/validate_all.sh --persistent  # workspace/reporting lane
```

For direct sync invocation:

```bash
bash Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh --project-local
bash Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh --workspace
```

## Rollout Checklist For Other Projects

1. Update the local `verify-work` equivalent to default to project-local governance.
2. Add an explicit workspace flag for full governed-estate checks.
3. Remove implicit workspace defaults from standalone governance scripts.
4. Require explicit `--manifest` or `--inventory` style arguments where scope matters.
5. Ensure project-local mode writes temporary outputs, not shared tracked reports.
6. Add a short scope-policy markdown in each repo so the default is discoverable.
7. Validate both paths:
- project-local run passes when unrelated repos are stale.
- workspace run fails when governed workspace artifacts are stale.

## Why This Matters

Project-local defaults prevent unrelated workspace drift from blocking normal feature work.
Workspace mode preserves governance visibility for broader audits and periodic cross-repo checks.