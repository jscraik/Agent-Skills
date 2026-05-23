# Governor Remediation: PR #192 Head d55d915

## Status

blocked_pending_followup_push

## Runtime Truth

- PR #192 head inspected before this remediation: d55d9159cf49b290419ce0d4d3846b87711639e5.
- Live GraphQL review truth showed a new current unresolved thread at Infrastructure/scripts/lib/ask/commands/skills_impl.py:2947 asking that list-valued agents/openai.yaml dependencies parse as arrays.
- The finding is valid. The package contract parser still used the older fallback shape and would not preserve nested list-of-map metadata in the base CLI environment where PyYAML is not installed.

## Fix Applied

- Infrastructure/scripts/lib/ask/commands/skills_impl.py now tries yaml.safe_load when PyYAML is available and falls back to a deterministic parser that preserves scalar lists and simple nested list-of-map metadata such as dependencies.required_skills[] and dependencies.tools[].name.
- Infrastructure/scripts/lib/ask/services/codex_preview.py received the same fallback hardening so preview and package contract behavior do not diverge when PyYAML is absent.
- Infrastructure/tests/test_ask_skills_package_contract.py now asserts agents/openai.yaml dependency tools are emitted as an array of maps in the SkillPackage contract.

## Validation Evidence

| Command | Outcome | Evidence |
|---|---|---|
| uv run --python 3.12 --with pytest python -m pytest Infrastructure/tests/test_ask_skills_package_contract.py -q | pass | 9 passed without installing PyYAML. |
| uv run --python 3.12 --with pytest python -m pytest Infrastructure/tests/test_ask_skills_codex_preview.py -q | pass | 20 passed without installing PyYAML. |
| python3 Skills/agent-ops/goal-governor/scripts/check_goal_board.py Docs/goals/jsc-351-agent-skills-codex-abi-conformance | pass | Goal board is valid. |
| uv run --python 3.12 --with pytest python -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q | pass | 15 passed and 15 subtests passed. |
| /usr/bin/python3 -m py_compile Infrastructure/scripts/lib/ask/commands/skills_impl.py Infrastructure/scripts/lib/ask/services/codex_preview.py Infrastructure/tests/test_ask_skills_package_contract.py Infrastructure/tests/test_ask_skills_codex_preview.py | pass | Compilation succeeded. |
| ./bin/ask repo doctor --json --robot | pass | blocking=false; ask bootstrap and repo surface remain diagnostic debt only. |
| git diff --check HEAD | pass | No whitespace errors. |

## Governor Decision

Commit and push this follow-up remediation to PR #192. After push, refresh PR checks, review-thread state, mergeability, and Linear traceability before any PU-006 service extraction or next implementation slice.

WROTE: artifacts/reviews/jsc-351-pr192-triage-lane/governor-remediation-d55d915.md
