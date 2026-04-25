# Context Budget Rooted Soak Evidence

This artifact records the C3 rooted soak for the context-budgeted skill trees
plan.

- Branch: `develop`
- Commit: `22840fad87ad0d2e9e58830834e6fa98dd491b96`
- Recorded after commit: `7c54617641e296a9f7f4a169e20fb9bb83aa0333`
- Generated: `2026-04-25T08:06:22Z`
- Final projection mode: `rooted`
- Policy identity: `146a6f20347f3958`
- Full checksum manifest: `checksums.sha256`
- Checksum manifest SHA-256:
  `c0848187cf5e06e43f1762984ddc5ffd00dc7a482bd86f3c51fbd024b9dd977f`

## Five-Run Soak

The same command set passed five consecutive times on the same branch:

1. `python3 bin/ask skills budget --json`
2. `python3 bin/ask skills sync --scope workspace --projection rooted --dry-run`
3. `python3 bin/ask skills sync --scope workspace --projection rooted`
4. `python3 bin/ask skills sync --scope user --projection rooted --dry-run`
5. `python3 bin/ask skills sync --scope user --projection rooted`
6. `PYTHON_BIN=/Users/jamiecraik/.venvs/pyyaml/bin/python bash Infrastructure/scripts/validate_all.sh --ephemeral`
7. `python3 bin/ask skills sync --scope user --projection flat`
8. `python3 bin/ask skills sync --scope workspace --projection flat`
9. `python3 bin/ask skills sync --scope workspace --projection flat --dry-run`
10. `python3 bin/ask skills sync --scope user --projection flat --dry-run`
11. `python3 Infrastructure/scripts/validation-and-linting/check_context_budget.py --json`

Each run has one log file per step at `run-<n>-step-<n>.log`.

Validation summary from each run:

- `required_failures: 0`
- `warn_only_issues: 0`
- `check_context_budget.py --json`: `status: pass`

After the flat rollback checks, the rooted projection was restored with:

1. `python3 bin/ask skills sync --scope workspace --projection rooted`
2. `python3 bin/ask skills sync --scope user --projection rooted`

Restore logs:

- `final-workspace-rooted.log`
- `final-user-rooted.log`

Runtime surface artifacts covered by the restore:

- `.agents/skills`
- `.skillsets`

## Diagnostic Workouts

The three C1 diagnostic workouts passed under rooted projection and their
scorecards are retained in `scorecards/`.

| Workout | Attempts | Pass rate | Flake rate | Scorecard |
| --- | ---: | ---: | ---: | --- |
| `agent-ops/verification-before-completion` | 3 | 1.0 | 0 | `scorecards/agent-ops__verification-before-completion.json` |
| `harness-engineering/he-spec` | 3 | 1.0 | 0 | `scorecards/harness-engineering__he-spec.json` |
| `skill-factory/skill-refactor` | 3 | 1.0 | 0 | `scorecards/skill-factory__skill-refactor.json` |

Workout command evidence:

1. `python3 bin/ask workouts run agent-ops/verification-before-completion --attempts 3 --json`
2. `python3 bin/ask workouts run harness-engineering/he-spec --attempts 3 --json`
3. `python3 bin/ask workouts run skill-factory/skill-refactor --attempts 3 --json`

Telemetry snapshots:

- `runs.jsonl`
- `workout-results.jsonl`

## C3 Status

Satisfied by this artifact:

- Three rooted soak records exist.
- Soak records include timestamp, git SHA, projection mode, exact commands,
  validation result, runtime surface artifact paths, and report hashes.
- Three diagnostic workouts pass with scorecards.
- Five consecutive executions of the same validation command set pass on the
  same branch.
- Flat rollback remains documented and tested in the soak command set.

Remaining before C4 default flip:

- Confirm no P0/P1 routing regressions remain open against the current review
  tracker, if an external tracker is in use.
