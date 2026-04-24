# Testing Strategy Review: Context-Budgeted Skill Tree

## Findings

### 1) HIGH: Workout failure-path coverage is missing for the new verifier contract and subprocess execution
- Evidence:
  - `Infrastructure/scripts/lib/ask/commands/workouts.py:183-203` introduces critical failure modes (`tool_error`, `contract_violation`) based on `seed.sh`/`verify.py` exit codes and verifier hash drift.
  - `Infrastructure/scripts/lib/ask/commands/workouts.py:193-194` runs subprocesses with timeouts; timeout exceptions are part of runtime behavior.
  - `Infrastructure/tests/test_workouts_cli.py:34-47` validates only the happy path (`pass_rate == 1.0`, successful promote dry-run).
  - `Infrastructure/tests/test_workouts_cli.py:49-71` only checks that JSON output contains a `"scorecard"` key.
- Risk:
  - Regressions in the most important safeguard path (verifier mutation/failure detection) can ship without detection.
  - A timeout or failing verifier path can break CLI reliability without a test signal.
- Remediation:
  - Add targeted tests for:
    - seed failure (`seed_exit_code != 0`)
    - verifier failure (`verify_exit_code != 0`)
    - verifier mutation between pre/post hash (`failure_type == contract_violation`)
    - subprocess timeout handling (assert structured `CallResult` error instead of uncaught exception)

### 2) MEDIUM: Context-budget gate coverage does not exercise key negative-policy paths
- Evidence:
  - Budget policy includes routing/module constraints in `Infrastructure/GOVERNANCE/context-budget.yaml:6-17`.
  - Validator enforces only a subset in `Infrastructure/scripts/validation-and-linting/check_context_budget.py:198-239` (root/body counts, `max_candidates_returned`, rooted first-level exposure, manifest file/provenance checks).
  - Existing tests in `Infrastructure/tests/test_context_budgeted_skillsets.py:28-88` cover generation success, bounded candidates, and one unowned-file rejection, but do not cover policy toggles such as `forbid_full_manifest_output`, `forbid_unrelated_skillset_load`, module budget limits, or rooted missing-manifest failure branch.
- Risk:
  - Policy appears governed in config but can drift unvalidated in implementation/tests, reducing trust in “context budget gate” claims.
- Remediation:
  - Add failing/negative tests that explicitly prove enforcement (or intentionally document non-enforcement and remove unused knobs):
    - rooted mode with missing generated manifests -> expect `MANIFEST_FILES_MISSING`
    - router payload policy checks that map to `forbid_full_manifest_output` / unrelated skill-set load constraints
    - module budget/path checks (if intended contract)

### 3) MEDIUM: Shell projection tests verify rejection paths but not user-scope success behavior
- Evidence:
  - Shell script adds scope handling and projection mode plumbing in `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh:22-102` and user projection branch in `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh:1851-1861`.
  - Shell tests `Infrastructure/tests/test_sync_skills_shell_projection.py:22-40` cover rooted rejection and invalid scope ordering only.
- Risk:
  - Regressions in `--user` behavior (home projection updates) can pass CI undetected even though scope semantics changed and docs were updated.
- Remediation:
  - Add at least one integration-style shell test for `--user --projection flat` with isolated HOME/temporary dirs, asserting expected user-link actions and non-error exit.

## Residual Risk
- Runtime/budget/report surfaces are well-covered for contract-shape checks, but regression protection remains skewed toward happy paths. The highest unverified risk is workout failure behavior under real-world command failures/timeouts.

WROTE: artifacts/reviews/context_tree_testing_review_2.md
