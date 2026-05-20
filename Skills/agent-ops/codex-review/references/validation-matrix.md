# Codex Review Validation Matrix

## Backup And Baseline

Before major refactors, create a backup copy outside the canonical skill path and run helper syntax plus dry-run checks against both backup and live skill.

## Helper Edits

Run:

```bash
bash -n Skills/agent-ops/codex-review/scripts/codex-review
bash Skills/agent-ops/codex-review/scripts/codex-review --help
bash Skills/agent-ops/codex-review/scripts/codex-review --mode commit --commit HEAD --dry-run
CODEX_REVIEW_YOLO=0 bash Skills/agent-ops/codex-review/scripts/codex-review --mode commit --commit HEAD --dry-run
bash Skills/agent-ops/codex-review/scripts/codex-review --mode commit --commit HEAD --no-yolo --dry-run
```

For output-classification edits, use a fixture or direct helper path that proves untagged `Findings:` output does not get marked clean.

## Skill Or Reference Edits

Run:

```bash
./bin/ask skills audit Skills/agent-ops/codex-review --level strict --json --robot
./bin/ask evals run Skills/agent-ops/codex-review --mode smoke --runner discovery-smoke --skip-tessl --json --robot --no-dashboard
python3 Infrastructure/bin/ask skills external-review Skills/agent-ops/codex-review --audit-level compat --json
```

## Failure Classification

Classify every failed gate as one of:

- introduced by current patch
- pre-existing
- unrelated dirty worktree
- environment or tooling failure
- blocked on user input or permission
