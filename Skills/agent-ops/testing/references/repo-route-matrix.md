# Repo Route Matrix

Read when: selecting commands for a specific repo or language surface.

## General Selection Order

1. Read nearest AGENTS.md, repo README, contribution docs, and validation docs.
2. Prefer repo wrappers and documented command contracts.
3. Run the smallest exact behavior proof first.
4. Widen to codestyle, aggregate, deep, or CI-parity gates only when the change
   surface requires it.
5. Classify failures before assigning ownership.

## coding-harness

Common routes:

- bash scripts/validate-codestyle.sh --fast
- bash scripts/validate-codestyle.sh
- bash scripts/verify-work.sh --fast
- pnpm test
- pnpm test:deep when artifact or runtime behavior changes

Use harness assurance layers for agent workflow, artifact, closeout, and
governance changes.

Focused regression examples:

- `pnpm run test:related` for the repository-selected changed-file test lane.
- `pnpm run test:related -- --grep closeout-receipt` when the repository's
  current test runner supports that filter shape and the claim concerns
  closeout-receipt rejection.

Do not import these commands into another repository. Discover its package
scripts and supported filter syntax first.

## agent-skills

Common routes:

- bash scripts/bootstrap-ask.sh --json
- python3 bin/ask repo status --json
- ./bin/ask repo doctor --json --robot
- ./bin/ask skills audit <skill-path> --level strict --json --robot
- ./bin/ask evals run <skill-path> --mode smoke --json --robot
- ./bin/ask repo closeout --changed --json --robot
- bash Infrastructure/scripts/validation-and-linting/verify-work.sh

Use path ownership checks when source/projection boundaries are touched.

## evals

Common routes:

- pnpm evals run fixtures/smoke/pr-closeout.case.json --json
- pnpm evals check --json
- pnpm test

Use schema validation and artifact hash checks before trusting summaries.

## codex

For Rust work under codex-rs:

- run just fmt after Rust code edits;
- run the specific project test first, such as cargo test -p codex-tui;
- run broader cargo test or just test only when shared/common/core/protocol
  changes require it or the user approves the larger sweep;
- use just fix -p <project> before finalizing large Rust changes;
- be patient with Rust commands and do not kill them by PID.

When writing Rust tests, prefer comparing whole objects over checking fields one
by one when that better captures the contract.

## Report Template

schema_version: "1"
selected_route: "<repo/language/change-surface>"
exact_behavior_proof: "<command or blocked reason>"
validation_evidence:
  - command: "<exact command>"
    outcome: "pass|fail|blocked"
    note: "<short evidence>"
failure_ownership: "current_patch|pre_existing|unrelated_dirty_worktree|environment_tooling|missing_credential|expected_fixture_stderr|unknown|not_applicable"
remaining_risk: []
