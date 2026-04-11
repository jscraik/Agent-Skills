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
- [Next Steps After Bootstrap](#next-steps-after-bootstrap)

## Purpose
Use this guide when the user wants Project Brain initialized in a repository or needs exact bootstrap commands and expected layout.

## Canonical Sources
- `/Users/jamiecraik/dev/configs/codex/instructions/project-brain.md`
- `/Users/jamiecraik/dev/configs/codex/scripts/init-project-brain.sh`

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
bash /Users/jamiecraik/dev/configs/codex/scripts/init-project-brain.sh --help
bash /Users/jamiecraik/dev/configs/codex/scripts/init-project-brain.sh
bash /Users/jamiecraik/dev/configs/codex/scripts/init-project-brain.sh --domains api,auth,ui
bash /Users/jamiecraik/dev/configs/codex/scripts/init-project-brain.sh --domains api,auth,ui --index
bash /Users/jamiecraik/dev/configs/codex/scripts/init-project-brain.sh --domains api,auth,ui --force
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

## Next Steps After Bootstrap
1. Update `.harness/knowledge/INDEX.md` with domain focus
2. Update `.harness/quality/criteria.md` with project criteria
3. Add first repo-specific learning to `.harness/memory/LEARNINGS.md`
4. Continue with ongoing process in [operating-routine.md](./operating-routine.md)
