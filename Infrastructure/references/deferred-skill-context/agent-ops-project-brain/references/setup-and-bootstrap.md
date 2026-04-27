# Setup and Bootstrap

## Table of Contents
- [Purpose](#purpose)
- [Canonical Sources](#canonical-sources)
- [Preconditions](#preconditions)
- [Command Contract](#command-contract)
- [Bootstrap Flow](#bootstrap-flow)
- [Files Created](#files-created)
- [Reinitialization and Force](#reinitialization-and-force)
- [Indexing Behavior](#indexing-behavior)
- [Harness-Managed Rollout Depth](#harness-managed-rollout-depth)
- [Next Steps After Bootstrap](#next-steps-after-bootstrap)

## Purpose
Use this guide when the user wants Project Brain initialized in a repository or needs exact bootstrap commands and expected layout.

## Canonical Sources
- `<codex-control-plane>/instructions/project-brain.md`
- `<codex-control-plane>/Infrastructure/scripts/init-project-brain.sh`

If either file is missing, stop and ask for the installed Project Brain control-plane location.

## Preconditions
Before bootstrapping:
- Run from repository root
- Confirm whether `.harness/` already exists
- Confirm user wants Project Brain initialized in this repository
- Use `bash`, not `sh`
- Do not source the script

The bootstrap script enforces bash-only and CLI-only usage.

## Command Contract
Canonical invocations:

```bash
bash <codex-control-plane>/Infrastructure/scripts/init-project-brain.sh --help
bash <codex-control-plane>/Infrastructure/scripts/init-project-brain.sh
bash <codex-control-plane>/Infrastructure/scripts/init-project-brain.sh --domains api,auth,ui
bash <codex-control-plane>/Infrastructure/scripts/init-project-brain.sh --domains api,auth,ui --index
bash <codex-control-plane>/Infrastructure/scripts/init-project-brain.sh --domains api,auth,ui --force
```

Flags:
- `--domains`: comma-separated initial domain folders
- `--force`: overwrite existing files
- `--index`: best-effort local-memory sync

Script defaults:
- Domains: `api,ui`
- No overwrite unless `--force`
- No indexing unless `--index`

## Bootstrap Flow
1. Check whether `.harness/` already exists.
2. If missing, run canonical script with optional `--domains` and `--index` as requested.
3. If present, stop by default and explain that script errors unless `--force` is used.
4. Use `--force` only when user explicitly requests rebuild and prior state has been reviewed/backed up.

## Files Created
The script creates:

```text
.harness/
├── archive/
├── memory/
│   └── LEARNINGS.md
├── knowledge/
│   ├── INDEX.md
│   └── {domain}/
│       ├── knowledge.md
│       ├── hypotheses.md
│       └── rules.md
├── decisions/
│   └── .gitkeep
├── quality/
│   └── criteria.md
└── review-log.md
```

## Reinitialization and Force
Treat `--force` as destructive. Only use when:
- `.harness/` exists
- User explicitly requests reinitialization
- Current state has been reviewed or backed up

If users only need updates, edit existing Project Brain files instead of rerunning with `--force`.

## Indexing Behavior
`--index` is optional and best-effort.

Script behavior:
1. Creates files first
2. Checks `local-memory` on PATH or `LOCAL_MEMORY_URL`
3. Tries index hook with `python3` when available
4. Warns and continues when prerequisites are missing

Report indexing as `attempted`, `skipped`, or `warned` based on actual outcome.

## Harness-Managed Rollout Depth
Read when the repository enforces Project Brain through harness policy and tooling audit surfaces.

Per-repo checklist:
1. Confirm `Infrastructure/harness.contract.json` has the active memory contract keys (`memoryPolicy`, `memoryMaintenancePolicy`, `memoryEvalPolicy`).
2. Set `enabled=true` only when the repository should enforce Project Brain readiness.
3. Keep `requiredPaths` aligned with the repository `.harness/**` scaffold.
4. Re-run scaffold or update flow so `Infrastructure/scripts/check-environment.sh` includes both:
   - `project_brain_memory_extension_enabled=true`
   - `required_project_brain_paths=(...)`
5. Verify required Project Brain paths exist in the repository.
6. Run `./bin/ask repo validate --robot` and fix policy or readiness drift before enabling strict gates.

Validation lane for rollout changes:
1. Run the repository documented harness checks for policy and readiness drift.
2. Run the repository fast verification gate.
3. If the repository is coding-harness, use the concrete command lane from `${CODING_HARNESS_ROOT}/Docs/agents/20-project-brain-memory-extension-rollout.md` (set `CODING_HARNESS_ROOT` to your local coding-harness checkout).

Use this section as a conditional layer over bootstrap, not as a replacement for canonical Project Brain initialization.

## Next Steps After Bootstrap
1. Update `.harness/knowledge/INDEX.md` with domain focus
2. Update `.harness/quality/criteria.md` with project criteria
3. Add first repo-specific learning to `.harness/memory/LEARNINGS.md`
4. Continue with ongoing process in [operating-routine.md](./operating-routine.md)
