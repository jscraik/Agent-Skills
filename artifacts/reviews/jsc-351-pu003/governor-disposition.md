# Governor Disposition: JSC-351 PU-003

## Slice

T012 / PU-003: deterministic doctor schema and runtime failure JSON for JSC-352.

## Review Inputs

- artifacts/reviews/jsc-351-pu003/architecture.md
- artifacts/reviews/jsc-351-pu003/testing.md
- artifacts/reviews/jsc-351-pu003/simplify-docs.md
- artifacts/reviews/jsc-351-pu003/architecture-rereview.md
- artifacts/reviews/jsc-351-pu003/testing-rereview.md
- artifacts/reviews/jsc-351-pu003/simplify-docs-rereview.md

## Findings Disposition

| Finding | Severity | Disposition | Evidence |
|---|---:|---|---|
| Missing end-to-end public CLI regression for invalid `--runtime-target` JSON payload | medium | fixed_immediately | `Infrastructure/tests/test_ask_skills_doctor.py` now invokes `Infrastructure/bin/ask skills proof autofix --runtime-target cloud --json --robot` through subprocess and asserts exit code plus `data.runtime_failure` contract fields. |
| Unused `_skill_doctor_next_command` wrapper | medium | fixed_immediately | Wrapper removed; tests assert `_skill_doctor_next_command_decision(...)["command"]` directly. |
| Future-tense implementation-note wording | low | fixed_immediately | T012 notes now describe implemented evidence in present/past-tense implementation language. |
| `next_command_decision.additionalProperties=true` | low | accepted_compatibility_risk | Kept for additive JSON compatibility in the v1 experimental schema; no blocker/high/medium risk remains for PU-003. |

## Validation Evidence

- `python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q` -> pass, 15 tests and 15 subtests.
- `./bin/ask skills proof autofix --runtime-target cloud --json --robot` -> expected validation failure, exit 2, includes `data.runtime_failure.schema_version=skill-runtime-failure.v1`.
- `./bin/ask skills doctor autofix --codex-parity --json --robot` -> expected validation failure, exit 2, includes `checks.runtime_reachability.runtime_failure` and blocker-precedence `next_command_decision`.
- `./bin/ask repo doctor --json --robot` -> pass, no blockers; diagnostic repo-surface debt remains advisory.
- `python3 Skills/agent-ops/goal-governor/scripts/check_goal_board.py docs/goals/jsc-351-agent-skills-codex-abi-conformance` -> pass.

## Governor Decision

No unresolved blocker, high, or medium findings remain. PU-003 is safe to close after tracker update, receipt append, and goal-board validation.

WROTE: artifacts/reviews/jsc-351-pu003/governor-disposition.md
